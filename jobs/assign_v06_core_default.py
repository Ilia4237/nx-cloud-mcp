from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/04404a0901769d067fb8904e/payload.py").read_text(encoding="utf-8")
old='    wrapper=table.GetScalarFieldWrapperPropertyValue("MassDensity")\n    p.Expressions.EditWithUnits(wrapper.GetExpression(),p.UnitCollection.FindObject("kg_per_m3"),72.0)\n'
if old not in source: raise RuntimeError("Unexpected script")
source=source.replace(old,"")
exec(compile(source,"v06_core_default_density","exec"))
