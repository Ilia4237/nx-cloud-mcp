import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V05_MATERIAL_INVENTORY.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"errors":[],"bodies":[],"materials":[],"expressions":[]}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/4e89fed5d68b203d98c25338/Monocoque_EDU_v05_unified_reinforcement.prt")
    if status is not None: status.Dispose()
    d["source"]=p.FullPath
    d["units_enum"]=str(p.PartUnits)
    d["is_millimeters"]=(p.PartUnits==NXOpen.Part.Units.Millimeters)
    for b in p.Bodies:
        item={"name":b.Name,"solid":b.IsSolidBody,"attributes":[]}
        try:
            for a in b.GetUserAttributes():
                item["attributes"].append({"title":a.Title,"type":str(a.Type),"string":a.StringValue,"real":a.RealValue,"integer":a.IntegerValue})
        except Exception as e: item["attribute_error"]=str(e)
        d["bodies"].append(item)
    try:
        for m in p.MaterialManager.PhysicalMaterials:
            item={"name":m.Name}
            try: item["assigned_objects"]=[getattr(x,"Name",str(x.Tag)) for x in m.GetAssignedObjects()]
            except Exception as e: item["assignment_error"]=str(e)
            d["materials"].append(item)
    except Exception as e: d["material_query_error"]=str(e)
    for e in p.Expressions: d["expressions"].append({"name":e.Name,"formula":e.RightHandSide})
    d["note"]="Inventory only; no materials assigned; no laminate or strength validation; source not saved."
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
