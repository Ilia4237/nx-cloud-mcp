import os
from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/296c4f8d57790309997a7809/payload.py").read_text(encoding="utf-8")
old="    box=list(u.Modl.AskBoundingBox(b.Tag))"
new="""    corner,directions,lengths=u.ModlGeneral.AskBoundingBoxExact(b.Tag,0)
    vertices=[[corner[j]+sum(flags[k]*lengths[k]*directions[k][j] for k in range(3)) for j in range(3)] for flags in itertools.product((0,1),repeat=3)]
    box=[min(v[j] for v in vertices) for j in range(3)]+[max(v[j] for v in vertices) for j in range(3)]"""
if old not in source: raise RuntimeError("Unexpected source script")
source=source.replace(old,new)
source=source.replace("u.Modl.AskMinimumDist(","u.ModlGeneral.AskMinimumDist(")
exec(compile(source,"geometry_audit_fixed","exec"))
