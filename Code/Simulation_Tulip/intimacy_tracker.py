# BEFORE RUNNING: run equalValue on a comms graph by the commsDate edge property. 
# Adjust t so that the subgraphs are taken in the right order, starting from 
# commDate[e] = 0

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
import csv

# the updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# the pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the "Run script " button.

# the runGraphScript(scriptFile, graph) function can be called to launch another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call (in the form [a-zA-Z0-9_]+.py)

# the main(graph) function must be defined 
# to run the script on the current graph

def main(graph): 
	birthDate = graph.getIntegerProperty("birthDate")
	commDate = graph.getDoubleProperty("commDate")
	intimacy = graph.getDoubleProperty("intimacy")
	lastCom = graph.getDoubleProperty("lastCom")
	manager = graph.getBooleanProperty("manager")
	membershipStrength = graph.getDoubleProperty("membershipStrength")
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

	comms = graph.getSubGraph('communicationsNetwork10')	# or any other
	dirPath = '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/'
	decay = 1/float(100)

	dataset = []
	strengthMap = {}
	for n in comms.getNodes():
		strengthMap[n] = 0 # storing last values of s
	for t in range (41, 718):
		period = comms.getSubGraph(t)
		
		for n in period.getNodes():
			s = strengthMap[n] / (1 + decay) # at the beginning of each period run time decay 
			for e in period.getInEdges(n):
				s += 1
			item = {}
			item['user'] = birthDate[n]
			item['t'] = t-43
			item['s'] = s
			dataset.append(item)
			strengthMap[n] = s # update the map

	
	with open (dirPath + 'csv_data/intimacyTimeProfiles.csv', 'w') as csvfile:
		fieldnames = ['user', 't', 's']
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		for item in dataset:
			writer.writerow(item)
