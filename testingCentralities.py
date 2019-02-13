#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 17:19:07 2018

@author: carlos
"""

import networkx as nx
from networkx.algorithms.community.kernighan_lin import kernighan_lin_bisection
from networkx.algorithms import community
import json

import domainConfiguration
import time
import random
import argparse
# import grafica_availability



import os


# from conf import config


def enoughResources(node_,file_):
    
    if domainConfiguration.nodeFreeResources[node_] >= domainConfiguration.filesResources[file_]:
        return True
    else:
        if verbose_: print "FILE DOES NOT FIT IN NODE "+str(node_)
        return False



def weightGraph_(G, sources_):
    
    for edgeId in G.edges:
        if edgeWeight == "propagation":
            G[edgeId[0]][edgeId[1]]['weight']=G[edgeId[0]][edgeId[1]]['PR']
        else:
            G[edgeId[0]][edgeId[1]]['weight']=1
    for edgeId in G.edges:
        for nodeId in sources_:
            if edgeWeight == "propagation":
                dist_e0 = nx.shortest_path_length(G,source=edgeId[0],target=nodeId,weight='PR')
                dist_e1 = nx.shortest_path_length(G,source=edgeId[1],target=nodeId,weight='PR')
            else:
                dist_e0 = nx.shortest_path_length(G,source=edgeId[0],target=nodeId)
                dist_e1 = nx.shortest_path_length(G,source=edgeId[1],target=nodeId)
            dist_small = min(dist_e0,dist_e1)
            G[edgeId[0]][edgeId[1]]['weight']=G[edgeId[0]][edgeId[1]]['weight']+dist_small


#def deprecated_weightGraph_(G, sources_):
#    
#    for edgeId in G.edges:
#        G[edgeId[0]][edgeId[1]]['weight']=0
#    for n in G.nodes:
#        totalDistance = 0
#        for nodeId in sources_:
#            totalDistance = totalDistance + nx.shortest_path_length(G,source=n,target=nodeId)
#        for edgeId in G.edges(n):
#            if G[edgeId[0]][edgeId[1]]['weight']<totalDistance:
#                G[edgeId[0]][edgeId[1]]['weight']=totalDistance





def getRackOrganization(mySources):




    
    G_w = domainConfiguration.G.copy()
    weightGraph_(G_w,mySources)
    
    
#    racks_=asyn_lpa_communities(G, weight='weight')
#    print racks_
    
#    k = domainConfiguration.REPLICATIONFACTOR -1
#    comp = nx.girvan_newman(G_w)
#    limited = itertools.takewhile(lambda c: len(c) <= k, comp)
#    for communities in limited:
#        pass
#    print(tuple(sorted(c) for c in communities)) 


#    racks_= kernighan_lin_bisection(G_w)
#    print racks_
    racks_ = kernighan_lin_bisection(G_w,weight='weight')
#    print racks_
    
    
    return racks_


def initializeResources(domainConfiguration):
    for i in domainConfiguration.G.nodes:
        if i != domainConfiguration.cloudId:
            domainConfiguration.nodeFreeResources[i] = domainConfiguration.nodeResources[i]


def singleReplicaPlacement(domainConfiguration,sorted_files):
    ########
    # POLITICA DE SOLO UN FICHERO SINGLE PLACEMENT DEL FMEC
    ########
    initializeResources(domainConfiguration)
    
    file2NodePlacementMatrixSINGLE = [[0 for j in xrange(len(domainConfiguration.G.nodes))] for i in xrange(domainConfiguration.TOTALNUMBEROFFILES)]
    #[file][node]
     
    for i_f in sorted_files:
        f=i_f[0]
    
        Gs_w = domainConfiguration.G.copy()
        sources_ = list(domainConfiguration.datasourcesRequests[f])
        weightGraph_(Gs_w,sources_)
        singCentr1 = nx.eigenvector_centrality(G=Gs_w,weight='weight',max_iter=1000)
        singCentr1.pop(domainConfiguration.cloudId,None)
        sorted_c = sorted(singCentr1.items(), key=lambda x: x[1], reverse=True)

        i = 0
        while not enoughResources(sorted_c[i][0],f):
            i = i+1
            if i==len(sorted_c):
                break                
        if i<len(sorted_c):
            if verbose_: print "First elegible node is "+str(sorted_c[i][0])
            file2NodePlacementMatrixSINGLE[f][sorted_c[i][0]]=1
            domainConfiguration.nodeFreeResources[sorted_c[i][0]] = domainConfiguration.nodeFreeResources[sorted_c[i][0]] - domainConfiguration.filesResources[f]
            
        else:
            if verbose_: print "ERROR not found any node"

    
    return file2NodePlacementMatrixSINGLE

def replicaAwarePlacement(domainConfiguration,sorted_files):
    ########
    # BEGIN POLITICA DE REPLICA PLACEMENT DEL ARTICULO
    ########
    
    initializeResources(domainConfiguration)
    
    file2NodePlacementMatrix = [[0 for j in xrange(len(domainConfiguration.G.nodes))] for i in xrange(domainConfiguration.TOTALNUMBEROFFILES)]
    #[file][node]

    
    #for f in range(domainConfiguration.TOTALNUMBEROFFILES):
    for i_f in sorted_files:
        f=i_f[0]
    
        #we define the set of data generators and data generators+cloud
    
        eligibleNodes_ = set()
        eligibleNodes_.add(domainConfiguration.cloudId)
        sources_ = list(domainConfiguration.datasourcesRequests[f])
        sourcesAndCloud_=list(sources_)
        sourcesAndCloud_.append(domainConfiguration.cloudId)
        
        racks_ = getRackOrganization(sources_)
        
        if verbose_: print "FILE NUMBER "+str(f)
        
    
        
        #the first selected node is the one with the hightest centrality considereing the data generators and the cloud provider
        
        
        if replicaaware_centrality == "betweenness":
            if edgeWeight == "propagation":
                scentr1 = nx.betweenness_centrality_subset(G=domainConfiguration.G, sources=sourcesAndCloud_, targets=sourcesAndCloud_, normalized=False, weight="PR")
            else:
                scentr1 = nx.betweenness_centrality_subset(G=domainConfiguration.G, sources=sourcesAndCloud_, targets=sourcesAndCloud_, normalized=False, weight=None)
            scentr1.pop(domainConfiguration.cloudId,None)
            sorted_s = sorted(scentr1.items(), key=lambda x: x[1], reverse=True)
        elif replicaaware_centrality == "eigenvector":
            Gs_w = domainConfiguration.G.copy()
            weightGraph_(Gs_w,sourcesAndCloud_)
            singCentr1 = nx.eigenvector_centrality(G=Gs_w,weight='weight')
            singCentr1.pop(domainConfiguration.cloudId,None)
            sorted_s = sorted(singCentr1.items(), key=lambda x: x[1], reverse=True)

        else:
            print "NO SUITABLE CONFIGURATION FOR VARIABLE replicaaware_centrality IN REPLICA AWARE PLACEMENT"
            break
        
        i = 0
        while not enoughResources(sorted_s[i][0],f):
            i = i+1
            if i==len(sorted_s):
                break    
        
        if i<len(sorted_s):
            if verbose_: print "First elegible node is "+str(sorted_s[i][0])
            eligibleNodes_.add(sorted_s[i][0])
            file2NodePlacementMatrix[f][sorted_s[i][0]]=1
            domainConfiguration.nodeFreeResources[sorted_s[i][0]] = domainConfiguration.nodeFreeResources[sorted_s[i][0]] - domainConfiguration.filesResources[f]
            
        else:
            if verbose_: print "ERROR not found any node"
        
        
        #the second and third node are the ones with the highest centrality values from each of the two --racks--
        
        if edgeWeight == "propagation":
            ccentr1 = nx.betweenness_centrality_subset(G=domainConfiguration.G, sources=sources_, targets=sources_, normalized=False, weight="PR")
        else:
            ccentr1 = nx.betweenness_centrality_subset(G=domainConfiguration.G, sources=sources_, targets=sources_, normalized=False, weight=None)
        ccentr1.pop(domainConfiguration.cloudId,None)
        sorted_c = sorted(ccentr1.items(), key=lambda x: x[1], reverse=True)
        
        for r in range(domainConfiguration.NUMBEROFRACKS):
            i = 0
            while (not enoughResources(sorted_c[i][0],f)) or (sorted_c[i][0] in eligibleNodes_) or (not sorted_c[i][0] in racks_[r]) :
                i = i+1
                if i==len(sorted_c):
                    break   
                
            if i<len(sorted_c):
                if verbose_: print "Elegible node for rack "+str(r)+" is "+str(sorted_c[i][0])
                eligibleNodes_.add(sorted_c[i][0])
                file2NodePlacementMatrix[f][sorted_c[i][0]]=1
                domainConfiguration.nodeFreeResources[sorted_c[i][0]] = domainConfiguration.nodeFreeResources[sorted_c[i][0]] - domainConfiguration.filesResources[f]
            else:
                if verbose_: print "ERROR not found any node"
    
    return file2NodePlacementMatrix
    ########
    # END POLITICA DE REPLICA PLACEMENT DEL ARTICULO
    ########


def fogStorePlacement(domainConfiguration,sorted_files,cachedecommunities):

    ########
    # BEGIN POLITICA DE FOGSTORE
    ########
    
    initializeResources(domainConfiguration)
    random.seed(1345)
    
    
    file2NodePlacementMatrixFstr = [[0 for j in xrange(len(domainConfiguration.G.nodes))] for i in xrange(domainConfiguration.TOTALNUMBEROFFILES)]
    #[file][node]
    
    
    if not numNodes in cachedecommunities:
    
        #print "The partition of the network for FogStore starts"
        communities_generator = community.girvan_newman(domainConfiguration.G)
        for i_rep in range(0,domainConfiguration.REPLICATIONFACTOR-1): #getting as much regions as replicas needed
            myPartition = next(communities_generator) 
    
        #print "The partition of the network for FogStore ENDED"
        #print myPartition
        cachedecommunities[numNodes]=myPartition
    else:
        #print "Partition is cached"
        myPartition = cachedecommunities[numNodes]

    distancesWithGateways = {}
    
    
    #for f in range(domainConfiguration.TOTALNUMBEROFFILES):
    
    for i_f in sorted_files:
        f=i_f[0]


        sources_ = list(domainConfiguration.datasourcesRequests[f])
        random.shuffle(sources_)
        
        alphanode=sources_[0]
        
        if not alphanode in distancesWithGateways:
            distancesWithGateways[alphanode] = {}
            for nodeI in domainConfiguration.G.nodes:
                if edgeWeight == "propagation":
                    mylength = nx.shortest_path_length(domainConfiguration.G, source=alphanode, target=nodeI, weight="PR")
                else:
                    mylength = nx.shortest_path_length(domainConfiguration.G, source=alphanode, target=nodeI)
                distancesWithGateways[alphanode][nodeI]=  mylength
                 

        
        for i_rep in range(0,domainConfiguration.REPLICATIONFACTOR):
            
            myregion = myPartition[i_rep]
            mydistances = distancesWithGateways[alphanode]
            
            selectedNode = -1
            minDistance = float('inf')
            for candidateNodeId in myregion:
                if (candidateNodeId == domainConfiguration.cloudId) or enoughResources(candidateNodeId,f):
                    if mydistances[candidateNodeId] < minDistance:
                        minDistance = mydistances[candidateNodeId]
                        selectedNode = candidateNodeId
            if selectedNode == -1:
                file2NodePlacementMatrixFstr[f][domainConfiguration.cloudId]=1
            else:
                file2NodePlacementMatrixFstr[f][selectedNode]=1
                if not (selectedNode == domainConfiguration.cloudId):
                    domainConfiguration.nodeFreeResources[selectedNode] = domainConfiguration.nodeFreeResources[selectedNode] - domainConfiguration.filesResources[f]
                
        
    return file2NodePlacementMatrixFstr        

    
    ########
    # END POLITICA DE FOGSTORE
    ########
    
    
def randomPlacement(domainConfiguration,sorted_files):
    initializeResources(domainConfiguration)
    random.seed(1345)   

   ########
    # BEGIN POLITICA DE REPLICA PLACEMENT ALEATORIA
    ########
    
        
    
    file2NodePlacementMatrixRnd = [[0 for j in xrange(len(domainConfiguration.G.nodes))] for i in xrange(domainConfiguration.TOTALNUMBEROFFILES)]
    #[file][node]
    
    
    #for f in range(domainConfiguration.TOTALNUMBEROFFILES):

    for i_f in sorted_files:
        f=i_f[0]

        
        sorted_rnd = range(0,numNodes)
        random.shuffle(sorted_rnd)
        i = 0
        for i_rep in range(0,domainConfiguration.REPLICATIONFACTOR):
        
            if i==len(sorted_rnd):
                break
            while not enoughResources(sorted_rnd[i],f):
                i = i+1
                if i==len(sorted_rnd):
                    break    
            
            if i<len(sorted_rnd):
                if verbose_: print "First elegible node is "+str(sorted_rnd[i])
                file2NodePlacementMatrixRnd[f][sorted_rnd[i]]=1
                domainConfiguration.nodeFreeResources[sorted_rnd[i]] = domainConfiguration.nodeFreeResources[sorted_rnd[i]] - domainConfiguration.filesResources[f]
                i = i + 1
            else:
                print "ERROR not found any node"
                break

    return file2NodePlacementMatrixRnd            
    
    ########
    # END POLITICA DE REPLICA PLACEMENT ALEATORIA
    ########



   

def allInCloudPlacement(domainConfiguration,sorted_files):

    initializeResources(domainConfiguration)
    random.seed(9999)
    
    
    file2NodePlacementMatrixCld = [[0 for j in xrange(len(domainConfiguration.G.nodes))] for i in xrange(domainConfiguration.TOTALNUMBEROFFILES)]

    for iFile in range(0,domainConfiguration.TOTALNUMBEROFFILES):
        file2NodePlacementMatrixCld[iFile][domainConfiguration.cloudId]=1
    
    return file2NodePlacementMatrixCld


def initTime(s):
    global t
    print s
    t = time.time()

def endTime(s):
    global t
    print "Execution time of:"+str(time.time()-t)
    print s
    t = time.time()
    
def checkAvailability4Sensors(domainConfiguration,file2NodePlacementMatrix,GfailsSensors,nodesFailedSensors):

    mySensorsAvailables = 0
    for f in xrange(domainConfiguration.TOTALNUMBEROFFILES):
        availableFile = True
        for sensor in list(domainConfiguration.datasourcesRequests[f]):
            sensorReach1Replica = False
            for idDevice in xrange(len(domainConfiguration.G.nodes)):
                if file2NodePlacementMatrix[f][idDevice]==1:
                    if idDevice not in nodesFailedSensors:
                        if sensor not in nodesFailedSensors:
                            if nx.has_path(GfailsSensors,sensor,idDevice):
                                sensorReach1Replica = True
            if not sensorReach1Replica: availableFile=False
        if availableFile: mySensorsAvailables = mySensorsAvailables + 1
    return mySensorsAvailables



def checkAvailability4Cloud(numberOfReplicas,domainConfiguration,file2NodePlacementMatrix,GfailsCloud,nodesFailedCloud):

    myCloudAvailables = 0
    for f in xrange(domainConfiguration.TOTALNUMBEROFFILES):
        cloudAvailable = False
        allocatedReplicas = 0
        for idDevice in xrange(len(domainConfiguration.G.nodes)):
            if file2NodePlacementMatrix[f][idDevice]==1:
                if idDevice not in nodesFailedCloud:
                    if nx.has_path(GfailsCloud,idDevice,domainConfiguration.cloudId):
                        cloudAvailable = True
                allocatedReplicas = allocatedReplicas + 1
        if allocatedReplicas < numberOfReplicas:
            cloudAvailable = True
        if cloudAvailable: myCloudAvailables = myCloudAvailables + 1
    return myCloudAvailables


def storeAllocationJson(numberOfReplicas,fileName,domainConfiguration,file2NodePlacementMatrix):
    
    allAlloc = {}
    myAllocationList = list()
    myCloudDeployments = 0
    
    for f in xrange(domainConfiguration.TOTALNUMBEROFFILES):
        replicaId = numberOfReplicas-1
        listofplacements = {}
        for idDevice in xrange(len(domainConfiguration.G.nodes)):
            if file2NodePlacementMatrix[f][idDevice]==1:
                if edgeWeight == "propagation":
                    distance_ = nx.shortest_path_length(domainConfiguration.G,source=idDevice,target=domainConfiguration.cloudId,weight="PR")
                else:
                    distance_ = nx.shortest_path_length(domainConfiguration.G,source=idDevice,target=domainConfiguration.cloudId)
                listofplacements[idDevice]=distance_
        #el orden en el json siempre va desde el que esta mas cerca al que esta mas lejos del cloud, para facilitar la seleccion de la lectura en el simulador
        #ya que a la hora de generar el archivo de los transmissions solo se hace transmission entre el modulo de la primera replica, en el resto nunca
        for key, value in sorted(listofplacements.iteritems(), key=lambda (k,v): (v,k),reverse=True):          
            myAllocation = {}
            myAllocation['app']=str(f)
            myAllocation['module_name']=str(f)+'_'+str(replicaId)
            myAllocation['id_resource']=key
            myAllocation['distance2cloud']=value
            myAllocationList.append(myAllocation)
            replicaId = replicaId -1
            if key == domainConfiguration.cloudId:
                myCloudDeployments = myCloudDeployments + 1
        while replicaId >= 0:
            myAllocation = {}
            myAllocation['app']=str(f)
            myAllocation['module_name']=str(f)+'_'+str(replicaId)
            myAllocation['id_resource']=domainConfiguration.cloudId
            myAllocation['distance2cloud']=0
            myAllocationList.append(myAllocation)
            replicaId = replicaId -1
            myCloudDeployments = myCloudDeployments + 1
        #emplazamos todos los cloud reads en el cloud
        myAllocation = {}
        myAllocation['app']=str(f)
        myAllocation['module_name']='CLOUD_'+str(f)
        myAllocation['id_resource']=domainConfiguration.cloudId
        myAllocationList.append(myAllocation)
        
        
    allAlloc['initialAllocation']=myAllocationList
    
    file = open(fileName,"w")
    file.write(json.dumps(allAlloc))
    file.close()
    
    return myCloudDeployments




if __name__ == '__main__':
    """Main function"""


    #PARAMETERS FROM COMMAND LINE

    # replicaaware_centrality = "eigenvector"
    #replicaaware_centrality = "betweenness"
    #netTopology = "twolevel"
    #netTopology = "onelevel"
    # edgeweight="hopcount"
    # edgeweight="propagation"


    #userLocation = "concentrated" #sensors of the same data type distributed in neighboring gateways
    # userLocation = "dispersed"  #sensors of the same data type distributed uniformemly across all the gateways


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


    #name

    #Experiment configuraiton

    testingSizeExperiment = False

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

    allExperiment = [(100,40)]


    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--work-dir',
        type=str,
        default="",
        help='name of experiment equiv. PATH directory')

    parser.add_argument(
        '--centrality',
        type=str,
        default="eigenvector",
        help='Indicates the centrality index to use in replica-aware placement')

    parser.add_argument(
        '--userlocation',
        type=str,
        default="dispersed",
        help='Indicates the type of distribution for the users/sensors')

    parser.add_argument(
        '--edgeweight',
        type=str,
        default="propagation",
        help='Indicates the type of distribution for the users/sensors')

    parser.add_argument(
        '--topology',
        type=str,
        default="twolevel",
        help='Indicates the type of distribution for the users/sensors')


    args, pipeline_args = parser.parse_known_args()

    replicaaware_centrality = args.centrality
    userLocation = args.userlocation
    edgeWeight = args.edgeweight
    netTopology = args.topology

    datestamp = args.work_dir

    # replicaaware_centrality = config.replicaaware_centrality
    # userLocation = config.userLocation

    
    pathExp =  "experiment_"+datestamp
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




    from shutil import copyfile
    # copyfile("conf/config.py",conffolder+"/config.py") 
    f= open(conffolder+"/config.log","a+")
    f.write("\n\n\n#command line options\n\n")
    f.write("--userlocation " + args.userlocation)
    f.write("\n")
    f.write("--centrality " + args.centrality)
    f.write("\n")
    f.write("--edgeweight " + args.edgeweight)
    f.write("\n")
    f.write("--topology " + args.topology)
    f.close() 



    #allNumFiles = [100]
    #allNumNodes = [50]




    #allNumFiles = [5]
    #allNumNodes = [50]


    file2 = open(csvfolder+"/results.csv","w")

    #cloudDeployments = {}
    #availabilityCloudReads = {}
    #availabilitySensorWrites = {}

    cachedecommunities = {}

    #for numFiles in allNumFiles:
    #    for numNodes in allNumNodes:

    for exp_ in allExperiment:
        numFiles=exp_[0]
        numNodes=exp_[1]

        experimentName = 'f'+str(numFiles)+'-n'+str(numNodes)
        #numFiles=30
        #numNodes = 10
        
        
        #GENERATION OF THE MODEL
        
        print "############"+str(numFiles)+" files and "+str(numNodes)+" nodes##################"
        
        initTime("Generation of the model for "+str(numFiles)+" files and "+str(numNodes)+" nodes")
        
        
        domainConfiguration.initializeRandom(8)
        domainConfiguration.setConfigurations()
        
        domainConfiguration.TOTALNUMBEROFFILES = numFiles
        if netTopology == "twolevel":
            domainConfiguration.func_NETWORKGENERATION = "twolevelBarabasiAlbert("+str(numNodes/numberOfBarabasiAlbertRegions)+","+str(numberOfBarabasiAlbertRegions)+")"
            print "two level barabasi"
        else:
            domainConfiguration.func_NETWORKGENERATION = "nx.barabasi_albert_graph(n="+str(numNodes)+", m=2)"
            print "single barabasi"
        
        
        domainConfiguration.initializeRandom(25)
        domainConfiguration.networkModel(jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+'-')
        domainConfiguration.initializeRandom(133)
        if userLocation == "concentrated":
            print "NEW USER LOCATION - Concentrated"
            domainConfiguration.datasourcesGenerationGeoconcentrated(jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+'-')
        if userLocation == "dispersed":
            print "OLD USER LOCATION - Dispersed"
            domainConfiguration.datasourcesGenerationGeodispersed(jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+'-')
        domainConfiguration.initializeRandom(666)
        domainConfiguration.filesGeneration(jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+'-')
        domainConfiguration.initializeRandom(69)
        domainConfiguration.generateFailuresSensors()
        domainConfiguration.initializeRandom(69)
        domainConfiguration.generateFailuresCloud()        
        
        endTime("")



        ### ORDERING THE FILES WITH THEIR FILE RATES REQUESTS

        fileRatesTotal = {}
        for i in xrange(domainConfiguration.TOTALNUMBEROFFILES):
            fileRatesTotal[i] = 0.0
        
        for i,v in enumerate(domainConfiguration.myDataSources):
            fileRatesTotal[int(v['app'])]=fileRatesTotal[int(v['app'])]+(1.0/float(v['lambda']))

        sorted_files = sorted(fileRatesTotal.items(), key=lambda x: x[1], reverse=True)    
        
        initTime("Placement for the replica algorithm "+str(numFiles)+" files and "+str(numNodes)+" nodes")
        file2NodePlacementMatrix = replicaAwarePlacement(domainConfiguration,sorted_files)
        endTime("")
        
        initTime("Placement for fogstore replica algorithm "+str(numFiles)+" files and "+str(numNodes)+" nodes")
        file2NodePlacementMatrixFstr=fogStorePlacement(domainConfiguration,sorted_files,cachedecommunities)    
        endTime("")

        initTime("Placement for the single file algorithm "+str(numFiles)+" files and "+str(numNodes)+" nodes")
        file2NodePlacementMatrixSINGLE = singleReplicaPlacement(domainConfiguration,sorted_files)
        endTime("")

        initTime("Placement for all in cloud "+str(numFiles)+" files and "+str(numNodes)+" nodes")
        file2NodePlacementMatrixCld = allInCloudPlacement(domainConfiguration,sorted_files)
        endTime("")
        
        
        initTime("Storing placements in JSON files "+str(numFiles)+" files and "+str(numNodes)+" nodes")






        
    #GENERATION OF THE ORDERED FAILED DEVICES FOR WRITING FROM SENSORS TO REPLICAS
        GfailsSensors = domainConfiguration.G.copy()
        nodesFailedSensors = set()    
        numberOfFailures = int(len(GfailsSensors.node)*nodesToFail)
        for i in range(0,numberOfFailures):
        #for i in range(0,nodesToFail):
            if i!=domainConfiguration.cloudId:
                GfailsSensors.remove_node(domainConfiguration.failureOrderSensors[i])
                nodesFailedSensors.add(domainConfiguration.failureOrderSensors[i])

    #GENERATION OF THE ORDERED FAILED DEVICES FOR READING FROM REPLICAS TO CLOUD
        GfailsCloud = domainConfiguration.G.copy()
        nodesFailedCloud = set()    
        numberOfFailures = int(len(GfailsCloud.node)*nodesToFail)
        shiftOfFailures = int(len(GfailsCloud.node)*nodesToFail)
        for i in range(0+shiftOfFailures,numberOfFailures+shiftOfFailures):
        #for i in range(0,nodesToFail):
            if i!=domainConfiguration.cloudId:
                GfailsCloud.remove_node(domainConfiguration.failureOrderSensors[i])
                nodesFailedCloud.add(domainConfiguration.failureOrderSensors[i])
        
        
        
           
        
        mySensorsAvailables=checkAvailability4Sensors(domainConfiguration,file2NodePlacementMatrix,GfailsSensors,nodesFailedSensors)
        mySensorsAvailablesFstr=checkAvailability4Sensors(domainConfiguration,file2NodePlacementMatrixFstr,GfailsSensors,nodesFailedSensors)
        mySensorsAvailablesSingle=checkAvailability4Sensors(domainConfiguration,file2NodePlacementMatrixSINGLE,GfailsSensors,nodesFailedSensors)
        mySensorsAvailablesAllInCloud=checkAvailability4Sensors(domainConfiguration,file2NodePlacementMatrixCld,GfailsSensors,nodesFailedSensors)
        
        
        numberOfReplicas = domainConfiguration.REPLICATIONFACTOR
        myCloudAvailables = checkAvailability4Cloud(numberOfReplicas,domainConfiguration,file2NodePlacementMatrix,GfailsCloud,nodesFailedCloud)
        numberOfReplicas = domainConfiguration.REPLICATIONFACTOR
        myCloudAvailablesFstr = checkAvailability4Cloud(numberOfReplicas,domainConfiguration,file2NodePlacementMatrixFstr,GfailsCloud,nodesFailedCloud)
        numberOfReplicas = 1
        myCloudAvailablesSingle = checkAvailability4Cloud(numberOfReplicas,domainConfiguration,file2NodePlacementMatrixSINGLE,GfailsCloud,nodesFailedCloud)
        numberOfReplicas = 1
        myCloudAvailablesAllInCloud = checkAvailability4Cloud(numberOfReplicas,domainConfiguration,file2NodePlacementMatrixCld,GfailsCloud,nodesFailedCloud)

        
        
        

        ###Storing json for allocation of replica algorithm
        expStringSufix = expSufix["replicaaware"]
        numberOfReplicas = domainConfiguration.REPLICATIONFACTOR
        filePath = jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+"-alloc"+expStringSufix+".json"
        myCloudDeployments = storeAllocationJson(numberOfReplicas,filePath, domainConfiguration, file2NodePlacementMatrix)


        file2.write('cloudDeployments;'+expStringSufix+'-'+experimentName+';'+str(myCloudDeployments)+'\n')
        file2.write('availabilityCloudReads;'+expStringSufix+'-'+experimentName+';'+str(myCloudAvailables)+'\n') 
        file2.write('availabilitySensorWrites;'+expStringSufix+'-'+experimentName+';'+str(mySensorsAvailables)+'\n') 
        file2.flush()



        ###Storing json for allocation of FogStore replica algorithm
        expStringSufix = expSufix["fogstore"]
        numberOfReplicas = domainConfiguration.REPLICATIONFACTOR
        filePath = jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+"-alloc"+expStringSufix+".json"
        myCloudDeploymentsFstr = storeAllocationJson(numberOfReplicas,filePath, domainConfiguration, file2NodePlacementMatrixFstr)


        file2.write('cloudDeployments;'+expStringSufix+'-'+experimentName+';'+str(myCloudDeploymentsFstr)+'\n')
        file2.write('availabilityCloudReads;'+expStringSufix+'-'+experimentName+';'+str(myCloudAvailablesFstr)+'\n') 
        file2.write('availabilitySensorWrites;'+expStringSufix+'-'+experimentName+';'+str(mySensorsAvailablesFstr)+'\n') 
        file2.flush()



        ##Storing json file for single file allocation 
        expStringSufix = expSufix["singlefile"]
        numberOfReplicas = 1
        filePath = jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+"-alloc"+expStringSufix+".json"
        myCloudDeploymentsSingle = storeAllocationJson(numberOfReplicas,filePath, domainConfiguration, file2NodePlacementMatrixSINGLE)


        
        file2.write('cloudDeployments;'+expStringSufix+'-'+experimentName+';'+str(myCloudDeploymentsSingle)+'\n')
        file2.write('availabilityCloudReads;'+expStringSufix+'-'+experimentName+';'+str(myCloudAvailablesSingle)+'\n')
        file2.write('availabilitySensorWrites;'+expStringSufix+'-'+experimentName+';'+str(mySensorsAvailablesSingle)+'\n')
        file2.flush()




        ##Storing json file for all in cloud allocation
        expStringSufix = expSufix["onlycloud"]
        numberOfReplicas = 1
        filePath = jsonfolder+'/f'+str(numFiles)+'n'+str(numNodes)+"-alloc"+expStringSufix+".json"
        myCloudDeploymentsAllInCloud = storeAllocationJson(numberOfReplicas,filePath, domainConfiguration, file2NodePlacementMatrixCld)

       
        file2.write('cloudDeployments;'+expStringSufix+'-'+experimentName+';'+str(myCloudDeploymentsAllInCloud)+'\n')
        file2.write('availabilityCloudReads;'+expStringSufix+'-'+experimentName+';'+str(myCloudAvailablesAllInCloud)+'\n')
        file2.write('availabilitySensorWrites;'+expStringSufix+'-'+experimentName+';'+str(mySensorsAvailablesAllInCloud)+'\n')
        file2.flush()


        endTime("")




    file2.close()

# grafica_availability.generateAvailabilityPlots()



