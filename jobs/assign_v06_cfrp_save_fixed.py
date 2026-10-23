from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/546a63f120cb417dcfd60d7c/payload.py").read_text(encoding="utf-8")
old="    save_status=p.Save()\n    if save_status is not None: save_status.Dispose()\n    d[\"saved\"]=True"
if old not in source: raise RuntimeError("Unexpected script")
new="    save_status=p.Save(NXOpen.Part.SaveComponents.TrueValue,NXOpen.Part.CloseAfterSave.FalseValue)\n    if save_status is not None: save_status.Dispose()\n    d[\"saved\"]=True"
source=source.replace(old,new)
exec(compile(source,"assign_v06_cfrp_save_fixed","exec"))
