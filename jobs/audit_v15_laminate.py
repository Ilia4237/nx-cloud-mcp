import os,json
from pathlib import Path
import NXOpen
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V15_LAMINATE_AUDIT_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"bodies":[],"materials":[],"errors":[]}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v06_materials.prt")
    if status is not None: status.Dispose()
    for b in p.Bodies:
        try:
            bb=b.GetBoundingBox()
            size=[bb.MaxPoint.X-bb.MinPoint.X,bb.MaxPoint.Y-bb.MinPoint.Y,bb.MaxPoint.Z-bb.MinPoint.Z]
            vol=b.Volume
            area=sum(f.Area for f in b.GetFaces())
            mat=None
            try:
                assigned=b.GetMaterial()
                mat=assigned.Name if assigned else None
            except Exception as e: mat=f"ERROR: {e}"
            d["bodies"].append({"name":b.Name,"size_mm":size,"volume_mm3":vol,"surface_area_mm2":area,"material":mat})
        except Exception as e: d["bodies"].append({"name":b.Name,"error":str(e)})
    for m in p.MaterialManager.PhysicalMaterials:
        d["materials"].append(m.Name)
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
