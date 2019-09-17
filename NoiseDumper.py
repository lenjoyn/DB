#Getting the noise input
from ROOT import TFile,TH1F,TCanvas,TTree
f = TFile("noise_r10684_MapFixed.root")
jT_h = f.Get("jT_noise");
jNbins=jT_h.GetSize()-1;
gT_h = f.Get("gT_noise");
gNbins=gT_h.GetSize()-1;

#get numbers into json format

json_jT = {}
import json
for x in range(1,jNbins):
   noise=jT_h.GetBinContent(x)
   json_jT[x] = json.dumps(noise)

json_gT={}
import json
for x in range(1,gNbins):
   noise=gT_h.GetBinContent(x)
   json_gT[x] = json.dumps(noise)

json_noise={}
json_noise["jT_noise"]=json_jT
json_noise["gT_noise"]=json_gT

#output json file
with open('data.json', 'w') as outfile:
    json.dump(json_noise, outfile)
