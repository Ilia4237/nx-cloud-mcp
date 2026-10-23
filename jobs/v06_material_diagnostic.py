import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V06_MATERIAL_DIAG.txt"
target=Path(os.environ["SIEMENS_JOB_DIR"])/"Monocoque_EDU_v06_materials.prt"
if r.exists() or target.exists(): raise RuntimeError("Output exists")
d={"steps":[],"saved":False,"errors":[]}
def step(n,x=None):
    d["steps"].append({"step":n,"result":x}); r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/4e89fed5d68b203d98c25338/Monocoque_EDU_v05_unified_reinforcement.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    step("open",{"bodies":len(list(p.Bodies)),"materials":len(list(pm.PhysicalMaterials))})
    builder=pm.CreatePhysicalMaterialBuilder(NXOpen.PhysicalMaterial.Type.Isotropic)
    step("builder",{"methods":[m for m in dir(builder) if not m.startswith('_')][:80]})
    builder.ItemName="EDU_CFRP_QUASI_ISO"
    step("name",builder.ItemName)
    table=builder.ItemPropertyTable
    step("table",{"methods":[m for m in dir(table) if not m.startswith('_')][:100]})
    try:
        wrapper=table.GetScalarFieldWrapperPropertyValue("MassDensity")
        step("density_wrapper",{"methods":[m for m in dir(wrapper) if not m.startswith('_')][:80],"expression":getattr(wrapper.GetExpression(),"Name",None)})
    except Exception as e: step("density_wrapper_error",str(e))
    material=builder.Commit()
    step("commit",{"material":material.Name})
    builder.Destroy()
    save_status=p.SaveAs(str(target))
    if save_status is not None: save_status.Dispose()
    d["saved"]=target.exists() and target.stat().st_size>0
    d["output"]=str(target)
    step("save",d["saved"])
except Exception as e:
    d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
