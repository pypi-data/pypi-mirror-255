from types import CoroutineType

from .tags import parse, RootTag, InvalidEntry, EmptyEntry
from .hooks import HookTrigger, Hook


# needs better API 
# - passing external variables into it (state managment)


class GeneralInterface:

    def __init__(self, renderer):
        self.renderer = renderer
        self.renderer.inject_trigger_resolver(self.execute_hook_func)
        self.renderer.inject_trigger_matcher(self.match_trigger_to_hook)

        self.root: RootTag = None

        self.input_hooks = []
        self.event_queue = []

        self.__suppress_update = False

    # generates a root by parsing the template form
    # and renders the template 
    async def construct(self, form: str, vars: dict={}):
        self.root = parse(form).inject_ui(self)

        if vars:
            self.root.update_state(**vars)

        await self.root.render()
        await self.renderer.construct(
            # only register listener if mode != "view"
            self.root, register_listener=vars.get("mode") != "view"
        )

    # not really sure where this is even used
    async def update(self):
        await self.root.render()
        await self.renderer.update(self.root)

    # api for registering input hooks from tags
    def register_hook(self, hook: Hook, func: CoroutineType):
        self.input_hooks.append((hook, func))

    # api for queueing events from tags
    def queue_event(self, event: CoroutineType):
        self.event_queue.append(event)

    # need to separate this from hook execution
    async def execute_events(self):
        while self.event_queue:
            event = self.event_queue.pop(0)
            try:
                # events which return True terminate event loop 
                # and suppress HookTrigger cleanup
                if await event(): return True
            # prevents report from being saved if required fields are empty;
            # not sure if here is the right place to handle this
            except EmptyEntry as entry_name:
                self.renderer.send_error(f"Field **'{entry_name}'** is required.")

    # prevents the template from visually updating during 
    # the update loop following the call of this method 
    #
    # rename to suppress_update pls
    def suppress_refresh(self):
        self.__suppress_update = True

    # checks if any of the input hooks matches the passed hook trigger
    # and schedules the hook function for execution if match
    def match_trigger_to_hook(self, trigger) -> bool:
        # goes through input_hooks backwards, this is to ensure 
        # entry hooks are handled correctly when changing entry mid render
        for hook, func in self.input_hooks[::-1]:
            
            # if hook matches, the match object gets set as an attribute of trigger
            if hook is None or hook.matches(trigger):
                # this could get dangerous, as func will begin execution
                # and might finish before it's awaited
                self.hook_func = func(trigger)
                return True

        return False

    # The way this currently works is input hooks and event queue get populated
    # during construction, however the first set of events is never executed
    # as the second render overrides them, leading to undesired behaviour
    async def execute_hook_func(self):

        # input_hooks and event_queue are purged and refilled here
        self.input_hooks = []

        if self.hook_func:
            try:
                await self.hook_func

            except InvalidEntry as error_message:
                # idk if this should be handled here
                self.renderer.send_error(error_message)

            self.hook_func = None
        
        # repopulates both input_hooks and event_queue
        await self.root.render()

        # events and empty input hooks can trigger deactivation of the template,
        # possibly leaving behind user input that only gets cleaned up after this method finishes,
        # this might be an issue when it comes to message commands later

        # some input hooks can be directly responsible for the executed events,
        # e.g. reaction triggering save/discard
        if await self.execute_events():
            # this is needed as events use it to signal
            # to the listener when an event terminates the template
            return True

        # deactivate interface if there are no input_hooks after rerender
        if not self.input_hooks:
            await self.renderer.deactivate()
            # suppresses HookTrigger cleanup
            return True

        if self.__suppress_update:
            self.__suppress_update = False
            return

        await self.renderer.update(self.root)
        
    
    # API FOR ROOT

    # deactivates the template without deleting it,
    # usually used after saving when done creating report
    def clean_up(self):
        async def __clean_up():
            await self.renderer.update(self.root)
            await self.renderer.deactivate()

            self.suppress_refresh()
            return True

        self.queue_event(__clean_up)

    # deletes and deactivates the template without saving
    def discard(self):
        async def __discard():
            await self.renderer.discard()
            self.suppress_refresh()

            return True

        self.queue_event(__discard)

    # replaces the current template with a new one
    # using the same renderer to display it
    def swap(self, form):
        async def __swap():
            self.root = parse(form).inject_ui(self)
            await self.root.render()

        self.queue_event(__swap)

    # moves the template to a new channel
    def forward(self, channel_id, mode=None):
        async def __forward():
            self.renderer.swap_channel(channel_id)
            await self.renderer.construct(self.root)

            # needs to be handled more generally elsewhere
            if mode == 'view':
                await self.renderer.deactivate()

            self.suppress_refresh()

        self.queue_event(__forward)