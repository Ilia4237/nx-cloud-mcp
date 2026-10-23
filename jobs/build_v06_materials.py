import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V06_MATERIAL_REPORT.txt"
target=Path(os.environ["SIEMENS_JOB_DIR"])/"Monocoque_EDU_v06_materials.prt"
if r.exists() or target.exists(): raise RuntimeError("Output exists")
d={"saved":False,"assignments":[],"errors":[]}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/4e89fed5d68b203d98c25338/Monocoque_EDU_v05_unified_reinforcement.prt")
    if status is not None: status.Dispose()
    d["source"]=p.FullPath
    pm=p.MaterialManager.PhysicalMaterials
    def make(name,category,density):
        b=pm.CreatePhysicalMaterialBuilder(NXOpen.PhysicalMaterial.Type.Isotropic)
        b.ItemName=name
        t=b.ItemPropertyTable
        t.SetStringPropertyValue("Category",category)
        w=t.GetScalarFieldWrapperPropertyValue("MassDensity")
        p.Expressions.EditWithUnits(w.GetExpression(),p.UnitCollection.FindObject("kg_per_m3"),density)
        m=b.Commit(); b.Destroy(); return m
    cfrp=make("EDU_CFRP_QUASI_ISO","Carbon Fiber Reinforced Plastic",1550.0)
    core=make("EDU_AL_HONEYCOMB_EQUIV","Aluminum Honeycomb Core",72.0)
    groups={"EDU_CFRP_QUASI_ISO":[n for n in [b.Name for b in p.Bodies] if ("CFRP" in n or "REINFORCEMENT" in n or "STRAP" in n or "CAP" in n)],"EDU_AL_HONEYCOMB_EQUIV":[n for n in [b.Name for b in p.Bodies] if "CORE_EQUIVALENT" in n]}
    for name,items in groups.items():
        material=next(m for m in pm.PhysicalMaterials if m.Name==name)
        objs=[p.Bodies.FindObject(n) for n in items]
        material.AssignObjects(objs)
        d["assignments"].append({"material":name,"bodies":items})
    d["material_count"]=len(list(pm.PhysicalMaterials))
    if d["material_count"]<2: raise RuntimeError("Materials missing")
    save_status=p.SaveAs(str(target))
    if save_status is not None: save_status.Dispose()
    d["saved"]=target.exists() and target.stat().st_size>0
    d["output"]=str(target)
    d["note"]="Isotropic educational placeholders; CFRP is not orthotropic laminate; no structural validation."
    if not d["saved"]: raise RuntimeError("Output not verified")
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
