#this project is implementation of fat tree topology

#we use GraphVisualization which works with networkx to visualize graph
import GraphVisualization
G = GraphVisualization.GraphVisualization()


#import k from user's input
k = int(input("K?"))

bv = int(input("Degree Constraint?"))

#open the output file
f = open("output.txt","w")


#Calculating the pods, servers, core switches, aggregation switches

#connected list used when we want to keep track of connection and which are 1
connected= []

pods_Count = int(k)
Servers_Count = int(pods_Count * ((k / 2) ** 2))
Servers_In_Pod = (k / 2) ** 2
AggrSwitch_Count = int((k ** 2) / 2)
EdgeSwitch_Count = AggrSwitch_Count
CoreSwitch_Count = int((k / 2) ** 2)
AllSwitch_Count = CoreSwitch_Count + EdgeSwitch_Count + AggrSwitch_Count
Elements_Count = AllSwitch_Count + Servers_Count
EdgeSwitch_Count_In_Pods = k//2
AggrSwitch_Count_In_Pods=EdgeSwitch_Count_In_Pods

# Each Element has connection to itself, First we add those connections to output
for i in range(Elements_Count):
    out = str(i)+ "\t" + str(i) + "\t" +"1" + "\n"
    connected.append((i, i))
    f.write(out)



# counter is way that we address number of edge switches
# counter starts at number of servers because 0 should be included in server counts
counter = Servers_Count

# server counter is a way to address the server for mapping between edge switches and servers
Server_counter = 0

# program goes stage by stage bottom up, first we create links between edge and servers

for i in range(pods_Count):

    for j in range(EdgeSwitch_Count_In_Pods):

        for l in range (k//2):

            out = str(counter)+"\t"+str(Server_counter)+"\t"+"1"+"\n"
            f.write(out)
            connected.append((counter,Server_counter))
            G.addEdge(counter, Server_counter)

            out = str(Server_counter) + "\t" + str(counter) + "\t" + "1" + "\n"
            f.write(out)
            connected.append((Server_counter,counter ))
            G.addEdge(Server_counter,counter )

            Server_counter+=1

        counter += 1

#Handling connection between Aggregation switches and edge switches

for i in range(pods_Count):

    for j in range(AggrSwitch_Count_In_Pods):

        for l in range (k//2):

            out = str(counter)+"\t"+str(Server_counter)+"\t"+"1"+"\n"
            f.write(out)
            connected.append((counter,Server_counter ))
            G.addEdge(counter,Server_counter )

            out = str(Server_counter) + "\t" + str(counter) + "\t" + "1" + "\n"
            f.write(out)
            connected.append((Server_counter,counter ))
            G.addEdge(Server_counter,counter )
            Server_counter+=1

        Server_counter-=k//2
        counter += 1
    Server_counter+=k//2




#Implementing link between aggregation switches and core switches

# we create core because when link reaches the end of cores we want to reset cores
core = []
for i in range(CoreSwitch_Count):
    core.append(counter)
    counter+=1


p = 0
for i in range(pods_Count):
    for j in range(AggrSwitch_Count_In_Pods):
        for l in range(k // 2):
            counter=counter-k+1
            out = str(Server_counter) + "\t" + str(core[p]) + "\t" + "1" + "\n"
            f.write(out)

            connected.append((Server_counter,core[p] ))
            G.addEdge(Server_counter,core[p] )
            out = str(core[p]) + "\t" + str(Server_counter) + "\t" + "1" + "\n"
            f.write(out)
            connected.append((core[p],Server_counter ))
            G.addEdge(core[p],Server_counter )
            p+=1
            if(p==(k//2)**2):
                p=0
        Server_counter+=1
    p = p+1


# implementing the zero connections
counter = 0

for i in range (Elements_Count):
    for j in range(Elements_Count):
        if (i,j) not in connected:
            f.write(str(i)+"\t"+ str(j)+"\t"+"99999"+"\n")
            counter+=1

# Finally visualizing the data using mathplotlib
G.visualize()

# convert G to stp file
# note that the node index of stp file starts from 1
H = nx.Graph()
H.add_edges_from(G.visual)
output = open("FatTree{}.stp".format(k), "w+")

with open("workers.txt", "r") as data:
    workers = [int(line.strip()) + 1 for line in data.readlines()]

output.write("   33D32945 STP File, STP Format Version 1.0\n\n")
output.write(
    "   SECTION Comment\n   Name    "Fat Tree"\n   Creator "Ivan Lin"\n   Remark  "A Fat Tree Topology in Data Center"\n   END\n\n"
)

output.write("   SECTION Graph\n   Nodes {}\n   Edges {}\n".format(H.number_of_nodes(), H.number_of_edges()))
for edge in H.edges:
    if (edge[0] in workers) and (edge[1] in workers):
        output.write("   E {} {} {}\n".format(edge[0] + 1, edge[1] + 1, 2))
    else:
        output.write("   E {} {} {}\n".format(edge[0] + 1, edge[1] + 1, 1))
    
output.write("   END\n\n")

output.write("   SECTION Terminals\n")
output.write("   Terminals {}\n".format(len(workers)))
for worker in workers:
    output.write("   T {}\n".format(worker))
output.write("   END\n\n")

output.write("   SECTION MaximumDegrees\n")
for node in range(0, H.number_of_nodes()):
    if node in workers:
        output.write("   MD {} 1\n".format(node+1))
    else:
        output.write("   MD {} {}\n".format(node+1, bv))
output.write("   END\n\n")
output.write("   EOF")


