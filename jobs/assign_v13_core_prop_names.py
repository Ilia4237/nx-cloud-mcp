import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V13_CORE_PROP_NAMES_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"properties":[],"set_results":{},"errors":[],"saved":False}
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
    count=table.GetPropertyCount()
    for i in range(count):
        try:
            name=table.GetPropertyNameByIndex(i)
            ptype=table.GetPropertyType(name)
            d["properties"].append({"index":i,"name":name,"type":str(ptype)})
        except Exception as e: d["properties"].append({"index":i,"error":str(e)})
    aliases={"YoungsModulus1":["YoungsModulus","YoungsModulusX","E1","YoungsModulus11"],"ShearModulus12":["ShearModulusXY","G12"],"ShearModulus13":["ShearModulusXZ","G13"],"ShearModulus23":["ShearModulusYZ","G23"],"PoissonsRatio12":["PoissonsRatioXY","Nu12"],"PoissonsRatio13":["PoissonsRatioXZ","Nu13"],"PoissonsRatio23":["PoissonsRatioYZ","Nu23"]}
    values={"YoungsModulus1":0.05,"ShearModulus12":0.05,"ShearModulus13":100.0,"ShearModulus23":100.0,"PoissonsRatio12":0.01,"PoissonsRatio13":0.0001,"PoissonsRatio23":0.0001}
    names=[x.get("name") for x in d["properties"] if isinstance(x,dict) and "name" in x]
    for logical,candidates in aliases.items():
        found=[n for n in candidates if n in names]
        d["set_results"][logical]={"candidates":candidates,"found":found}
        if found:
            name=found[0]
            try:
                table.SetDoublePropertyValue(name,values[logical]); d["set_results"][logical]["set"]="SetDoublePropertyValue"
            except Exception as e:
                d["set_results"][logical]["error"]=str(e)
    try: material.UpdateMaterialProperties()
    except Exception as e: d["errors"].append(str(e))
    cores=[b for b in p.Bodies if "CORE_EQUIVALENT" in b.Name]
    material.AssignObjects(cores)
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["assigned"]=[b.Name for b in cores]; d["output"]=p.FullPath
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
