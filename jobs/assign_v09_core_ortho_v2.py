import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V09_CORE_ORTHO_V2_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"created":False,"assigned":[],"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    if any(m.Name=="EDU_AL_HONEYCOMB_EQUIV_V2" for m in pm): raise RuntimeError("V2 material already exists")
    builder=pm.CreatePhysicalMaterialBuilder(NXOpen.PhysicalMaterial.Type.Orthotropic)
    builder.ItemName="EDU_AL_HONEYCOMB_EQUIV_V2"
    material=builder.Commit(); builder.Destroy()
    d["created"]=True
    cores=[b for b in p.Bodies if "CORE_EQUIVALENT" in b.Name]
    if len(cores)!=4: raise RuntimeError(f"Expected 4 core bodies, found {len(cores)}")
    material.AssignObjects(cores)
    d["assigned"]=[b.Name for b in cores]
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["output"]=p.FullPath
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
