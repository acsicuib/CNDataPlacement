#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:58:58 2018

@author: carlos
"""

import networkx as nx
import random
import operator
import json






random.seed(8)
verbose_log = False
generatePlots = True
graphicTerminal =False
myConfiguration_ = 'newage'


def mapping(x):
    global delta
    return x+delta

def increaseNodeID(d):
    global delta
    delta = 30
    G=nx.path_graph(5)
    print G.nodes
    print G.edges
    nx.relabel_nodes(G,mapping)



def twolevelBarabasiAlbert(nPartitions,nNodesPerPartition):
    
    
    thePartitions = list()
    theCentralities = list()
    GtotalGraph = nx.Graph()
    for i in range(0,nPartitions):
        Gi = nx.barabasi_albert_graph(n=nNodesPerPartition, m=2)
        centr_ = nx.eigenvector_centrality(G=Gi)
        maxCentr_ = max(centr_.iteritems(), key=operator.itemgetter(1))[0]
        theCentralities.append((i*nNodesPerPartition) +maxCentr_)
        GtotalGraph = nx.disjoint_union(GtotalGraph,Gi)
        thePartitions.append(Gi)
    GtopLevelNet = nx.barabasi_albert_graph(n=nPartitions, m=2)
    
    for idNode in GtopLevelNet.nodes:
        nodeEdges_ = GtopLevelNet.edges(idNode)
        for edges_ in nodeEdges_:
            u = theCentralities[edges_[0]]
            v = theCentralities[edges_[1]]
            GtotalGraph.add_edge(u,v)
            
    return GtotalGraph
    
    

def initializeRandom(seed_):
    random.seed(seed_)


#****************************************************************************************************
#Generacion de la topologia de red
#****************************************************************************************************
def networkModel(filePrefix):
    
    #TOPOLOGY GENERATION
    
    global G
    global nodeResources
    global nodeFreeResources
    global devices
    global gatewaysDevices
    global cloudgatewaysDevices
    global cloudId
    global gatewaysDevicesDistance
    
    
    
    G = eval(func_NETWORKGENERATION)
    #G = nx.barbell_graph(5, 1)
    if graphicTerminal:
        nx.draw(G)
    
   
    devices = list()
    
    nodeResources = {}
    nodeFreeResources = {}
    for i in G.nodes:
        nodeResources[i]=eval(func_NODERESOURECES)
        nodeFreeResources[i] = nodeResources[i]
    
    for e in G.edges:
        G[e[0]][e[1]]['PR']=eval(func_PROPAGATIONTIME)
        G[e[0]][e[1]]['BW']=eval(func_BANDWITDH)
    
    
    #JSON EXPORT
    
    netJson={}
    
    
    for i in G.nodes:
        myNode ={}
        myNode['id']=i
        myNode['HD']=nodeResources[i]
        myNode['RAM']=1
        myNode['IPT']=1
        devices.append(myNode)
    
    
    
    
    myEdges = list()
    for e in G.edges:
        myLink={}
        myLink['s']=e[0]
        myLink['d']=e[1]
        myLink['PR']=G[e[0]][e[1]]['PR']
        myLink['BW']=G[e[0]][e[1]]['BW']
    
        myEdges.append(myLink)
    
    
    #TODO, debería de estar con weight='weight' ??????
    
    
    centralityValuesNoOrdered = nx.betweenness_centrality(G,weight="weight")
    centralityValues=sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)
    
    gatewaysDevices = set()
    cloudgatewaysDevices = set()
    
    highestCentrality = centralityValues[0][1]
    
    for device in centralityValues:
        if device[1]==highestCentrality:
            cloudgatewaysDevices.add(device[0])
    
    gatewaysDevicesDistance = [[0 for col in range(len(G.nodes))] for row in range(len(G.nodes))]
    
    initialIndx = int((1-PERCENTATGEOFGATEWAYS)*len(G.nodes))  #Indice del final para los X tanto por ciento nodos
    
    for idDev in range(initialIndx,len(G.nodes)):
        for idGtw in gatewaysDevices:
            #print " es para el gateway "+str(idGtw)+" y el device "+str(centralityValues[idDev][0])
            mylength = nx.shortest_path_length(G, source=centralityValues[idDev][0], target=idGtw)
            #print mylength
            gatewaysDevicesDistance[centralityValues[idDev][0]][idGtw]=mylength
            gatewaysDevicesDistance[idGtw][centralityValues[idDev][0]]=mylength
        gatewaysDevices.add(centralityValues[idDev][0])
        
    
    
    
    cloudId = len(G.nodes)
    myNode ={}
    myNode['id']=cloudId
    myNode['HD']=CLOUDCAPACITY
    myNode['RAM']=1
    myNode['IPT']=1
    myNode['type']='CLOUD'
    devices.append(myNode)
    
    G.add_node(cloudId)
    
    for cloudGtw in cloudgatewaysDevices:
        myLink={}
        myLink['s']=cloudGtw
        myLink['d']=cloudId
        myLink['PR']=CLOUDPR
        myLink['BW']=CLOUDBW
        

        G.add_edge(cloudId,cloudGtw)
        G[cloudId][cloudGtw]['PR']=CLOUDPR
        G[cloudId][cloudGtw]['BW']=CLOUDBW
    
        myEdges.append(myLink)
    
    
    netJson['entity']=devices
    netJson['link']=myEdges
    
    
    file = open(filePrefix+"network.json","w")
    file.write(json.dumps(netJson))
    file.close()
    





def setConfigurations():

    global CLOUDCAPACITY
    global CLOUDBW
    global CLOUDPR

    global func_NETWORKGENERATION
    global PERCENTATGEOFGATEWAYS
    global func_PROPAGATIONTIME
    global func_BANDWITDH
    global func_NODERESOURECES


    global TOTALNUMBEROFFILES
    global REPLICATIONFACTOR
    global NUMBEROFRACKS
    global func_FILEGENERATION
    global func_FILEMESSAGESIZE
    global func_FILEREADMESSAGESIZE
    global func_FILERESOURCES
    global func_FILEREADRATIO

    global func_USERREQRAT
    global func_REQUESTPROB
    
    
    
    #****************************************************************************************************
    
    #INICIALIZACIONES Y CONFIGURACIONES
    
    #****************************************************************************************************

    
    
    
    
    if myConfiguration_ == 'newage':
    
        #CLOUD
        CLOUDCAPACITY = 9999999999999999  #MB RAM
#        CLOUDBW = 125000 # BYTES / MS --> 1000 Mbits/s
#        CLOUDPR = 1 # MS
        CLOUDBW = 50000 # BYTES / MS --> 1000 Mbits/s
        CLOUDPR = 5 # MS
    
    
        #NETWORK
        PERCENTATGEOFGATEWAYS = 0.25
        func_PROPAGATIONTIME = "random.randint(1,5)" #MS
        func_BANDWITDH = "random.randint(50000,75000)" # BYTES / MS
        func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=10, m=2)" #algorithm for the generation of the network topology
        #func_NODERESOURECES = "random.randint(10,25)" #MB RAM #random distribution for the resources of the fog devices
        func_NODERESOURECES = "random.randint(10,15)" #MB RAM #random distribution for the resources of the fog devices
    
    
        #FILES
        TOTALNUMBEROFFILES = 1
        REPLICATIONFACTOR = 3
        NUMBEROFRACKS = 2
        func_FILEGENERATION = "nx.balanced_tree(r=3,h=1)"
        func_FILEMESSAGESIZE = "random.randint(1500000,4500000)" #BYTES y teniendo en cuenta net bandwidth nos da entre 20 y 60 MS
        func_FILEREADMESSAGESIZE="filesPacketsSize[j]"
        func_FILERESOURCES = "random.randint(1,6)" #MB de ram que consume el servicio, teniendo en cuenta noderesources y appgeneration tenemos que nos caben aprox 1 app por nodo o unos 10 servicios
        func_FILEREADRATIO = "random.random()"
    
        #USERS and IoT DEVICES
        #func_REQUESTPROB="random.random()/4" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_REQUESTPROB="random.random()/2" #Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
        func_USERREQRAT="random.randint(200,1000)"  #MS
    
    
    

def filesGeneration(filePrefix):

    global filesResources
    global filesPacketsSize
    global filesReadPacketsSize
    global filesReadRatio
    
    filesResources = [0 for j in xrange(TOTALNUMBEROFFILES)]
    filesPacketsSize = [0 for j in xrange(TOTALNUMBEROFFILES)]
    filesReadPacketsSize = [0 for j in xrange(TOTALNUMBEROFFILES)]
    filesReadRatio = [0 for j in xrange(TOTALNUMBEROFFILES)]

    appJson = list()
    appJsonSingle = list()
    
    
    for j in range(0,TOTALNUMBEROFFILES):
        filesResources[j]=eval(func_FILERESOURCES)
        filesPacketsSize[j]=eval(func_FILEMESSAGESIZE)
        filesReadPacketsSize[j]=eval(func_FILEREADMESSAGESIZE)
        filesReadRatio[j]=eval(func_FILEREADRATIO)
        
        myApp = {}
        
        myApp['id']=j
        myApp['name']=str(j)
    
        myApp['module']=list()
    
        edgeNumber=0
        myApp['message']=list()
    
        myApp['transmission']=list()


        myAppSingle = {}
        
        myAppSingle['id']=j
        myAppSingle['name']=str(j)
    
        myAppSingle['module']=list()
    
        edgeNumberSingle=0
        myAppSingle['message']=list()
    
        myAppSingle['transmission']=list()

      


        #Anyado la informacion del lector en el cloud
        myNode={}
        myNode['id']=j*(REPLICATIONFACTOR+1)
        myNode['name']='CLOUD_'+str(j)
        myNode['HD']=0
        myNode['type']='CLOUD'
        myApp['module'].append(myNode)

        
        for n in range(0,REPLICATIONFACTOR):
            replicaId = 1+n+j*(REPLICATIONFACTOR+1)
            
            #Anyado la informacion del la replica
            myNode={}
            myNode['id']=replicaId
            myNode['name']=str(j)+'_'+str(n)
            myNode['HD']=filesResources[j]
            myNode['type']='REPLICA'
            myApp['module'].append(myNode)
            if n==0: 
                myNode['id']=1+n+j*(1+1)
                myAppSingle['module'].append(myNode)
            
            #anyado la informacion del mensaje de entrada que vendra del user donde quiera que este y es el mismo para todas las replicas
            myEdge={}
            myEdge['id']=edgeNumber
            edgeNumber = edgeNumber +1
            #myEdge['name']="M.USER.REPLICA."+str(j)+'_'+str(n)
            myEdge['name']="M.USER.APP."+str(j)+'R'+str(n)
            myEdge['s']= "None"
            myEdge['d']=str(j)+'_'+str(n)
            myEdge['instructions']=0
            myEdge['bytes']=filesPacketsSize[j]
            myApp['message'].append(myEdge)
            if n==0:
                edgeNumberSingle = edgeNumberSingle +1
                myEdge['id']=edgeNumberSingle
                myAppSingle['message'].append(myEdge)


            #anyado la informacion del mensaje de salida dela replica que va al cloud
#TODO anyadir informacion de cuantas veces se lee  desde  el (envia al) cloud en funcion del numero de escrituras (llegadas)
            myEdge={}
            myEdge['id']=edgeNumber
            edgeNumber = edgeNumber +1
            myEdge['name']="M.CLOUD.READ."+str(j)+'_'+str(n)
            myEdge['s']= str(j)+'_'+str(n)
            myEdge['d']='CLOUD_'+str(j)
            myEdge['instructions']=0
            myEdge['bytes']=filesReadPacketsSize[j]
            myApp['message'].append(myEdge)
            
            
            if n==0:
                edgeNumberSingle = edgeNumberSingle +1
                myEdge['id']=edgeNumberSingle
                myAppSingle['message'].append(myEdge)
            
            
            #anyado la transmission que genera la llegada de una peticion
            
            myTransmission = {}
            myTransmission['module']=str(j)+'_'+str(n)
            if n==0:
                myTransmission['fractional']=filesReadRatio[j]
            else:
                myTransmission['fractional']=0.0
            #myTransmission['message_in']="M.USER.REPLICA."+str(j)+'_'+str(n)
            myTransmission['message_in']="M.USER.APP."+str(j)+'R'+str(n)
            myTransmission['message_out']="M.CLOUD.READ."+str(j)+'_'+str(n)
            myApp['transmission'].append(myTransmission)

            if n==0:
                myAppSingle['transmission'].append(myTransmission)
            
            #anyado la transmission, aunque no se genera, de cuando un mensaje llega al cloud
            
            myTransmission = {}
            myTransmission['module']='CLOUD_'+str(j)
            myTransmission['message_in']="M.CLOUD.READ."+str(j)+'_'+str(n)
            myApp['transmission'].append(myTransmission)            
            
            if n==0:
                myAppSingle['transmission'].append(myTransmission)     
    
        appJson.append(myApp)
        appJsonSingle.append(myAppSingle)
        
        
    file = open(filePrefix+"appReplica.json","w")
    file.write(json.dumps(appJson))
    file.close()

    file = open(filePrefix+"appSingle.json","w")
    file.write(json.dumps(appJsonSingle))
    file.close()


def datasourcesGenerationGeodispersed(filePrefix):

    #****************************************************************************************************
    #Generacion de los IoT devices (users) que requestean cada aplciacion
    #****************************************************************************************************
    
    
    global myDataSources
    global datasourcesRequests
    
    userJson ={}
    userJsonSingle = {}
    
    
    myDataSources=list()
    myDataSourcesSingle = list()
    
    datasourcesRequests = list()
    for i in range(0,TOTALNUMBEROFFILES):
        datasourcesRequestList = set()
        probOfRequested = eval(func_REQUESTPROB)
        atLeastOneAllocated = False
        for j in gatewaysDevices:
            if random.random()<probOfRequested:
                mylambda=eval(func_USERREQRAT)
                for n in range(0,REPLICATIONFACTOR):
                    myOneDataSource={}
                    myOneDataSource['app']=str(i)
                    myOneDataSource['message']="M.USER.APP."+str(i)+'R'+str(n)
                    myOneDataSource['id_resource']=j
                    myOneDataSource['lambda']=mylambda
                    datasourcesRequestList.add(j)
                    myDataSources.append(myOneDataSource)
                    if n==0: myDataSourcesSingle.append(myOneDataSource)
                    atLeastOneAllocated = True
        if not atLeastOneAllocated:
            j=random.randint(0,len(gatewaysDevices)-1)
            mylambda=eval(func_USERREQRAT)
            for n in range(0,REPLICATIONFACTOR):
                myOneUser={}
                myOneUser['app']=str(i)
                myOneUser['message']="M.USER.APP."+str(i)+'R'+str(n)
                myOneUser['id_resource']=j
                myOneUser['lambda']=mylambda
                datasourcesRequestList.add(j)
                myDataSources.append(myOneUser)
                if n==0: myDataSourcesSingle.append(myOneUser)
        datasourcesRequests.append(datasourcesRequestList)
    
    userJson['sources']=myDataSources
    userJsonSingle['sources']=myDataSourcesSingle
    
    
    file = open(filePrefix+"usersReplica.json","w")
    file.write(json.dumps(userJson))
    file.close()
    
    file = open(filePrefix+"usersSingle.json","w")
    file.write(json.dumps(userJsonSingle))
    file.close()


def WeightedPick(d):
    #print d
    r = random.uniform(0, sum(d.itervalues()))
    s = 0.0
    for k, w in d.iteritems():
        s += w
        if r < s: return k
    return k


def datasourcesGenerationGeoconcentrated(filePrefix):

    #****************************************************************************************************
    #VERSION QUE CONCENTRA LOS REQUESTER EN UNA ZONA DE LA RED
    #****************************************************************************************************

    #****************************************************************************************************
    #Generacion de los IoT devices (users) que requestean cada aplciacion
    #****************************************************************************************************
    
    
    global myDataSources
    global datasourcesRequests
    
    userJson ={}
    userJsonSingle = {}
    
    
    myDataSources=list()
    myDataSourcesSingle = list()
    
    datasourcesRequests = list()
    for i in range(0,TOTALNUMBEROFFILES):
        datasourcesRequestList = set()
        probOfRequested = eval(func_REQUESTPROB)
        
        #The first requester is assigned

        #firstJ=random.randint(0,len(gatewaysDevices)-1)
        firstJ=random.sample(gatewaysDevices,1)[0]
        mylambda=eval(func_USERREQRAT)
        for n in range(0,REPLICATIONFACTOR):
            myOneUser={}
            myOneUser['app']=str(i)
            myOneUser['message']="M.USER.APP."+str(i)+'R'+str(n)
            myOneUser['id_resource']=firstJ
            myOneUser['lambda']=mylambda
            datasourcesRequestList.add(firstJ)
            myDataSources.append(myOneUser)
            if n==0: myDataSourcesSingle.append(myOneUser) 
            
        datasourcesRequests.append(datasourcesRequestList) 
        
        
        firstRequesterDistances = {}
        sumOfDistances = sum(gatewaysDevicesDistance[firstJ])
        
        #print gatewaysDevices
        #print firstJ
        #print "####"
        
        for gi,gv in enumerate(gatewaysDevicesDistance[firstJ]):
            if gv > 0.0:
                firstRequesterDistances[gi]=float(float(1)/float(gv))
        
        total2Select = int(len(gatewaysDevices)*probOfRequested)

        for pending in range(total2Select):
            j = WeightedPick(firstRequesterDistances)
            mylambda=eval(func_USERREQRAT)
            for n in range(0,REPLICATIONFACTOR):
                myOneDataSource={}
                myOneDataSource['app']=str(i)
                myOneDataSource['message']="M.USER.APP."+str(i)+'R'+str(n)
                myOneDataSource['id_resource']=j
                myOneDataSource['lambda']=mylambda
                datasourcesRequestList.add(j)
                myDataSources.append(myOneDataSource)
                if n==0: myDataSourcesSingle.append(myOneDataSource)

        datasourcesRequests.append(datasourcesRequestList)
    
    userJson['sources']=myDataSources
    userJsonSingle['sources']=myDataSourcesSingle
    
    
    file = open(filePrefix+"usersReplica.json","w")
    file.write(json.dumps(userJson))
    file.close()
    
    file = open(filePrefix+"usersSingle.json","w")
    file.write(json.dumps(userJsonSingle))
    file.close()


def generateFailuresSensors():
    
    global failureOrderSensors
    
#    failureOrderSensors = range(0,len(G.nodes))
#    random.shuffle(failureOrderSensors)

    failureOrderSensors=list()
    cent = nx.betweenness_centrality(G=G)
    orderedCent = sorted(cent.items(), key=lambda x: x[1], reverse=True)
    for i in orderedCent:
        failureOrderSensors.append(i[0])


def generateFailuresCloud():
    
    global failureOrderCloud
    
    Gf = G.copy()
    Gf.remove_node(cloudId)
#    failureOrderCloud = range(0,len(Gf.nodes))
#    random.shuffle(failureOrderCloud)

    failureOrderCloud=list()
    cent = nx.betweenness_centrality(G=Gf)
    orderedCent = sorted(cent.items(), key=lambda x: x[1], reverse=False)
    for i in orderedCent:
        failureOrderCloud.append(i[0])





#****************************************************************************************************

#FIN GENERACION MODELO

#****************************************************************************************************



