import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V06_CORE_ASSIGN_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"assignments":[],"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    if any(m.Name=="EDU_AL_HONEYCOMB_EQUIV" for m in pm): raise RuntimeError("Core material already exists")
    builder=pm.CreatePhysicalMaterialBuilder(NXOpen.PhysicalMaterial.Type.Isotropic)
    builder.ItemName="EDU_AL_HONEYCOMB_EQUIV"
    material=builder.Commit(); builder.Destroy()
    cores=[b for b in p.Bodies if "CORE_EQUIVALENT" in b.Name]
    if len(cores)!=4: raise RuntimeError(f"Expected 4 core bodies, found {len(cores)}")
    material.AssignObjects(cores)
    d["assignments"].append({"material":material.Name,"bodies":[b.Name for b in cores]})
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["output"]=p.FullPath
    d["note"]="Material created with NX default density; density and honeycomb anisotropy require later correction."
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
