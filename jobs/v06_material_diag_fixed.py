from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/7955c34b113f1b1910321e1f/payload.py").read_text(encoding="utf-8")
source=source.replace('step("open",{"bodies":len(list(p.Bodies)),"materials":len(list(pm.PhysicalMaterials))})','step("open",{"bodies":len(list(p.Bodies)),"materials":len(list(pm))})')
source=source.replace('step("commit",{"material":material.Name})','step("commit",{"material":material.Name,"materials":len(list(pm))})')
exec(compile(source,"v06_material_diag_fixed","exec"))
