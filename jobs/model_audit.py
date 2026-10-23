import os,json
from pathlib import Path
import NXOpen
s=NXOpen.Session.GetSession()
r=Path(os.environ["SIEMENS_JOB_DIR"])
out=r/"MONOCOQUE_MODEL_AUDIT.json"
if out.exists():
    raise RuntimeError("Report already exists")
p,status=s.Parts.Open("C:/Users/bobri/NX_Rollback_Backup_20261023_035742/NX_Automation/Monocoque_EDU_v04.prt")
if status is not None:
    status.Dispose()
if p is None:
    raise RuntimeError("Part not loaded")
def info(obj):
    return {"name":getattr(obj,"Name",""),"type":type(obj).__name__}
data={"source":p.FullPath,"units":str(p.PartUnits),"bodies":[info(x) for x in p.Bodies],"features":[info(x) for x in p.Features],"expressions":[],"components":[]}
for x in p.Expressions:
    try:
        data["expressions"].append({"name":x.Name,"formula":x.RightHandSide})
    except Exception as e:
        data["expressions"].append({"error":str(e)})
def children(c):
    if c is None:
        return
    for x in c.GetChildren():
        entry=info(x)
        try:
            entry["prototype"]=x.Prototype.OwningPart.FullPath
        except Exception:
            entry["prototype"]="unavailable"
        data["components"].append(entry)
        children(x)
children(p.ComponentAssembly.RootComponent)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("MODEL_AUDIT_SAVED; source not saved or modified")
