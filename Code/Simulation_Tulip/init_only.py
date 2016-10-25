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
from random import random # uniform distribution! 
from math import exp

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
	
	return C + betaxcm + betaxu 
	
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

	for n in graph.getNodes():
		print n
	
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
	C = 0.05 # chattiness
	delta = 1 # responsiveness 
	beta = 0.1 # intimacy strength	
	
	# initialize the network
	
	intima = graph.addSubGraph('intimacyNetwork')
	comms = graph.addSubGraph('communicationsNetwork')
	for i in range(1, int(startNodes+1) ):
		newNode = comms.addNode()
		intima.addNode(newNode)
		birthDate[newNode] = i
		manager[newNode] = False
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
	birthDate[commManager] = 0 
	comms.addNode(commManager)
	
	for n in graph.getNodes():
		print n
