import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V07_CORE_PROPS_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    pm=p.MaterialManager.PhysicalMaterials
    material=None
    for m in pm:
        if m.Name=="EDU_AL_HONEYCOMB_EQUIV": material=m; break
    if material is None: raise RuntimeError("Core material not found")
    table=material.MaterialTable
    table.SetScalarFieldValue("MassDensity",72.0)
    table.SetScalarFieldValue("YoungsModulus1",0.05)
    table.SetScalarFieldValue("YoungsModulus2",0.05)
    table.SetScalarFieldValue("YoungsModulus3",1000.0)
    table.SetScalarFieldValue("ShearModulus12",0.05)
    table.SetScalarFieldValue("ShearModulus13",100.0)
    table.SetScalarFieldValue("ShearModulus23",100.0)
    table.SetScalarFieldValue("PoissonsRatio12",0.01)
    table.SetScalarFieldValue("PoissonsRatio13",0.0001)
    table.SetScalarFieldValue("PoissonsRatio23",0.0001)
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["output"]=p.FullPath; d["material"]=material.Name
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
