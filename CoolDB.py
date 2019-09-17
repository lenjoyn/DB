#!/usr/bin/env python
import io
print "importing PyCool ..."
from PyCool import cool,coral
print "import json"
import json
import time

print "done"

FV = cool.FolderVersioning
ST = cool.StorageType




# Define the folder
def getFolderDescription(isMultiChannel ):
    if isMultiChannel:
        description = "<timeStamp>run-lumi</timeStamp><addrHeader><address_header service_type=\"71\" clid=\"1238547719\" /></addrHeader><typeName>CondAttrListCollection</typeName>"
    else:
        description = "<timeStamp>run-lumi</timeStamp><addrHeader><address_header service_type=\"71\" clid=\"1238547719\" /></addrHeader><typeName>AthenaAttributeList</typeName>"
    return description


# Create the .db file to import to COOL
def getOrCreateDB ( filename ):

    # get database service and name
    dbSvc=cool.DatabaseSvcFactory.databaseService()
    dbstring="sqlite://;schema=%s;dbname=CONDBR2" % filename
    readonly = False # need to write to DB

    try:
        db=dbSvc.openDatabase ( dbstring, readonly)
        print "Opened database",dbstring
    except Exception,e:
        # create db
        db=dbSvc.createDatabase(dbstring)
        print "Created database",dbstring

    print "The db content can be checked using\nAtlCoolConsole.py '" + dbstring + "'"
    return db

def defineFolderSpecTypeName( Name, Type, isMultiVersion ):
    recordSpec = cool.RecordSpecification()
#    recordSpec.extend( "Maps", ST.Float )
    recordSpec.extend( Name, Type )
    folderSpec = cool.FolderSpecification( FV.MULTI_VERSION if isMultiVersion else FV.SINGLE_VERSION,
                                           recordSpec )


    return ( folderSpec )

def getOrCreateFolder (db, folderName, folderSpec, isMultiChannel ):
    if db.existsFolder(folderName):
        print "Folder %s exists already" % folderName
        folder = db.getFolder ( folderName )
        return folder

    # since it doesn't exist, create it
    createParents = True
    folder = db.createFolder( folderName, folderSpec,
                              getFolderDescription( isMultiChannel ),
                              createParents )

    print "Folder '%s' was created" % folderName
    return folder




def writeDataToFolder(folder, data):
    folderTag = "Test-01"

    for d in data:
        since = (d["since"][0]<<32) + d["since"][1]
        until = (d["until"][0]<<32) + d["until"][1]
        print "since: ",since," until:",until
        for (ch, v) in enumerate(d["offset"]):
            record = cool.Record(folder.payloadSpecification())
            record["Offset"] = v
            folder.storeObject(since, until, record, ch, folderTag)


def createDataBlob(data):
    blob = coral.Blob(len(data))
    for ientry in data:
        blob.write(ientry)

    return blob


def writeBlobToFolder(recordName,folder, data):
    folderTag = "Test-01"

    count = 0

    record = cool.Record(folder.payloadSpecification())
    for d in data:
        
        since = (d["since"][0]<<32) + d["since"][1]  
        until = (d["until"][0]<<32) + d["until"][1]
       
        #print count
        record[recordName] = d["blob"]
        count = count + 1
        folder.storeObject(since, until, record, count)

def main():



    with open('noise.json') as json_data:
         noise = json.load(json_data)


    # get db
    noise_db = getOrCreateDB("mynoise.db")

    noise_folderSpec = defineFolderSpecTypeName( "Noise",ST.Blob64k,isMultiVersion = True )

    # JFex Noise folder
    jfolder = getOrCreateFolder ( db = noise_db,
                                 folderName = "/L1Calo/JFex/Noise",
                                 folderSpec = noise_folderSpec,
                                 isMultiChannel = True
                                 )

    # GFex Noise folder
    gfolder = getOrCreateFolder ( db = noise_db,
                                 folderName = "/L1Calo/GFex/Noise",
                                 folderSpec = noise_folderSpec,
                                 isMultiChannel = True
                                 )

    # writing Noise to data in the format of blob 
    jT_blob = createDataBlob(noise["jT_noise"])
    gT_blob = createDataBlob(noise["gT_noise"])

    # Time stamp: since Dec 31, 2015 until Dec 31, 2023  
    since = int(time.mktime(time.strptime('Dec 31, 2015 @ 20:02:58 UTC', '%b %d, %Y @ %H:%M:%S UTC')))
    until = int(time.mktime(time.strptime('Dec 31, 2023 @ 20:02:58 UTC', '%b %d, %Y @ %H:%M:%S UTC')))

 
    # make the data format and dump into .db file
    jdata = [ { "since" : (since,0), "until" : (until,0), "blob" : jT_blob } ]
    writeBlobToFolder("Noise",jfolder, jdata)
    gdata = [ { "since" : (since,0), "until" : (until,0), "blob" : gT_blob } ]
    writeBlobToFolder("Noise",gfolder, gdata)



    with open('map.json') as json_data:
         FexMap = json.load(json_data)

    map_db = getOrCreateDB("mymap.db")

    map_folderSpec = defineFolderSpecTypeName( "Map", ST.Blob16M, isMultiVersion = True )


    # JMap Noise folder
    jMap_folder = getOrCreateFolder ( db = map_db,
                                      folderName = "/L1Calo/JFex/Map",
                                      folderSpec = map_folderSpec,
                                      isMultiChannel = True
                                     )

    # GMap Noise folder
    gMap_folder = getOrCreateFolder ( db = map_db,
                                      folderName = "/L1Calo/GFex/Map",
                                      folderSpec = map_folderSpec,
                                      isMultiChannel = True
                                     )
    jMap_data = []
    for ientry in FexMap["jTowerSCMap"]:
        jMap_blob = createDataBlob(ientry)
        jMap_dict = {"since":(since,0), "until":(until,0), "blob": jMap_blob}
        jMap_data.append(jMap_dict)

    writeBlobToFolder("Map", jMap_folder, jMap_data)

    gMap_data = []
    for ientry in FexMap["gTowerSCMap"]:
        gMap_blob = createDataBlob(ientry)
        gMap_dict = {"since":(since,0), "until":(until,0), "blob": gMap_blob}
        gMap_data.append(gMap_dict)

    writeBlobToFolder("Map", gMap_folder, gMap_data)

if __name__=="__main__":
    main()
