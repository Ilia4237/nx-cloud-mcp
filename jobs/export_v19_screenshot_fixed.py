import os,json
from pathlib import Path
import NXOpen
import NXOpen.UF as UF
r=Path(os.environ["SIEMENS_JOB_DIR"])/"V19_SCREENSHOTS_FIXED_REPORT.txt"
if r.exists(): raise RuntimeError("Report exists")
d={"view_methods":[],"images":[],"errors":[],"saved":False}
try:
    s=NXOpen.Session.GetSession()
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/Siemens_Local_Agent/data/jobs/abdb0f5f42bd5f9d2cc3e356/Monocoque_EDU_v07_layup.prt")
    if status is not None: status.Dispose()
    uf=UF.UFSession.GetUFSession()
    d["view_methods"]=[x for x in dir(uf.View) if not x.startswith("_")]
    out=Path(os.environ["SIEMENS_JOB_DIR"])
    png=out/"MONOCOQUE_CURRENT_VIEW.png"
    uf.Disp.CreateImage(str(png),UF.Disp.ImageFormat.Png,UF.Disp.ImageResolution.High)
    d["images"].append(str(png))
    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)
    if save_status is not None: save_status.Dispose()
    d["saved"]=True; d["output"]=p.FullPath
except Exception as e: d["errors"].append(str(e))
finally: r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
