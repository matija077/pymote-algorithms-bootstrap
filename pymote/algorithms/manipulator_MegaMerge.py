from pymote import NetworkGenerator
from pymote import Simulation
from pymote.npickle import write_pickle
from pymote.npickle import read_pickle
#from pymote.algorithms.prsa_MegaMerger import MegaMerger
from pymote.algorithms.MegaMeger import MegaMerger
from networkx import minimum_spanning_tree

net = read_pickle('mreza2.txt')

net.algorithms = ( MegaMerger, )

mySim = Simulation( net )
mySim.run()

'''for node in net.nodes():
    print node.id, node.memory['I']'''