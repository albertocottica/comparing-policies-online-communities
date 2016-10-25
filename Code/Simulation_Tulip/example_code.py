# Powered by Python 2.7

# To cancel the modifications performed by the script
# on the current graph, click on the undo button.

# Some useful keyboards shortcuts : 
#   * Ctrl + D : comment selected lines.
#   * Ctrl + Shift + D  : uncomment selected lines.
#   * Ctrl + I : indent selected lines.
#   * Ctrl + Shift + I  : unindent selected lines.
#   * Ctrl + Return  : run script.
#   * Ctrl + F  : find selected text.
#   * Ctrl + R  : replace selected text.
#   * Ctrl + Space  : show auto-completion dialog.

from tulip import *
from scipy.special import expit
from random import random # uniform distribution! 
from math import exp
import csv

# the updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# the pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the "Run script " button.

# the runGraphScript(scriptFile, graph) function can be called to launch another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call (in the form [a-zA-Z0-9_]+.py)

# the main(graph) function must be defined 
# to run the script on the current graph

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
		betacu = 0.04
	elif xu == 1:
		betaxu = 0.04 + 0.03
	elif xu == 2:
		betaxu = 0.04 + 0.03 + 0.02
	elif xu > 2 and xcm < 11:
		betaxu = 0.04 + 0.03 + 0.02 + 0.01 * (xcm - 2)
	else: 
		betaxu = 0.04 + 0.03 + 0.02 + 0.01 * 11		
	
	# based on table 6 in Microfoundations.
	
	return c + betaxcm + betaxu 


def initialize_model(startNodes, edgeWeight):
	'''
	(int, float) => none	
	Initialize to n connected nodes
	'''
	
	intima = graph.addSubGraph('intimacyNetwork')
	comms = graph.addSubGraph('communicationsNetwork')
	for i in range(startNodes):
		newNode = intima.addNode()
		birthDate[newNode] = 0
		manager[newNode] = False
		newNode = comms.addNode()
		if i > 0:
			for n in intima.getNodes():
				if n != newNode:
					e1 = intima.addEdge(newNode, n)
					intimacy[e1] = edgeWeight
					e2 = intima.addEdge(n, newNode)
					intimacy[e2] = edgeWeight
		# for now I am not adding comm events before time 0
		
	# add the community manager
	commManager = intima.addNode()
	manager[commManager] = True
	
					
def grow_network(rate):
	'''
	(float) => none
	add rate nodes at each time step
	'''
	newNode = intima.addNode()
	birthDate[newNode] = t 
	manager[newNode] = False
	newNode = comms.addNode()
	
def whether(node):
	'''
	(node) => bool
	Decide whether node will engage in communication. Return True if it will, False otherwise.
	'''
	# find out whether node had incoming communication at time t-1
	# iterate over previous comm event	for n in comms.getNodes():
	xcm = 0 # intialize the counters of incoming comments
	xu = 0 
	for e in comms.getInEdges():
		if commDate[e] == t-1:
			if manager [comms.source(e)] == True:
				xcm += 1 
			else:
				xu += 1
	prob = compute_probability(C, xcm, xu)
	if random() < prob:
		return True
	else: 
		return False
		
def compute_denominator_P_phi(graph1):
	'''
	(graph) => float
	Returns the denominator of equation 3 in the preliminary note for graph1 (intimacy graph).
	'''
	denominator = 0
	for n1 in graph1.getNodes():
		for n2 in graph1.getNodes():
			edge1 = graph1.getEdge(n1,n2)
			edge2 = graph1.getEdge(n2,n1)
			if edge1.isValid() and edge2.isValid() and n1 != n2:
				denominator += 1 + beta * intimacy[edge1] * intimacy[edge2] 
	return denominator
				
		
def communicate(node1, node2):
	'''
	(node, node) => bool
	Returns True if node1 decides to communicate with node2, False otherwise.
	'''
	edge1 = intima.getEdge (node1, node2)
	edge2 = intima,getEdge (node2, node1)
	probComm = (1 + beta * intimacy[edge1] * intimacy[edge2])/denominator
	if random.random() < probComm:
		return True
	else:
		return False

