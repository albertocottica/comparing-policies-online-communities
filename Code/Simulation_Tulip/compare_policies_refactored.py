# Grows networks under baseline conditions (no policies) and with community management policies
# Run within the Tulip GUI

from tulip import *
from random import random # uniform distribution! 
import time
import csv

class intimacyModel(object):
    '''
    Not sure what to put in the docstring! 
    '''
    
    def __init__(self, founders, networkSize, beta):
        '''
        (intimacyModel object, int, int, float) => intimacyModel object
        '''
        super(intimacyModel, self).__init__()
        
        self.graph = tlp.newGraph('mainGraph')
        
        # model parameters
        self.founders = founders # the number of members that are already in the community at time 0
        self.networkSize = networkSize
        self.beta = beta # the intimacy strength parameter
        
		# recording timestep for convenience, so the evolution of the network can be animated if needed
		self.timestepProp = None
		self.time_step = 0

		self.newly_added_node = None
		self.current_node_index = 0
		self.current_edge_index = 0
        
    def initialize(self):
        '''
        Start with founders nodes, recicprocally connected both ways in the INTIMACY network
        Nodes are singletons in the COMMUNICATION network
        '''
	    # policy parameters (in a tuple for iteration)
	    bit = [False, True]
        
    	for onboarding in bit:
    		for engagement in bit:
    			policy = self.graph.addSubGraph('onboard'+str(onboarding) + 'Engage' + str(engagement))
				intima = policy.addSubGraph('intimacyNetwork')
				comms = policy.addSubGraph('communicationsNetwork'
                )

        # add the nodes 
        
        for i in range (self.founders):
            newNode = intima.addNode()
            comms.addNode(newNode)
            
        # now the edges, only in intima
        

    def compute_probability(C, xcm, xu):
    	'''
    	(float, float, float) => float
    	computes the probability that a user will be active based on a constant (C), the number of comments received by 
    	community managers (xcm), and the number of comments received by other users (xu)
    	should I do a full simulation of the logistic?
    	'''
    	if xcm == 0:
    		betaxcm = 0
    	elif xcm == 1:
    		betaxcm = 0.23
    	elif xcm == 2:
    		betaxcm = 0.23 + 0.15
    	else: 
    		betaxcm = 0.23 + 0.15 + 0.1
		
    	# based on table 5 in Microfoundations

    	if xu == 0:
    		betaxu = 0.04
    	elif xu == 1:
    		betaxu = 0.04 + 0.03
    	elif xu == 2:
    		betaxu = 0.04 + 0.03 + 0.02
    	elif xu > 2 and xcm < 11:
    		betaxu = 0.04 + 0.03 + 0.02 + 0.01 * (xcm - 2)
    	else: 
    		betaxu = 0.04 + 0.03 + 0.02 + 0.01 * 11		
	
    	# based on table 6 in Microfoundations.
	
    	total = C + betaxcm + betaxu 
    	if total < 0.99:
    		return total
    	else:
    		return 0.99
            
	def findEdge(node1, node2, graph1, directed = False, create = True):
		'''
        finds an edge connecting two given nodes if it exists,
        if not returns a newly created edge unless stated otherwise
        deals with either directed or undirected graphs
        '''
		e = graph1.existEdge(node1, node2)
		if e.isValid():
			return e
		else:
			if not directed:
				e = graph1.existEdge(node2, node1)
				if e.isValid():
					return e
				else:
					if create:
						e = graph1.addEdge(node1, node2)
						return e                        
			else:
				if create:    
					e = graph1.addEdge(node1, node2)
					return e
				else:
					return None

    def remove_node(t_interval, t_threshold, graph, timeNow, birthDateProperty, intimacyProperty, deadProperty):
    	'''
    	(float, float, graph, int, integerProperty, doubleProperty, booleanProperty) => None
    	Remove nodes from the network if their value of intimacyProperty is lower than t_threshold, AND if they have been alive for longer than t_interval.
    	Removal happens by setting deadProperty to True.
    	intimacyProperty carries edge weight
    	'''
    	for n in graph.getNodes():
    		thisNodeLifespan = timeNow - birthDateProperty[n]
    		mS = 0
    		for e in graph.getInEdges(n):
    			mS += intimacyProperty[e]
    		if thisNodeLifespan > t_interval and mS < t_threshold:
    			deadProperty[n] = True
    	return None
	
    def enact_engagement(manager, timePeriod, commGraph, commTimeProperty, intimaGraph, weightProperty):
        '''
        (node, int, graph, integerProperty, graph, doubleProperty) => None
    	manager creates new edges with herself as a source and each node in commGraph and intimaGraph as a target.
    	This behavior at timePeriod is triggered by target nodes being themselves sources of one or more edges in 
    	commsGraph having commTimeProperty == timePeriod - 1. New edges have commTimeProperty = timePeriod in 
    	commGraph, and weightProperty = 1 in intimaGraph. Updated edges in intimaGraph have weight += 1.
    	'''
    	for e in commGraph.getEdges():
    		if commTimeProperty[e] == timePeriod - 1:
    			engageTarget = commGraph.source(e)
    			if engageTarget != manager:
    				engageCommsEdge = commGraph.addEdge(manager, engageTarget)
    				commTimeProperty [engageCommsEdge] = timePeriod
    				engageIntimaEdge = findEdge(manager, engageTarget, intimaGraph, True, False)
    				if engageIntimaEdge == None: #the edge does not exist, so we must add it
    					engageIntimaEdge = intimaGraph.addEdge(manager, engageTarget)
    					weightProperty[engageIntimaEdge] = 1
    				else: # there alleady is an edge from manager to engageTarget, so we update it
    					weightProperty[engageIntimaEdge] += 1
    	return None

    def enact_onboarding ():
    
    def initialize(founders, edgeWeight):
        '''
        (int, float) => graph
        initializes a directed graph with number of nodes = founders.
        The graph has two subgraphs. In the intimacy subgraph, all nodes form a clique. All edges have weight edgeWeight.
        In the communication subgraph, all nodes are disconnected
        '''
        mainGraph = tlp.newGraph('mainGraph')


    def generateNetwork(inputTuple):
        # initialize
        # at each timestep:
            # add one node
            # nodes communicate
            # enact onboarding (if present)
            # enact engagement (if present)
            # update intimacy edge weight
            # remove node (if present)
