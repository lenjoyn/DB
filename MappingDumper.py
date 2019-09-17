from ROOT import TFile,TH1F,TCanvas,TTree
import json

# Load the tree & event
f = TFile("myOutputFile.root")
f.ls("*tree*")
tree = f.Get("map_tree")
ievt = tree.GetEntry(0)

# start to treat the jtower map
jSCs =  getattr(tree,"jtower_map")
jSC_map_json = {}
for iJ  in range(0,len(jSCs)):
   jSC_map = [] 
   for iSC in range(0,len(jSCs[iJ])):
       jSC_map.append(json.dumps(jSCs[iJ][iSC]))

   jSC_map_json[iJ] = tuple(jSC_map)

# start to treat the gtower map
gSCs =  getattr(tree,"gtower_map")
gSC_map_json = {}
for iG  in range(0,len(gSCs)):
   gSC_map = []
   for iSC in range(0,len(gSCs[iG])):
       gSC_map.append(json.dumps(gSCs[iG][iSC]))

   gSC_map_json[iG] = tuple(gSC_map)



json_map = {}
json_map["jTowerSCMap"] = jSC_map_json
json_map["gTowerSCMap"] = gSC_map_json
with open('map.json', 'w') as outfile:
    json.dump(json_map, outfile)
    
