

N = [[7, 9, -4.851], [7, 2, 2.9585], [7, 5, -4.3057], [7, 3, 1.9569], [7, 4, 4.4298], [7, 0, -0.57024], [9, 0, 4.9738], [9, 3, 6.7302], [9, 4, 9.3592], [9, 2, 8.1628], [9, 6, 1.361], [0, 4, 4.8603], [0, 5, -3.9274], [0, 8, 3.426], [0, 6, -3.5175], [0, 1, 0.83131], [4, 8, -1.3038], [4, 1, -3.9057], [4, 5, -9.2724], [4, 2, -1.9237], [8, 6, -6.5603], [8, 2, -0.56773], [8, 1, -2.9797], [8, 5, -8.4274], [8, 3, -2.1633], [6, 2, 6.5333], [2, 5, -7.8453], [2, 1, -2.3873], [3, 1, -1.1802], [5, 1, 4.9125]]

nodes_dict = {}

#Add node connections to Nx, add relative NX delays in Cx 
for connection in N:
    if f"N{connection[0]}" in nodes_dict:
        nodes_dict[f"N{connection[0]}"].append(connection[1])
        nodes_dict[f"C{connection[0]}"].append(connection[2]*-1)
    else:
        nodes_dict[f"N{connection[0]}"] = [connection[1]]
        nodes_dict[f"C{connection[0]}"] = [connection[2]*-1]
    if f"N{connection[1]}" in nodes_dict:
        nodes_dict[f"N{connection[1]}"].append(connection[0])
        nodes_dict[f"C{connection[1]}"].append(connection[2])
    else:
        nodes_dict[f"N{connection[1]}"] = [connection[0]]
        nodes_dict[f"C{connection[1]}"] = [connection[2]]




#Check the node distance between node 0
L1 = nodes_dict["N0"]
L2 = []
for node in L1:
    branches = nodes_dict[f"N{node}"]
    for nodes2 in branches:
        if (nodes2 not in L2) and (nodes2 not in L1) and nodes2 != 0:
            L2.append(nodes2) 
# print(nodes_dict)
#Calculate weights to use to sum the parts that will be used to calculate the offset for each layer node, using only current node plus onne node up to calculate
L1_dict ={}
for node in L1:
    l0_connections = 1
    l1_connections = 0
    for connection in nodes_dict[f"N{node}"]:
        if connection in L1:
            l1_connections += 1 
    L1_dict[f'N{node}'] = l0_connections + l1_connections*1/2

L2_dict = {}
for node in L2:
    l1_connections = 0
    l2_connections = 0
    for connection in nodes_dict[f"N{node}"]:
        if connection in L1:
            l1_connections += 1
        if connection in L2:
            l2_connections += 1
    L2_dict[f'N{node}'] = l1_connections/2 + l2_connections/3

#Take weighted sums of L1 and L0 paths to estimate offset
for node in L1:
    average_L1_offset = 0
    index = 0
    weight = L1_dict[f'N{node}']
    for connection in nodes_dict[f"N{node}"]:
        if connection in L1:
            #get the layer ones connection to layer 0 offset
            l0_c_index = nodes_dict[f"N{connection}"].index(0)  
            path_0to1_offset = nodes_dict[f"C{connection}"][l0_c_index]
            path_1to1_offset = nodes_dict[f"C{node}"][index]
            average_L1_offset +=  (path_0to1_offset + path_1to1_offset)/(2*weight)     
        elif connection == 0:
            average_L1_offset += nodes_dict[f"C{node}"][index] /(1*weight)
        index += 1
    L1_dict[f"C{node}"] = average_L1_offset
print(L2_dict)
#Using weigthed sum offsets from L1, take weighted sum offsets from L1 and L2
for node in L2:
    average_L2_offset = 0
    index = 0
    weight = L2_dict[f'N{node}']
    for connection in nodes_dict[f"N{node}"]:
        if connection in L2:
            continue
            #in layer two there are no connection so we can skip
        elif connection in L1:
            average_L2_offset += nodes_dict[f"C{node}"][index] /(2*weight)
        index += 1
    L2_dict[f"C{node}"] = average_L2_offset




for i in range(10):
    if f"C{i}" in L1_dict:
        print(f"Offset Node {i}: {L1_dict[f'C{i}']}")
    elif f"C{i}" in  L2_dict:
        print(f"Offset Node {i}: {L2_dict[f'C{i}']}")












