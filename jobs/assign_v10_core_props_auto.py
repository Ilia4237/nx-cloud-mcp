import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V10_CORE_PROPS_AUTO_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"material":None,"api_candidates":{},"property_attempts":[],"assigned":[],"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    material=None
    for m in pm:
        if m.Name=="EDU_AL_HONEYCOMB_EQUIV_V2": material=m; break
    if material is None: raise RuntimeError("V2 material not found")
    d["material"]=material.Name
    d["material_methods"]=[x for x in dir(material) if not x.startswith("_")]
    targets={"MassDensity":72.0,"YoungsModulus1":0.05,"YoungsModulus2":0.05,"YoungsModulus3":1000.0,"ShearModulus12":0.05,"ShearModulus13":100.0,"ShearModulus23":100.0,"PoissonsRatio12":0.01,"PoissonsRatio13":0.0001,"PoissonsRatio23":0.0001}
    for attr in ["MaterialTable","PropertyTable","Properties","Table"]:
        if hasattr(material,attr):
            try:
                obj=getattr(material,attr)
                d["api_candidates"][attr]=[x for x in dir(obj) if not x.startswith("_")]
            except Exception as e: d["api_candidates"][attr]=[f"ERROR: {e}"]
    for attr in ["SetScalarFieldValue","SetScalarFieldWrapperPropertyValue","SetPropertyValue","SetValue","EditWithUnits"]:
        if hasattr(material,attr):
            d["property_attempts"].append({"object":"material","method":attr,"available":True})
    builder=pm.CreatePhysicalMaterialBuilder(NXOpen.PhysicalMaterial.Type.Orthotropic)
    d["builder_methods"]=[x for x in dir(builder) if not x.startswith("_")]
    builder.Destroy()
    cores=[b for b in p.Bodies if "CORE_EQUIVALENT" in b.Name]
    if len(cores)!=4: raise RuntimeError(f"Expected 4 core bodies, found {len(cores)}")
    material.AssignObjects(cores)
    d["assigned"]=[b.Name for b in cores]
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["output"]=p.FullPath
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
