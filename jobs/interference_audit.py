import os,json
from pathlib import Path
import NXOpen,NXOpen.UF
s=NXOpen.Session.GetSession()
u=NXOpen.UF.UFSession.GetUFSession()
r=Path(os.environ["SIEMENS_JOB_DIR"])/"INTERFERENCE_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"pairs":[],"errors":[],"legend":{"1":"interference","2":"no interference","3":"touching"}}
def save(): r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
try:
    audit=json.loads(Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/18ebff2826ca9dbf24d49ae0/GEOMETRY_REPORT.txt").read_text(encoding="utf-8"))
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/NX_Rollback_Backup_20261023_035742/NX_Automation/Monocoque_EDU_v04.prt")
    if status is not None: status.Dispose()
    d["units"]=str(p.PartUnits)
    bodies={b.Name:b for b in p.Bodies}
    module=next(getattr(u,n) for n in dir(u) if not n.startswith('_') and hasattr(getattr(u,n),'CheckInterference'))
    d["api_help"]=str(module.CheckInterference.__doc__)
    save()
    for pair in audit["pairs"]:
        if "distance" not in pair or abs(pair["distance"])>1e-7: continue
        item={"a":pair["a"],"b":pair["b"]}
        try:
            result=module.CheckInterference(bodies[item["a"]].Tag,1,[bodies[item["b"]].Tag])
            item["raw_result"]=result
        except Exception as e: item["error"]=str(e)
        d["pairs"].append(item)
        save()
    d["note"]="Source model not saved. Interpret raw_result using API signature and legend."
except Exception as e: d["errors"].append(str(e))
finally: save()
