import os,json,itertools
from pathlib import Path
import NXOpen,NXOpen.UF
s=NXOpen.Session.GetSession()
u=NXOpen.UF.UFSession.GetUFSession()
out=Path(os.environ["SIEMENS_JOB_DIR"])/"GEOMETRY_REPORT.txt"
if out.exists(): raise RuntimeError("Report exists")
data={"bodies":[],"pairs":[],"errors":[]}
def save(): out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
try:
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/NX_Rollback_Backup_20261023_035742/NX_Automation/Monocoque_EDU_v04.prt")
    if status is not None: status.Dispose()
    data["source"]=p.FullPath
    data["units"]=str(p.PartUnits)
    csys=p.WCS.CoordinateSystem.Tag
    bodies=list(p.Bodies)
    for b in bodies:
        item={"name":b.Name}
        try:
            item["solid"]=b.IsSolidBody
            corner,directions,lengths=u.ModlGeneral.AskBoundingBoxExact(b.Tag,csys)
            item.update({"corner":list(corner),"directions":[list(x) for x in directions],"lengths":list(lengths)})
        except Exception as e: item["error"]=str(e)
        data["bodies"].append(item)
        save()
    for a,b in itertools.combinations(bodies,2):
        item={"a":a.Name,"b":b.Name}
        try: item["distance"]=float(u.ModlGeneral.AskMinimumDist(a.Tag,b.Tag,0,[0.0]*3,0,[0.0]*3)[0])
        except Exception as e: item["error"]=str(e)
        data["pairs"].append(item)
    data["note"]="Zero minimum distance does not distinguish contact from overlap. Model not saved."
except Exception as e:
    data["errors"].append(str(e))
finally: save()
