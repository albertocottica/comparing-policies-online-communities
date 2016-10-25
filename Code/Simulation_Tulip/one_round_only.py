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
	
	# set parameters values
	
	# initialization parameters
	dirPath = '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/csv_data'
	startNodes = 2 # number of nodes at the beginning of the process
	edgeWeight = 0.1 # assumed initial edge weight	
	
	# iteration parameters
	iterations = 800
	decay = 1 / float(100) # time scale decay as in Kim
	
	# growth parameters
	alpha = 1
	
	# communication decision parameters
	C = 0.1 # chattiness
	delta = 1 # responsiveness 
	beta = 0.1 # intimacy strength	

	
	# one round of the main loop
	intima = graph.getSubGraph('intimacyNetwork')
	comms = graph.getSubGraph('communicationsNetwork')
	
	for  t in range (int(startNodes +10), int(startNodes + 20)): # replace 2 with iterations after testing
		
		# grow the network
		for i in range (alpha): # need to account for alpha < 1
			newNode = intima.addNode()
			comms.addNode(newNode)
			birthDate[newNode] = t 
			manager[newNode] = False
			
		# compute the denominator of equation 3 in the preliminary note for graph1 (intimacy graph).
		# This is identical for all nodes at any given t.
		denominator = t
		for n1 in intima.getNodes():
			for n2 in intima.getNodes():
				edge1 = findEdge (n1,n2, intima, True, False)
				edge2 = findEdge (n2,n1, intima, True, False)
				if edge1 != None and edge2 != None and n1 != n2:
					denominator += 1 + beta * intimacy[edge1] * intimacy[edge2] 	
		print ('Denominator = ' + str (denominator))


		# Decide whether node will engage in communication.
		# find out whether node had incoming communication at time t-1
		# iterate over previous comm event	for n in comms.getNodes():
		xcm = 0 # intialize the counters of incoming comments
		xu = 0 
		for n in comms.getNodes():
			if manager[n] == False:
				for e in comms.getInEdges(n):
					if commDate[e] == t-1:
						if manager [comms.source(e)] == True:
							xcm += 1 
						else:
							xu += 1
				prob = compute_probability(C, xcm, xu)
				print (prob)
				if random() < prob:
					print ('Node ' +  str(birthDate[n]) + ' engages at time ' + str(t))
					
					# Now the node has decided to engage in communication, it needs to decide who with. 
					for n2 in graph.getNodes(): # ... and who to communicate with
						numerator = 1 
						if n2 != n:
							edge1 = findEdge(n, n2, intima, True, False)
							edge2 = findEdge(n2, n, intima, True, False)
							if edge1 != None and edge2 != None:
								numerator = (1 + beta * intimacy[edge1] * intimacy[edge2]) 
							probComm = numerator/denominator
							
							print ('Node ' + str(birthDate[n]) + ' communicates with ' + str(birthDate[n2]) + ' with probability ' + str (probComm))
							
							if random() < probComm: 
								newEdge1 = comms.addEdge(n1,n2)
								newEdge2 = intima.addEdge(n1, n2)
								commDate[newEdge1] = t
	
		# update the intimacy network based on communication events at t and the discount factor
		for e in intima.getEdges():
			updateInt = intimacy[e] 
			updateInt = updateInt * exp(-1 * decay)			
			source = intima.source(e)
			target = intima.target(e)
			commsEdge = findEdge(source, target, comms, True, False)
			if commsEdge != None:
				updateInt += 1
			intimacy[e] = updateInt
			print ('intimacy = ' + str (intimacy[e]))
			print (updateInt)
		
