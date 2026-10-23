import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V11_CORE_V3_PROPS_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"created":False,"property_table_methods":[],"set_results":{},"assigned":[],"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    if any(m.Name=="EDU_AL_HONEYCOMB_EQUIV_V3" for m in pm): raise RuntimeError("V3 material already exists")
    builder=pm.CreatePhysicalMaterialBuilder(NXOpen.PhysicalMaterial.Type.Orthotropic)
    builder.ItemName="EDU_AL_HONEYCOMB_EQUIV_V3"
    table=builder.PropertyTable
    d["property_table_methods"]=[x for x in dir(table) if not x.startswith("_")]
    props={"MassDensity":72.0,"YoungsModulus1":0.05,"YoungsModulus2":0.05,"YoungsModulus3":1000.0,"ShearModulus12":0.05,"ShearModulus13":100.0,"ShearModulus23":100.0,"PoissonsRatio12":0.01,"PoissonsRatio13":0.0001,"PoissonsRatio23":0.0001}
    for name,value in props.items():
        done=[]
        for method in ["SetScalarFieldValue","SetScalar","SetRealValue","SetValue","SetLogicalValue"]:
            if hasattr(table,method):
                try:
                    getattr(table,method)(name,value); done.append(method); break
                except Exception as e: d["set_results"][name+"_"+method]=str(e)
        d["set_results"][name]=done
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
