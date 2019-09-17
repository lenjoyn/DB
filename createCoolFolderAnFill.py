#!/usr/bin/env python
import io
print "importing PyCool ..."
from PyCool import cool,coral
print "done"

FV = cool.FolderVersioning
ST = cool.StorageType



def getFolderDescription( isMultiChannel ):
    if isMultiChannel:
        description = "<timeStamp>run-lumi</timeStamp><addrHeader><address_header service_type=\"71\" clid=\"1238547719\" /></addrHeader><typeName>CondAttrListCollection</typeName>"
    else:
        description = "<timeStamp>run-lumi</timeStamp><addrHeader><address_header service_type=\"71\" clid=\"1238547719\" /></addrHeader><typeName>AthenaAttributeList</typeName>"
    return description



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



def defineFolderSpec( isMultiVersion ):
    recordSpec = cool.RecordSpecification()
    recordSpec.extend( "Offset", ST.Float )

    folderSpec = cool.FolderSpecification( FV.MULTI_VERSION if isMultiVersion else FV.SINGLE_VERSION,
                                           recordSpec )

    recordSpec2 = cool.RecordSpecification()
    recordSpec2.extend( "Noise", ST.Blob64k )

    folderSpec2 = cool.FolderSpecification( FV.MULTI_VERSION if isMultiVersion else FV.SINGLE_VERSION,
                                            recordSpec2 )
    
    return ( folderSpec, folderSpec2 )



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


def createDataBlob():
    import struct

    fmt = '<fdh10sc'
    size = struct.calcsize(fmt)
    
    blob = coral.Blob(size)

    blob.write(struct.pack(fmt, 1.23, 1.35e31, 17, "Hello",'T'))

    return blob


def writeBlobToFolder(folder, data):
    folderTag = "Test-01"


    record = cool.Record(folder.payloadSpecification())

    count = 0    
    for d in data:
        since = (d["since"][0]<<32) + d["since"][1]
        until = (d["until"][0]<<32) + d["until"][1]
        

        record["Noise"] = d["blob"]
        folder.storeObject(since, until, record, 0)
 
        count = count + 1

        if count == 20:
           break


def main():

#svcMgr.IOVDbSvc.dbConnection  = "impl=cool;techno=oracle;schema=ATLAS_COOL_LAR;ATLAS_COOLPROD:OFLP130:ATLAS_COOL_LAR_W:"
#svcMgr.IOVDbSvc.dbConnection  = "sqlite://;schema=gJTowerMap.db;dbname=OFLP200"



    folderlist=["/LAR/Identifier/GTowerSCMap","/LAR/Identifier/JTowerSCMap"]
    folderspec=[]
    tagspec=[]
    for f in folderlist:
        folderspec.append("GTowerSCMap#GTowerSCMapAtlas#"+f)
        tagspec.append("".join(f.split("/"))+"-boohoo")
        print "folderspec:",folderspec[f]," tagspec:",tagspec[f]
        pass


    fileName = "mycool.db"
    folderName = "/Path/To/Offsets"
    #folderName2 = "/Path/To/Blob"
    
    # get db
    db = getOrCreateDB( fileName )
    
    folderSpec, folderSpec2 = defineFolderSpec( isMultiVersion = True )

    folder = getOrCreateFolder ( db = db,
                                 folderName = folderName,
                                 folderSpec = folderSpec,
                                 isMultiChannel = True
                                 )

    #folder2 = getOrCreateFolder ( db = db,
    #                              folderName = folderName2,
    #                              folderSpec = folderSpec2,
    #                              isMultiChannel = False
    #                              )


    print "fill with data"

    data = [ { "since" : (123456,0), "until" : (200000,0), "offset" : [17.5, 4.5] },
             { "since" : (200000,0), "until" : (250000,4), "offset" : [18.4, 3.3] },
             { "since" : (250000,4), "until" : (300000,6), "offset" : [19.3, 2.7] },
             { "since" : (300000,6), "until" : (301000,9), "offset" : [20.2, 1.4, -5.4, -10] },
             ]
#    writeDataToFolder(folder, data)


    blob = createDataBlob()
    data2 = [ { "since" : (100000,0), "until" : (200000,0), "blob" : blob } ]

#    writeBlobToFolder(folder2, data2)


    db.closeDatabase()

    print "Check the data with"
    print "AtlCoolConsole.py 'sqlite://;schema=%s;dbname=CONDBR2'" % fileName
    print ">>> more %s" % folderName
#    print ">>> more %s" % folderName2

if __name__=="__main__":
    main()
