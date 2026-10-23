from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/fcf7b5bc44e69ba187230db4/payload.py").read_text(encoding="utf-8")
old="        objs=[p.Bodies.FindObject(n) for n in items]"
if old not in source: raise RuntimeError("Unexpected script")
new="        objs=[b for b in p.Bodies if b.Name in items]\n        if len(objs)!=len(items): raise RuntimeError('Missing bodies')"
source=source.replace(old,new)
exec(compile(source,"v06_materials_fixed","exec"))
