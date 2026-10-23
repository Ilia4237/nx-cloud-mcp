import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V06_ASSIGN_REPORT.txt"
target=Path(os.environ["SIEMENS_JOB_DIR"])/"Monocoque_EDU_v06_materials.prt"
if r.exists(): raise RuntimeError("Report exists")
d={"assignments":[],"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    materials=list(pm)
    if len(materials)!=1 or materials[0].Name!="EDU_CFRP_QUASI_ISO": raise RuntimeError("Expected existing CFRP material")
    material=materials[0]
    cfrp=[b for b in p.Bodies if ("CFRP" in b.Name or "REINFORCEMENT" in b.Name or "STRAP" in b.Name or "CAP" in b.Name)]
    if len(cfrp)!=12: raise RuntimeError(f"Expected 12 CFRP bodies, found {len(cfrp)}")
    material.AssignObjects(cfrp)
    d["assignments"].append({"material":material.Name,"bodies":[b.Name for b in cfrp]})
    save_status=p.Save()
    if save_status is not None: save_status.Dispose()
    d["saved"]=True
    d["output"]=p.FullPath
    d["note"]="CFRP assigned to 12 bodies; core bodies remain unassigned."
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
