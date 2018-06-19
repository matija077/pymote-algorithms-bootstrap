# -*- coding: utf-8 -*-
#12:45
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from pymote import Node
from random import random
import collections
from sys import maxint
from pymote.algorithms.test_helper import prepare_absorption, prepare_friendly_merger

class MegaMerger(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors', 'treeKey': 'TreeNeighbors', 'parentKey' : 'Parent', 'weightKey': 'Weight',
    'levelKey': 'Level', 'nameKey': 'Name', 'debugKey': 'DEBUG' , 'linkStatusKey':'LinkStatus', 'nodeEdgeKey': 'MinimumEdgeNode',
    'reportCounterKey': 'ReportCounter', 'numberOfInternalNodesKey': 'NumberOfInternalNodes', 'Let_us_merge_FriendlyMergerKey': 'Let_us_merge',
    'friendlyMergerMessagekey': 'FriendlyMergerMessage'}

    def initializer(self):
        ini_nodes = []
        max_node = Node()
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
           #node.memory[self.treeKey] = list(node.memory[self.neighborsKey])
            self.initialize(node)
            node.status = 'AVAILABLE'
            '''if random()<0.3:                #random initializers
                node.status = 'AVAILABLE'
                ini_nodes.append(node)'''

        # just for testing purposes
        #prepare_absorption(self)
        prepare_friendly_merger(self)



        # starting node has lover lvl for absorpton to work
        
        ini_nodes.append(self.network.nodes()[2])
        ini_nodes.append(self.network.nodes()[6])
        
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))  # to je spontani impuls
        
        
        # ne znam kako radi ovaj ini_nodes YOLO
        #ini_node = self.network.nodes()[1]                                                         ### 0. ili 1. imalvl 1? odluci se
        #self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,destination=ini_node))

    def available(self, node, message):

        #inicijatori
        if message.header == NodeAlgorithm.INI: #Spontaneously
            # koristimo za test absorptiona
            #prepared_data = self.prepare_message_data_concatenate(node)
            #for testing send Let us merge to the first neighbor.
            #node.send(Message(header='Let Us Merge', data=0, destination=node.memory[self.neighborsKey][0]))
            #node.send(Message(header='Let Us Merge', data=0, destination=node.memory[self.neighborsKey][1])) 
            ## Iskljucivo inicijatori, bilo jedan ili svi poslat ce svom prvom i drugm susjedu Let Us Merge
            self.send_Outside(node)

        if message.header=='Outside?':
            self.check_Outside_header(node, message)

        # ja ne kuzim kako rade ovi statusi stvarno
        if message.header=="Let Us Merge":
            #self.process_message_check_levels(node,message)
            #self.resolve(node, message)
            pass


        node.status = 'PROCESSING'

        '''node.send(Message(header='Activate', data='Activate'))
        if len(node.memory[self.neighborsKey])==1 : #ako je čvor list
            node.memory[self.parentKey] = list(node.memory[self.neighborsKey])[0]
            updated_data=self.prepare_message(node)
            node.send(Message(header='M', data = updated_data, destination = node.memory[self.parentKey]))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE' #izvrši se

    if message.header == 'Activate':
        destination_nodes = list(node.memory[self.treeKey])

        destination_nodes.remove(message.source)
        node.send(Message(header='Activate', data='Activate', destination=destination_nodes))
        if len(node.memory[self.treeKey])==1 :
            node.memory[self.parentKey] = list(node.memory[self.treeKey])[0]
            updated_data=self.prepare_message(node)
            node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
            node.status = 'PROCESSING'
        else:
            node.status='ACTIVE' #izvrši se'''

    def active(self, node, message):
        '''if message.header=='M':
            self.process_message(node,message)
            node.memory[self.treeKey].remove(message.source)
            if len(node.memory[self.treeKey])==1 :
                node.memory[self.parentKey] = list(node.memory[self.treeKey])[1]
                updated_data=self.prepare_message(node)
                node.send(Message(header='M', data=updated_data, destination=node.memory[self.parentKey]))
                node.status = 'PROCESSING' '''
        pass

    def processing(self, node, message):
        # valjda ovo rjesava donji TODO
        if message.header=='Outside?':
            self.check_Outside_header(node, message)

        #TODO add Outside? for other nodes, not just INI_NODES
        if message.header=="Let_us_merge":
            #           ako je poruka iz istog grada salji dalje, ako nije onda je to mergeEdge
            if node.memory[self.linkStatusKey][message.source] == 'INTERNAL':
                node.memory[self.debugKey] = 'YOLO'
