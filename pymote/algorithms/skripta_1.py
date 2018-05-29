from pymote import NetworkGenerator
from pymote.npickle import read_pickle, write_pickle
from networkx import minimum_spanning_tree
from pymote.algorithms.MegaMeger import MegaMerger

# create tree fron network
'''net_gen = NetworkGenerator(4)
net = net_gen.generate_random_network()
#net.show()
graph_tree = minimum_spanning_tree(net)
net.adj = graph_tree.adj'''

#print net.nodes()[1]
#self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))

#read network from disk
net_name = "mreza.txt"
net = read_pickle(net_name)

net.algorithms = (MegaMerger,)

#write_pickle(net, 'mreza.tar.gz')
write_pickle(net, 'mreza.txt')