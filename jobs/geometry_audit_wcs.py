from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/7f9f1c65882062d564979c16/payload.py").read_text(encoding="utf-8")
old="AskBoundingBoxExact(b.Tag,0)"
if old not in source: raise RuntimeError("Unexpected script")
source=source.replace(old,"AskBoundingBoxExact(b.Tag,p.WCS.CoordinateSystem.Tag)")
exec(compile(source,"geometry_audit_wcs","exec"))