#               we can't use destination_node in previous if because inital values of nodeEdgeKeys are the nodes themselves.
                destination_node = node.memory[self.nodeEdgeKey].keys()[0]
#               special case yeaaah. this sucks :( . Because node a will compute friendly merger, when b recieves Let_us_merge he we will 
#               use a's data, a a je vec povecao lvl. Ili promijeniti svugdje nacin slanja ili samo za ovaj specificni slucaj. Potrebno je 
#               imati i handler za ovaj slucaj.
                if (node.memory[self.Let_us_merge_FriendlyMergerKey] == False):
                    node.send(Message(header='Let_us_merge', data=0, destination=destination_node))
                else:
                    prepared_data = {'Level': node.memory[self.levelKey]}
                    node.send(Message(header='Let_us_merge', data=prepared_data, destination=destination_node))
            else:
                self.process_message_check_levels(node,message)

#           hardcoding :( . if we get let_us_merge and we are merging egde, we will remember it 
#           because we may need it for friendly merger. We need to set this somewhere.
#           TODO make this readable at least
#           because friendly merger resets Let_us_merge... we are going to check for default value first.
            if node.memory[self.Let_us_merge_FriendlyMergerKey] == False:
                if node.memory[self.linkStatusKey][message.source] == 'INTERNAL':
                    if node.memory[self.linkStatusKey][node.memory[self.nodeEdgeKey].keys()[0]] == 'EXTERNAL':
                        self.change_let_us_merge_FriendlyMergerKey(node, True)

            else:
                if node.memory[self.linkStatusKey][message.source] == 'INTERNAL':
                    self.process_message_check_levels(node, node.memory[self.friendlyMergerMessagekey])
                '''if node.memory[self.linkStatusKey][message.source] == 'EXTERNAL':
                    self.process_message_check_levels(node, message)
                else:
                    self.process_message_check_levels(node. node.memory[self.friendlyMergerMessagekey])'''


        if message.header=="absorption+orientation_of_roads" or message.header=="absorption":
            self.change_name_level(node, message)
            self.absorption(node, message)
            if message.header=="absorption+orientation_of_roads":
                #REDOSLJED FUNKCIJA MORA BITI OVAKAV. Prvo posaljemo parentu poruku, onda maknemo parenta.
                self.absorption(node, message, False, True)
                node.memory[self.parentKey] = message.source
#           TEST - start next cycle
            self.send_Outside(node)


        #TODO or internal external suspension
        if message.header=="Internal":
            self.change_link_status_key_internal(node, message.source)
        elif message.header=="External":
            self.change_link_status_key_external(node, message.source)
            if node.memory[self.parentKey]!=None:
                node.send(Message(header='Report', data=0, destination=node.memory[self.parentKey]))
            else:
