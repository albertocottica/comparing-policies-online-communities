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
	membershipStrength = graph.getDoubleProperty('membershipStrength') # initializing the membership strength property of nodes
	lastComm = graph.getDoubleProperty('lastCom') # only for debugging, later to be deleted
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
	dirPath = '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/'
	startNodes = 2 # number of nodes at the beginning of the process
	edgeWeight = 0.1 # assumed initial edge weight	
	
	# iteration parameters
	iterations = 700
	decay = 1/float(100) # time scale decay as in Kim
	
	# growth parameters
	alpha = 1
	
	# communication decision parameters
	C = 0.05 # chattiness
	delta = 1 # responsiveness 
	beta = 10 # intimacy strength	
	
	# policy parameters
	onboarding = False
	engagement = True

	nRun = 1 # number of runs
	allRuns = []
	for j in range (nRun):
		print ('Run ' + str (j))
		
		tracker = [] # tracker accumulator
	
		# initialize the network
	
		intima = graph.addSubGraph('intimacyNetwork' + str(j))
		comms = graph.addSubGraph('communicationsNetwork' + str (j))

		# add the community manager
		commManager = intima.addNode()
		manager[commManager] = True
		birthDate[commManager] = 0 
		comms.addNode(commManager)
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
			if onboarding == True:
				onboardEdge = comms.addEdge(commManager, newNode)
			# for now I am not adding comm events before time 0
		
		# main loop starts here
		
		for  t in range (int(startNodes +1), iterations): # replace 2 with iterations after testing
			
			# grow the network. 
			for i in range (alpha): # need to account for alpha < 1
				newNode = intima.addNode()
				comms.addNode(newNode)
				birthDate[newNode] = t 
				manager[newNode] = False
				if onboarding == True: # Onboarding goes here.
					onBoardEdge = comms.addEdge(commManager, newNode)
	
			# Decide whether node will engage in communication.
			# find out whether node had incoming communication at time t-1
			# iterate over previous comm event	for n in comms.getNodes():
	
			for n in comms.getNodes():
				if manager[n] == True:
					if engagement == True:
						for e in comms.getEdges():
							if commDate[e] == t-1: # find the communication events from last period
								engage = comms.addEdge(n, comms.source(e)) # ... and reach out to people that initaited the, 
				else: 
					xcm = 0 # initialize the counters of incoming comments
					xu = 0 
					for e in comms.getInEdges(n):
						if commDate[e] == t-1:
							if manager [comms.source(e)] == True:
								xcm += 1 
							else:
								xu += 1
					prob = compute_probability(C, xcm, xu)
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
									newEdge1 = comms.addEdge(n,n2)
									commDate[newEdge1] = t
									if edge1 == None: # if no intimacy edge exists (no previous communication), I must add it
										newEdge2 = intima.addEdge(n, n2)
										intimacy [newEdge2] = 1
										lastComm[newEdge2] = t
									else:
										intimacy[edge1] += 1
										lastComm[edge1] = t
								
		
			# update the intimacy network based on the discount factor
			for e in intima.getEdges():
				intimacy[e] = intimacy[e] / (1 + decay) # di
	#			print ('intimacy = ' + str (intimacy[e]))
	#			print (updateInt)
	
		# finally, get membership strength distribution and save to the accumulator. This is now INSIDE the time loop! 

			for n in intima.getNodes():
				item = {}
				item['node'] = birthDate[n]
				item['t'] = t
				mS = 0
				for e in intima.getInEdges(n):
					mS += intimacy[e]
				item['S'] = mS	
				tracker.append(item)
#	tlp.saveGraph(graph, dirPath + 'Tulip_data/20run_2founders_C05_beta10.tlp')
	
	csvFileName = dirPath + 'csv_data/' + 'tracking_' + str(startNodes) + 'founders_C' + str(C) + '_beta' + str(beta) + '_onb' + str(onboarding) + '_eng' + str(engagement) + '.csv'
	with open(csvFileName, 'w') as csvfile:
		fieldnames = ['node','t', 'S']
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		for item in tracker: # needs to be checked out!!!!
			writer.writerow(item)	
	runTime = (time.time() - startTime)/60
	print ('Runtime: ' + str (runTime) + ' minutes')
