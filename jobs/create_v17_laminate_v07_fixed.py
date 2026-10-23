import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V17_LAMINATE_V07_FIXED_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"audit":[],"expressions":{},"layup":{},"errors":[],"saved":False,"output":None}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    for b in p.Bodies:
        item={"name":b.Name}
        try:
            faces=b.GetFaces(); item["face_count"]=len(faces); item["surface_area_mm2"]=sum(f.Area for f in faces)
        except Exception as e: item["audit_error"]=str(e)
        d["audit"].append(item)
    out="C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v07_layup.prt"
    save_as=p.SaveAs(out)
    if save_as is not None: save_as.Dispose()
    d["output"]=p.FullPath
    exprs={"SKIN_PLY_THICKNESS":"0.25","SKIN_PLY_COUNT_PER_SIDE":"4","CORE_MATERIAL":"EDU_AL_HONEYCOMB_EQUIV_V3","CFRP_MATERIAL":"EDU_CFRP_QUASI_ISO","LAYUP_SEQUENCE":"[0/45/-45/90]s"}
    for name,value in exprs.items():
        try:
            p.Expressions.Create(name,value); d["expressions"][name]=value
        except Exception as e: d["errors"].append(f"Expression {name}: {e}")
    d["layup"]={"skin_material":"EDU_CFRP_QUASI_ISO","core_material":"EDU_AL_HONEYCOMB_EQUIV_V3","sequence":"[0/45/-45/90]s","ply_thickness_mm":0.25,"plies_per_skin":4,"skin_thickness_mm":1.0,"symmetry":"midplane"}
    p.SetUserAttribute("LAMINATE_SEQUENCE",NXOpen.NXObject.AttributeType.String,d["layup"]["sequence"],True)
    p.SetUserAttribute("SKIN_PLY_THICKNESS_MM",NXOpen.NXObject.AttributeType.String,"0.25",True)
    p.SetUserAttribute("CORE_MATERIAL",NXOpen.NXObject.AttributeType.String,d["layup"]["core_material"],True)
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