#               TODO when merging egde is also downtown - WRONG, he should be sending let us merge. this is a quick fix for merge node being root.
                node.send(Message(header="Let_us_merge" ,data=0, destination=message.source))
                self.change_let_us_merge_FriendlyMergerKey(node, True)

        if message.header=="Report":
            node.memory[self.reportCounterKey] += 1
            #node.memory[self.nodeEdgeKey] = self.min_weight_two_nods(node.memory[self.nodeEdgeKey], message.source, node)
            self.min_weight_two_nods(node.memory[self.nodeEdgeKey], message.source, node)
            # -1 is for parent node, because root doesn't have a prent we will add > to if
            if (node.memory[self.reportCounterKey]>=node.memory[self.numberOfInternalNodesKey]-1):
                if node.memory[self.parentKey]==None:
                    #TODO END if given weights are both maxint for root
                    if (node.memory[self.nodeEdgeKey].values()[0][0] == maxint and 
                        node.memory[self.nodeEdgeKey.values()[0][1]] == maxint):
                            pass
                    node.send(Message(header='Let_us_merge', data=0, destination=node.memory[self.nodeEdgeKey].keys()[0]))
                else:
                    node.send(Message(header='Report', data=0, destination=node.memory[self.parentKey]))
                node.memory[self.reportCounterKey] = 0

    def saturated(self, node):
        pass

    def prepare_message(self,node):
        pass

    '''def prepare_message_data_concatenate(self, node):
      
        args = {self.nameKey: node.memory[self.nameKey], self.levelKey: node.memory[self.levelKey]}
        #data = ",".join(args)
        return args'''

    def process_message(self, node, message):
        pass

    def send_Outside(self, node):
        #TODO everytime node receive Internal, send message again somehow TEST
        node.memory[self.nodeEdgeKey] = self.min_weight(node)
        node.memory[self.debugKey] = node.memory[self.nodeEdgeKey]
        # solution for infinitive is {self node: [maxint, maxint]}. we don't want node to send message to itself
        if node.id != node.memory[self.nodeEdgeKey].keys()[0].id:
            node.send(Message(header='Outside?', data=0, destination=node.memory[self.nodeEdgeKey]))

        #node.memory[self.nodeEdgeKey] = {node.memory[self.weightKey].keys()[0]: node.memory[self.weightKey].values()[0]}
        #node.send(Message(header='Outside?', data=0, destination=node.memory[self.nodeEdgeKey]))

#   it's a duplicate in 2 states, available and processing
    def check_Outside_header(self, node, message):
        if message.source.memory[self.nameKey]==node.memory[self.nameKey]:
                node.send(Message(header='Internal', data=0, destination=message.source))
                self.change_link_status_key_internal(node, message.source)
        elif node.memory[self.levelKey] >= message.source.memory[self.levelKey]:
            node.send(Message(header='External', data=0, destination=message.source))
            self.change_link_status_key_external(node, message.source)
        else:
            # TODO internal external suspension, this suspension is never gona be "unsuspended"
            #   need to check some things here, it's an absorption, so things start again, it's not like
            #   in other suspension where we wait.
            pass

#   name and level changes are in a function because they will be reused and we need to 
#   check queue whenever level changes
#   what_is_it: is it absorption or friendly merger?
    def change_name_level(self, node, message=None, city_name = None, what_is_it='absorption'):
        if what_is_it == 'absorption':
            node.memory[self.nameKey] = message.source.memory[self.nameKey]
            node.memory[self.levelKey] = message.source.memory[self.levelKey]
            self.check_queue()
        elif what_is_it == 'friendly_merger':
            node.memory[self.nameKey] = city_name
            node.memory[self.levelKey] += 1
        self.reset(node)

#   put here everything that needs to be reset after absorption or friendly merger happens
#   TODO fidn out what else needs to be reset
    def reset(self, node):
        self.change_let_us_merge_FriendlyMergerKey(node, False)

#   TODO
    def check_queue(self):
        pass

    def check_let_us_merge_friendlyMerger_messageSource(node, message):
        pass
        if node.memory[self.linkStatusKey][message_source] == 'INTERNAL':
            pass


