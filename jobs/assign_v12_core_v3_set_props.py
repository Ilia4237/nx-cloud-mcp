import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V12_CORE_V3_SET_PROPS_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"results":{},"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    material=None
    for m in pm:
        if m.Name=="EDU_AL_HONEYCOMB_EQUIV_V3": material=m; break
    if material is None: raise RuntimeError("V3 material not found")
    table=material.GetPropTable()
    props={"MassDensity":72.0,"YoungsModulus1":0.05,"YoungsModulus2":0.05,"YoungsModulus3":1000.0,"ShearModulus12":0.05,"ShearModulus13":100.0,"ShearModulus23":100.0,"PoissonsRatio12":0.01,"PoissonsRatio13":0.0001,"PoissonsRatio23":0.0001}
    for name,value in props.items():
        ok=None; err=None
        for method,args in [("SetDoublePropertyValue",(name,value)),("SetScalarPropertyValue",(name,value)),("SetScalarFieldPropertyValue",(name,value))]:
            if hasattr(table,method):
                try:
                    getattr(table,method)(*args); ok=method; break
                except Exception as e: err=f"{method}: {e}"
        d["results"][name]={"method":ok,"error":err}
    try: material.UpdateMaterialProperties()
    except Exception as e: d["errors"].append(f"UpdateMaterialProperties: {e}")
    cores=[b for b in p.Bodies if "CORE_EQUIVALENT" in b.Name]
    material.AssignObjects(cores)
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["assigned"]=[b.Name for b in cores]; d["output"]=p.FullPath
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
