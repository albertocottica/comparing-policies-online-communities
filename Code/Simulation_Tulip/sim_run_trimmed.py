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
import time
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
	(float, int, int) => float
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
	membershipStrength = graph.getDoubleProperty('membershipStrength') # initializing the membership strength property of nodes
	lastComm = graph.getDoubleProperty('lastCom') # only for debugging, later to be deleted
	xUNow = graph.getIntegerProperty('xUNow') # stores number of incoming comments from non community manager at time t-1
	xUNext = graph.getIntegerProperty('xUNext') # stores number of incoming comments from non community manager at time t	
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
	
	startTime = time.time()
	# set parameters values
	
	# initialization parameters
	dirPath = '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/csv_data/'
	startNodes = 2 # number of nodes at the beginning of the process
	edgeWeight = 0.1 # assumed initial edge weight	
	
	# iteration parameters
	iterations = 700
	decay = 1/float(100) # time scale decay as in Kim
	
	# growth parameters
	alpha = 1
	
	# communication decision parameters
	C = 0.1 # chattiness
	delta = 1 # responsiveness 
	beta = 20 # intimacy strength	
	
	# initialize the network
	
	intima = graph.addSubGraph('intimacyNetwork')
	for i in range(1, int(startNodes+1) ):
		newNode = intima.addNode()
		birthDate[newNode] = i
		manager[newNode] = False
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
	
	# main loop starts here
	
	for  t in range (int(startNodes +1), iterations): # replace 2 with iterations after testing
		print ('Iteration ' + str (t))
		
		# grow the network
		for i in range (alpha): # need to account for alpha < 1
			newNode = intima.addNode()
			birthDate[newNode] = t 
			manager[newNode] = False

		# Decide whether node will engage in communication.
		# find out whether node had incoming communication at time t-1
		# iterate over previous comm event	for n in comms.getNodes():

		for n in intima.getNodes():
			if manager[n] == False:
				xu = xUNow[n] # pull in the number of comments at time t-1
				xcm = 0 
				prob = compute_probability(C, xcm, xu)
				# reset to zero 
#				print (str(birthDate[n]) + ': ' + str(prob))
				if random() < prob:		
#					print (str(birthDate[n]) +  ' engages')			
					# Now the node has decided to engage in communication, it needs to decide who with. 
					# start by computing the denominator
					denominator = t
					for n2 in intima.getNodes():
						if n2 != n:
							edge1 = findEdge(n, n2, intima, True, False)
							edge2 = findEdge(n2, n, intima, True, False)
							if edge1 != None and edge2 != None:
								denominator += beta * intimacy[edge1] * intimacy [edge2]
					# now the numerators and probabilities
					for n2 in intima.getNodes(): 
						numerator = 1 
						if n2 != n:
							edge1 = findEdge(n, n2, intima, True, False)
							edge2 = findEdge(n2, n, intima, True, False)
							if edge1 != None and edge2 != None: # if no edge exists, the numerator is equal to 1
								numerator = (1 + beta * intimacy[edge1] * intimacy[edge2]) 
							probComm = numerator/float(denominator)
#							print (str(birthDate[n]) + ' ' + str(birthDate[n2]) + ' ' + str(probComm))
							if random() < probComm: # toss the biased coin. In this case communication happens
#								print ('Node ' + str(birthDate[n]) + ' communicates with ' + str(birthDate[n2]))
								xUNext[n2] += 1
								if edge1 == None: # if no intimacy edge exists (no previous communication), I must add it
									newEdge2 = intima.addEdge(n, n2)
									intimacy [newEdge2] = 1
									lastComm[newEdge2] = t
								else:
									intimacy[edge1] += 1
									lastComm[edge1] = t
			# update xUNow and reset xUNext
				for n in intima.getNodes():
					xUNow[n] = xUNext[n]
					xUNext[n] = 0 
							
	
		# update the intimacy network based on the discount factor
		for e in intima.getEdges():
			intimacy[e] = intimacy[e] * exp(-1 * decay)
#			print ('intimacy = ' + str (intimacy[e]))
#			print (updateInt)

	# finally, get membership strength distribution and save to CSV 
	thisRun = []
	for n in intima.getNodes():
		item = {}
		mS = 0
		row = []
		for e in intima.getInEdges(n):
			mS += intimacy[e]
		membershipStrength[n] = mS
		item['S'] = mS
		item['t'] = birthDate[n]
		thisRun.append(item)
	with open(dirPath + '1run_100founders_C1_beta20.csv', 'w') as csvfile:
		fieldnames = ['t', 'S']
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		for item in thisRun:
			writer.writerow(item)	
	runTime = (time.time() - startTime)/60
	print ('Runtime: ' + str (runTime) + ' minutes')
