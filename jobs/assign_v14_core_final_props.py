import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V14_CORE_FINAL_PROPS_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"set_results":{},"readback":{},"errors":[],"saved":False}
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
    props={"MassDensity":72.0,"YoungsModulus":0.05,"YoungsModulus2":0.05,"YoungsModulus3":1000.0,"ShearModulus":0.05,"ShearModulus2":100.0,"ShearModulus3":100.0,"PoissonsRatio":0.01,"PoissonsRatio3":0.0001,"PoissonsRatio2":0.0001}
    for name,value in props.items():
        try:
            table.SetDoublePropertyValue(name,value); d["set_results"][name]="SetDoublePropertyValue"
        except Exception as e:
            d["set_results"][name]=f"ERROR: {e}"; d["errors"].append(f"{name}: {e}")
    try: material.UpdateMaterialProperties()
    except Exception as e: d["errors"].append(f"UpdateMaterialProperties: {e}")
    for name in props:
        try: d["readback"][name]=table.GetDoublePropertyValue(name)
        except Exception as e: d["readback"][name]=f"ERROR: {e}"
    cores=[b for b in p.Bodies if "CORE_EQUIVALENT" in b.Name]
    material.AssignObjects(cores)
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["assigned"]=[b.Name for b in cores]; d["output"]=p.FullPath
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
