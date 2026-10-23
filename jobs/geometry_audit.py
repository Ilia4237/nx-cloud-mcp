import os,json,itertools
from pathlib import Path
import NXOpen
import NXOpen.UF
s=NXOpen.Session.GetSession()
u=NXOpen.UF.UFSession.GetUFSession()
p,load=s.Parts.Open("C:/Users/bobri/NX_Rollback_Backup_20261023_035742/NX_Automation/Monocoque_EDU_v04.prt")
if load is not None: load.Dispose()
data={"source":p.FullPath,"units_enum":str(p.PartUnits),"bodies":[],"pairs":[],"expressions":[]}
bodies=list(p.Bodies)
for b in bodies:
    box=list(u.Modl.AskBoundingBox(b.Tag))
    data["bodies"].append({"name":b.Name,"solid":b.IsSolidBody,"box":box,"size":[box[i+3]-box[i] for i in range(3)],"faces":len(b.GetFaces()),"edges":len(b.GetEdges())})
for a,b in itertools.combinations(bodies,2):
    entry={"a":a.Name,"b":b.Name}
    try:
        entry["minimum_distance"]=float(u.Modl.AskMinimumDist(a.Tag,b.Tag,0,[0.0]*3,0,[0.0]*3)[0])
    except Exception as e:
        entry["error"]=str(e)
    data["pairs"].append(entry)
for e in p.Expressions:
    data["expressions"].append({"name":e.Name,"formula":e.RightHandSide})
out=Path(os.environ["SIEMENS_JOB_DIR"])/"MONOCOQUE_GEOMETRY_AUDIT.txt"
if out.exists(): raise RuntimeError("Report already exists")
out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("GEOMETRY_AUDIT_SAVED; no model save; zero distance does not distinguish contact from overlap")
