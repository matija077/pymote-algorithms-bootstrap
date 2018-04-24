from pymote import NetworkGenerator, write_pickle, read_pickle
from pymote.algorithms.saturation import saturacija
from pymote.algorithms.median import Median
from networkx import minimum_spanning_tree
import sys
import os


'''net_gen = NetworkGenerator(7)
net = net_gen.generate_random_network()

networkx_tree = minimum_spanning_tree(net)
net.adj = networkx_tree.adj'''

#current_directory = os.getcwd()
current_directory = sys.path[0]
directory = current_directory + "/graphs"

graph_name = "/test_median_4.txt"
net = read_pickle(directory + graph_name)

#net.algorithms = ( (saturacija), )
net.algorithms = ( (Median), )


if not os.path.exists(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        print e
try:
    pass
    #write_pickle(net,directory +  "/lista4_median.txt")
    write_pickle(net, directory + "/test_median_4.txt")
    #write_pickle(net, directory + "/test_saturation_1.txt")
    #write_pickle(net, directory + "/test_saturacija.tar.gz")
except Exception as e:
    print e