def update_intimacy():
	'''
	(none) => none
	updates the intimacy graph based on recent communication events and the time discount factor
	'''
	for n1 in intima.getNodes():
		for n2 in intima.getNodes():
			commEdge = comms.getEdge(n1, n2)
			intimaEdge = intima.getEdge(n1, n2)
			if intimaEdge.isValid():
				updatedInt = intimacy[intimaEdge] * exp (-1 * decay)
				if commEdge.isValid() and commDate[commEdge] == t:
					updatedInt += 1 
				intimacy[intimaEdge] = updatedInt
				
def get_membership_strength():
	'''
	(none) => none
	compute the distribution of membership strength
	'''
	run = []
	init_parameters = ['startNodes: ' + str(startNodes), 'edgeWeight:' + str(edgeWeight), 'delta: ' + str(delta), 'beta: ' + str(beta),  'C: ' + str(C)]
	run.append(init_parameters)
	for n in intima.getNodes():
		strength = 0
		for e in intima.getInEdges(n):
			strength += intimacy[e]
			run.append(strength)
	
def write_run(run):
	'''
	(list)=> none 
	write results into a file
	'''			
	with open(dirPath + 'S_i.csv', "wb") as csvFile:
		writer = csv.writer(csvFile, delimiter = ',')
		writer.writerow(run)
					

def main(graph): 
	intimacy = graph.getDoubleProperty('intimacy') # initializing intimacy as a doubleProperty of edges.
	birthDate = graph.getIntegerProperty("birthDate") # initializing date of joining of the node 
	commDate = graph.getDoubleProperty('commDate') # initializing date of communication events
	manager = graph.getBooleanProperty('manager') # initializing the property of community manager
	viewBorderColor = graph.getColorProperty("viewBorderColor")
	viewBorderWidth = graph.getDoubleProperty("viewBorderWidth")
	viewColor = graph.getColorProperty("viewColor")
	viewFont = graph.getStringProperty("viewFont")
	viewFontAwesomeIcon = graph.getStringProperty("viewFontAwesomeIcon")
	viewFontSize = graph.getIntegerProperty("viewFontSize")
	viewLabel = graph.getStringProperty("viewLabel")
	viewLabelBorderColor = graph.getColorProperty("viewLabelBorderColor")
	viewLabelBorderWidth = graph.getDoubleProperty("viewLabelBorderWidth")
	viewLabelColor = graph.getColorProperty("viewLabelColor")
	viewLabelPosition = graph.getIntegerProperty("viewLabelPosition")
	viewLayout = graph.getLayoutProperty("viewLayout")
	viewMetric = graph.getDoubleProperty("viewMetric")
	viewRotation = graph.getDoubleProperty("viewRotation")
	viewSelection = graph.getBooleanProperty("viewSelection")
	viewShape = graph.getIntegerProperty("viewShape")
	viewSize = graph.getSizeProperty("viewSize")
	viewSrcAnchorShape = graph.getIntegerProperty("viewSrcAnchorShape")
	viewSrcAnchorSize = graph.getSizeProperty("viewSrcAnchorSize")
	viewTexture = graph.getStringProperty("viewTexture")
	viewTgtAnchorShape = graph.getIntegerProperty("viewTgtAnchorShape")
	viewTgtAnchorSize = graph.getSizeProperty("viewTgtAnchorSize")
	
	intima = graph.addSubGraph('intimacyGraph') # stores communication events
	comms = graph.addSubGraph('communicationGraph')

	# set parameters values
	
	# initialization parameters
	dirPath = '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/csv_data'
	startNodes = 2 # number of nodes at the beginning of the process
	edgeWeight = 0.1 # assumed initial edge weight	
	
	# iteration parameters
	iterations = 800
	decay = 1/100 # time scale decay as in Kim
	
	# growth parameters
	alpha = 1
	
	# communication decision parameters
	C = 5 # chattiness
	delta = 1 # responsiveness 
	beta = 0.1 # intimacy strength
	
	
	initialize_model(startNodes, edgeWeight)

	for t in range (iterations):
		grow_network()
		
		# this is the main loop to instantiate communications
		
		compute_denominator_P_phi(intima) # I will need this later
		
		for n1 in graph.getNodes():
			if whether(n1) == True: # the user decides whether to communicate
				for n2 in graph.getNodes(): # ... and who to communicate with
					if n2 != n and communicate (n1,n2) == True: 
						newEdge1 = comms.addEdge(n1,n2)
						newEdge2 = intima.addEdge(n1, n2)
						
		update_intimacy() #update the intimacy network
		
		get_membership_strength()
		