#   equal = frendly merger or suspenson, smaller = absorption, bigger = never happens
#   special_case handler is here. 
    def process_message_check_levels(self, node, message):
        special_case_boolean = False
        if message.data != 0:
            if message.data['Level'] == node.memory[self.levelKey]:
                special_case_boolean = True
        if message.source.memory[self.levelKey] < node.memory[self.levelKey]:
            self.absorption(node, message, True)
        elif message.source.memory[self.levelKey] == node.memory[self.levelKey] or special_case_boolean == True:
            if node.memory[self.Let_us_merge_FriendlyMergerKey] == True:
                self.friendly_merger(node, message.source, True)
            else:
                self.change_let_us_merge_FriendlyMergerKey(node, True)
                node.memory[self.friendlyMergerMessagekey] = message

    def change_link_status_key_internal(self, node, message_source):
        node.memory[self.linkStatusKey][message_source] = "INTERNAL"
        node.memory[self.numberOfInternalNodesKey] += 1
    def change_link_status_key_external(self, node, message_source):
        node.memory[self.linkStatusKey][message_source] = "EXTERNAL"

    def change_let_us_merge_FriendlyMergerKey(self, node, TRUE=False):
        if TRUE == True:
            node.memory[self.Let_us_merge_FriendlyMergerKey] = True
        else:
            node.memory[self.Let_us_merge_FriendlyMergerKey] = False

#   param begining - pocetnio slanje
#   orientation_of_rodas - Ako saljemo parentu, trebamo promijeniti orientaciju do roota. drugi cvorovi koji nisu na putu
#       zbog uvjeta slanja poruka nece slati poruke parentima, osim ako vujet niej True.
    def absorption(self, node, message, param_begining=False, orientation_of_roads=False):
        if node.memory[self.linkStatusKey][message.source]=='EXTERNAL':
            self.change_link_status_key_internal(node, message.source)
        if param_begining==True:
            node.send(Message(header="absorption+orientation_of_roads", data=0, destination=message.source))
            self.send_Outside(node)
        else:
            if orientation_of_roads==True:
                if node.memory[self.parentKey]!=None:
                    node.send(Message(header="absorption+orientation_of_roads", data=0, destination=node.memory[self.parentKey]))
                else:
                    # DEBUG
                    node.memory[self.debugKey] = "Nemam parenta"
            else:
                destination_nodes = list(filter(lambda neighbor:  neighbor != node.memory[self.parentKey] and neighbor != message.source
                    and node.memory[self.linkStatusKey][neighbor] == 'INTERNAL', node.memory[self.neighborsKey])) 
                node.send(Message(header="absorption", data=0, destination=destination_nodes))

#   compute new downtown (smaller ID) from two nodes independently one form antoher. add new name and increase lvl by one.
#   we need to change the orientation of roads depending on which node is the new downtown, also change internal nodes
    def friendly_merger(self, node, b, param_begining=False, orientation_of_roads=False):
        if param_begining == True:
            new_downtown = self.min_id_two_nodes(node, b)
            self.change_name_level(node, None, new_downtown.id, 'friendly_merger')
            self.change_link_status_key_internal(node, b)
#           without parent, message is being sent to everyone!!
            if node.memory[self.parentKey] != None:
                node.send(Message(header="friendly_merger+orientation_of_roads", data=0, destination=node.memory[self.parentKey]))
#           because we change parent, we need to send the message first.
            if new_downtown.id != node.id:
                node.memory[self.parentKey] = b


    def initialize(self, node):
        node.memory[self.weightKey] = {}
        node.memory[self.linkStatusKey] = {}
        node.memory[self.levelKey] = 0
        node.memory[self.nameKey] = node.id
        node.memory[self.parentKey] = None
        node.memory[self.reportCounterKey] = 0
        node.memory[self.numberOfInternalNodesKey] = 0
        node.memory[self.Let_us_merge_FriendlyMergerKey] = False
        node.memory[self.friendlyMergerMessagekey] = False
        # sam sebe dodamo kao defaultni minimumEdgeNode sa max weightom.
        node.memory[self.nodeEdgeKey] = {node: [maxint, maxint]}
        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),
            max(node.id, neighbor.id)]

        for neighbor in node.memory[self.neighborsKey]:
            node.memory[self.weightKey][neighbor] = [min(node.id, neighbor.id),max(node.id, neighbor.id)]
            node.memory[self.linkStatusKey][neighbor] = "UNUSED"


    def min_weight(self,node):
        #TODO if no unused edge found, return infinitive weight TEST
        #we are considering only unused edges.
        temp_unused_edges = dict()
        #temp_unused_edges = [(k, v) if v2='UNUSED' for (k,v), (k, v2) in zip(node.memory[self.weightKey].items(), node.memory[self.linkStatusKey].items())]
        for k,v in node.memory[self.weightKey].iteritems():
            if node.memory[self.linkStatusKey][k] == 'UNUSED':
                temp_unused_edges[k] = v
