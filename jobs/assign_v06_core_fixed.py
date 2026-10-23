from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/f5d2f571260d8634dd4fd658/payload.py").read_text(encoding="utf-8")
old='p.Expressions.EditWithUnits(wrapper.GetExpression(),p.UnitCollection.FindObject("kg_per_m3"),72.0)'
if old not in source: raise RuntimeError("Unexpected script")
new='wrapper.GetExpression().SetRightHandSide("72.0")'
source=source.replace(old,new)
exec(compile(source,"v06_core_fixed","exec"))
