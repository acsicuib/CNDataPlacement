#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 19:05:47 2019

@author: carlos
"""
import time
import os



#PARAMETERS FROM COMMAND LINE


cloud_location = "inthemiddleofthenight" #en nodos en medio de la topologa, con alto centrality
cloud_location = "countryside" #en nodos alejados de las posiciones centrales, bajo cnetrality

replicaaware_centrality = "eigenvector"
#replicaaware_centrality = "betweenness"

netTopology = "twolevel"
#netTopology = "onelevel"


#edgeweight="hopcount"
edgeweight="propagation"


#userLocation = "concentrated" #sensors of the same data type distributed in neighboring gateways
userLocation = "dispersed"  #sensors of the same data type distributed uniformemly across all the gateways


#PURE CONFIG PARAMETERS

#fogstore #random #replicaaware #onlycloud #singlefile
placements = ["fogstore","random","replicaaware","onlycloud","singlefile"]
expSufix = {}
expSufix["fogstore"] = "FstrRep"
expSufix["replicaaware"] = "Replica"
expSufix["onlycloud"] = "Cloud"
expSufix["singlefile"] = "Single"


verbose_=False
nodesToFail = 0.1
numberOfBarabasiAlbertRegions = 5


#DIRECTORY STRUCUTRE

# datestamp = time.strftime('%Y%m%d_%H%M%S')

#TODO

pathExp =  "experiment_"+"XXX"
if not os.path.exists(pathExp): os.makedirs(pathExp)
datafolder = pathExp +"/data"
if not os.path.exists(datafolder): os.makedirs(datafolder)
jsonfolder = datafolder +"/json"
if not os.path.exists(jsonfolder): os.makedirs(jsonfolder)
csvfolder = datafolder +"/csv"
if not os.path.exists(csvfolder): os.makedirs(csvfolder)
imgfolder = datafolder +"/img"
if not os.path.exists(imgfolder): os.makedirs(imgfolder)
conffolder = pathExp +"/conf"
if not os.path.exists(conffolder): os.makedirs(conffolder)



#Experiment configuraiton

testingSizeExperiment = True

allNumFiles1 = range(10,101,10)
allNumNodes1 = [50]
allNumFiles2 = [100]
allNumNodes2 = range(20,201,20)

allExperiment = list()
for i in allNumFiles1:
    for j in allNumNodes1:
        allExperiment.append((i,j))
for i in allNumFiles2:
    for j in allNumNodes2:
        allExperiment.append((i,j))


if testingSizeExperiment:
    allExperiment = [(100,40)]