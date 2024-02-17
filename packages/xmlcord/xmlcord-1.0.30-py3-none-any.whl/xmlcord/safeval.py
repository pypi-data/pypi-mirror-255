import re



def addition(a, b):
    if str in (type(a), type(b)):
        a = str(a)
        b = str(b)

    return b + a


OPERATORS = {
    '+':  (addition, 1),
    '-':  (lambda a, b: b - a,  1),
    '*':  (lambda a, b: b * a,  2),
    '/':  (lambda a, b: b / a,  2),
    '==': (lambda a, b: b == a, 0),
    '!=': (lambda a, b: b != a, 0),
    '>':  (lambda a, b: b > a,  0),
    '>=': (lambda a, b: b >= a, 0),
    '<':  (lambda a, b: b < a,  0),
    '<=': (lambda a, b: b <= a, 0),
    '^':  (lambda a, b: b or a, 0),
    '&':  (lambda a, b: b and a, 0),
    '(':  (lambda *_: _, 0),
    ')':  (lambda *_: _, 0)
}

CONST = r"(?P<const>[0-9\.]+)"
STR   = r"\"(?P<str>.*?)\""
VAR   = r"(?P<var>[a-zA-Z_][a-zA-Z0-9_\. ]*[a-zA-Z0-9_]+)"
#                        this escape only applies to the first char in OP
OP    = r"(?P<op>" + '|'.join(f'\\{op}' for op in OPERATORS) + ")"

# this should happen on decorator
# currently defaults to None
def get_var(tag, var_name, default=None):
    name, *index = var_name.split('.')
    while True:
        # BUG: this causes the tag to look for state var all the
        # way up to root before even attempting to consider tag args
        # BUG: used to just check if var, this made it impossible to get 0
        if (var := tag.get_state(name)) is not None:
            # supports for chaining indexes??
            if index:
                index = int(index[0])
                # temp solution to ensure out of bounds errors are not thrown,
                # returns 0 for easier stats
                if len(var) > index:
                    return var[index]
                else:
                    return 0
            return var
        if (tag := tag.parent) is None:
            return default


def shunting_yard(tag, string):
    op_stack = []
    out_queue = []
    
    ex = f"{CONST}|{STR}|{OP}|{VAR}"

    try:

        for match in re.finditer(ex, string):
            const, string, op, var = match.groups()

            if const:
                out_queue.append(int(const))

            elif string:
                out_queue.append(string)

            elif var:
                v = get_var(tag, var)
                out_queue.append(v)

            elif op:
                if op == ')':
                    while (next_op := op_stack.pop())[0] != '(':
                        _, func, _ = next_op

                        out_queue.append(
                            func(out_queue.pop(), out_queue.pop())
                        )
                else:
                    func, precedence = OPERATORS[op]

                    if op_stack and op_stack[-1][0] != '(':
                        _, prev_func, prev_precedence = prev_op = op_stack.pop()

                        if op != '(' and prev_precedence >= precedence:
                            out_queue.append(
                                prev_func(out_queue.pop(), out_queue.pop())
                            )
                        else:
                            # append back the previous operator, if not used
                            op_stack.append(prev_op)

                    op_stack.append((op, func, precedence))

        for (op, func, _) in op_stack[::-1]:
            out_queue.append(
                func(out_queue.pop(), out_queue.pop())
            )

        return out_queue[0]
    
    except Exception as err:
        raise Exception(f"Failed to evaluate: \n{string}\n" + err)


if __name__ == '__main__':
    s = "((5 + 5) * 3 + 1 == 32) == 0"
    out = shunting_yard(None, s)
    print(out)