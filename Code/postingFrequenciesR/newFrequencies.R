library (jsonlite)
netFileName <- '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/json/data/2015-11-02-14-08-26/edgesWIntervals.json'
edgesFile <- fromJSON(netFileName)
h <-hist(edgesFile$interval, col='lightblue')
plot (h, log = 'xy', main = "Interval between two consecutive comments")
