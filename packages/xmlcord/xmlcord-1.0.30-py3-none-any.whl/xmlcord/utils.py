
def similarity(sample1, sample2):
    connections = []
    for character1 in sample1:
        for i, character2 in enumerate(sample2[::-1]):
            index = len(sample2) - i - 1
            if character1 == character2:
                # finds the highest position within connection layers where index can be inserted
                if connections:
                    # goes through all the connection layers in a reverse order
                    for depth, layer in enumerate(connections[::-1]):
                        if min(layer) < index:
                            layer_index = len(connections) - depth
                            if layer_index < len(connections):
                                if index not in connections[layer_index]:
                                    connections[layer_index].append(index)
                            else:
                                connections.append([index])
                            break
                    else: 
                        if index not in connections[0]:
                            connections[0].append(index)
                else:
                    # if connection list is empty create a new connection and insert first (lowest) found value
                    connections.append([index])
            # print(character1, character2)
            # print(connections)
        
    # print(connections)

    return (len(connections) / len(sample1)) / (len(sample1) + len(sample2) - 2 * len(connections) + 1)


def find_item_in_array(string, array, threshold=0):
    value = 0
    out = None
    for item in array:
        sim = similarity(string.lower(), item.lower())
        if (value == 0 or sim > value) and sim >= threshold:
            value = sim
            out = item
    return out


if __name__ == '__main__':
    s1 = "Fliqqrrrr"
    s2 = "Flqqrrrri"
    print(similarity(s1, s2))