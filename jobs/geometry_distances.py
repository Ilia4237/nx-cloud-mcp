from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/efc9f62745c37639c0089924/payload.py").read_text(encoding="utf-8")
old="u.ModlGeneral.AskMinimumDist("
if old not in source: raise RuntimeError("Unexpected script")
source=source.replace(old,"next(getattr(getattr(u,n), 'AskMinimumDist') for n in dir(u) if not n.startswith('_') and hasattr(getattr(u,n), 'AskMinimumDist'))(")
exec(compile(source,"geometry_distances","exec"))