#       TEST - solution for TODO 
        if not temp_unused_edges:
            infinitiveEdge = {node: [maxint,maxint]}
            return infinitiveEdge
        orderedDict = collections.OrderedDict(sorted(temp_unused_edges.iteritems(), key=lambda (k,v):v[0]))            
        min_1= orderedDict.values()[0][0]
        print(min_1)        
        uzi_izbor={}

#        print("sortirano 1 ")               
        for o in orderedDict:
            #print orderedDict[o]
            if orderedDict[o][0] == min_1:
                uzi_izbor.update({o:orderedDict[o]})
    
        orderedDict = collections.OrderedDict(sorted(uzi_izbor.iteritems(), key=lambda (k,v):v[1]))       
#        print("sortirano 2")
#        for o in orderedDict:
#            print orderedDict[o]
        #iz nekog razloga nece vratiti uredeni par {key, value} pa sam ovako napravio
        mergeEdge = dict()
        mergeEdge[orderedDict.keys()[0]] = orderedDict.values()[0]
        return mergeEdge

    '''
        usporedujemo weightove cvora koji na kojemu se izvrsava i onog koji je poslao poruku
        Ako je weight cvora manji onda ostavljamo kako je bilo, ako nije onda mijenjamo weigthove
        u trenutnom cvoru. S obzirom da zelimo imati putanju poruka kako ne bi morali raditi broadcast
        od roota prema mergeEdgu, memory    oramo promijeniti nas dicitonary koji je bio <id cvora koji je poslao poruku 
        onom koji je poslao poruku trenutnom: mergeEdge Weight> u {id cvora koji je poslao poruku: mergeEgde Weight}.
        Mijenjamo samo vlasnika mergeEdge Weighta kako bi znali put od roota prema istome. Weight ostaje isti.  
    '''
    def min_weight_two_nods(self, node_id_weight_a, message_source, node):
        # node_id_* je dictionary <id  cvora koji je poslao poruku: weight>
        # NIKAD NE ZABORAVI KREIRAT NOVU VARIAJABlU SA KONTSTRUKTOROM ISTE AKO CES JOJ DODIJELTII VEC
        # POTOSTOJECE VRIJEDNOSTI ....
        node_id_weight_b = dict(message_source.memory[self.nodeEdgeKey])
        weight_node_a = node_id_weight_a.values()
        weight_node_b = node_id_weight_b.values()
        node.memory[self.debugKey] = [node_id_weight_a, node_id_weight_b]

        if weight_node_a[0]<weight_node_b[0]:
            node.memory[self.nodeEdgeKey] = node_id_weight_a
            return
        elif weight_node_a>weight_node_b[0]:
            temp = dict()
            temp[message_source] =  node_id_weight_b.pop(node_id_weight_b.keys()[0])
            #node_id_weight_b[message_source] = node_id_weight_b.pop(node_id_weight_b.keys()[0])
            #return node_id_weight_b
            node.memory[self.nodeEdgeKey] = temp
            return
        elif weight_node_a[1]<weight_node_b[1]:
            node.memory[self.nodeEdgeKey] = node_id_weight_a
            return
        else:
            temp = dict()
            temp[message_sourc] = node_id_weight_b.pop(node_id_weight_b.keys()[0])
            #node_id_weight_b[message_source] = node_id_weight_b.pop(node_id_weight_b.keys()[0])
            #return node_id_weight_b
            node.memory[self.nodeEdgeKey] = temp
            return

    def min_id_two_nodes(self, node1, node2):
        if node1.id < node2.id:
            return node1
        else:
            return node2

    STATUS = {
              'AVAILABLE': available,
              'PROCESSING': processing,
              'SATURATED': saturated,
             }