import json
import csv


dirPath = '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/raw_json_2016-05-11/json/data/2016-05-11-11-54-09/'

with open(dirPath + 'network.min.json') as jsonFile:
	jsonData = json.load(jsonFile)

edges = jsonData ['edges']
sortedEdges = sorted(edges, key = lambda k:k['ts'])

latestComments = {}
for i in range(len(sortedEdges)):
	user = str(sortedEdges[i]['source'])
	ts = int(sortedEdges[i]['ts'])
	if user in latestComments:
		previousComment = latestComments[user]
		sortedEdges[i]['interval'] = ts - latestComments[user]
	else:
		sortedEdges[i]['interval'] = 0
	latestComments[user] = ts #update

with open (dirPath + 'edgesWIntervals.json', 'w') as outfile:
	json.dump(sortedEdges, outfile)
	
with open (dirPath + 'edgesWIntervals.csv', 'w') as csvfile:
	fieldnames = sortedEdges[0].keys()
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	for row in sortedEdges:
		writer.writerow(row)
