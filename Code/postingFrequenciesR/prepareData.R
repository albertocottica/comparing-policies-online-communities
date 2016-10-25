library(jsonlite)
dirPath <- '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/raw_json_2016-05-11/json/data/2016-05-11-11-54-09/'
netFileName <- '/Users/albertocottica/Documents/More PhD stuff/MyPhDdata/Thesis Paper 3/Paper 3 Data/raw_json_2016-05-11/json/data/2016-05-11-11-54-09/network.min.json'
netFile <- fromJSON(netFileName, flatten = TRUE)
edges <- netFile ['edges']
realEdges <- t(edges[['edges']]) # transpose fails here
newEdges <- t(realEdges) 
dfEdges <- as.data.frame(newEdges)
realEdges <-NULL #clean up the environment
newEdges <-cbind(newEdges, 0) # add a column for interval
colnames(newEdges)[7] <- c('interval')

latestComments <- list() # structured like a Python dictionary
for (i in length(edges))
{
  user <- newEdges[i, 'source']
  ts <- strtoi(newEdges[i, 'ts'])
  if (exists(user, where = latestComments) == FALSE)
  {
    latestComments[user[1]] <- ts
  }
  else
{
  thisCommentTs <- strtoi(newEdges[i, 'ts'])
  latestCommentTS <- strtoi(latestComments[user])
  newEdges[i, 'interval'] <- thisCommentTs - latestCommentTS
}
}
  

  
  