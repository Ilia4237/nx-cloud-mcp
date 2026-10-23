import os
import json
from pathlib import Path
import NXOpen
import NXOpen.Features
import NXOpen.GeometricUtilities

ROOT = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
P = {"TUB_LENGTH":1800, "TUB_WIDTH":650, "TUB_HEIGHT":500,
     "CORE_T":20, "SKIN_T":1, "PLY_N":5, "PLY_T":0.2}
# Preliminary CAD dimensions only. PLY_T is assumed, not derived from fabric mass.
# Each component has local expressions. Cross-part associative links are not implemented.
S = NXOpen.Session.GetSession()
ASSEMBLY = ROOT / "MONOCOQUE_V01.prt"
if ASSEMBLY.exists():
    raise RuntimeError("Refusing to overwrite assembly")

def save(part):
    status = part.Save(NXOpen.BasePart.SaveComponents.TrueValue,
                       NXOpen.BasePart.CloseAfterSave.FalseValue)
    status.Dispose()

def component(name, origin, lengths, color):
    path = ROOT / (name + ".prt")
    if path.exists():
        raise RuntimeError("Refusing to overwrite " + str(path))
    part = S.Parts.NewDisplay(str(path), NXOpen.Part.Units.Millimeters)
    for key, value in P.items():
        part.Expressions.CreateExpression("Number", key + "=" + str(value))
    b = part.Features.CreateBlockFeatureBuilder(NXOpen.Features.Block.Null)
    try:
        b.Type = NXOpen.Features.BlockFeatureBuilderTypes.OriginAndEdgeLengths
        b.SetOriginAndLengths(NXOpen.Point3d(*origin), *lengths)
        b.BooleanOption.Type = NXOpen.GeometricUtilities.BooleanOperation.BooleanType.Create
        feature = b.Commit()
        feature.SetName(name)
    finally:
        b.Destroy()
    for body in part.Bodies:
        body.SetName(name)
        body.Color = color
    save(part)
    return path

L, W, H, C, T = [P[k] for k in ("TUB_LENGTH", "TUB_WIDTH", "TUB_HEIGHT", "CORE_T", "SKIN_T")]
D = C + 2*T
specs = []
# Floor occupies z=0..D. Sides and front occupy z=D..H.
for suffix, z, thickness, color in [("OUTER",0,"SKIN_T",216),
                                   ("CORE",T,"CORE_T",36),
                                   ("INNER",T+C,"SKIN_T",186)]:
    specs.append(("FLOOR_"+suffix, (0.,-W/2.,float(z)),
                  ("TUB_LENGTH","TUB_WIDTH",thickness),color))
for side in ("L", "R"):
    offsets = [("OUTER",0,"SKIN_T",216),("CORE",T,"CORE_T",36),
               ("INNER",T+C,"SKIN_T",186)]
    for suffix, off, thickness, color in offsets:
        y = -W/2+off if side=="L" else W/2-off-(T if suffix!="CORE" else C)
        specs.append(("SIDE_"+side+"_"+suffix,(0.,float(y),float(D)),
                      ("TUB_LENGTH",thickness,"TUB_HEIGHT-CORE_T-2*SKIN_T"),color))
for suffix, x, thickness, color in [("OUTER",0,"SKIN_T",216),
                                   ("CORE",T,"CORE_T",36),
                                   ("INNER",T+C,"SKIN_T",186)]:
    specs.append(("FRONT_"+suffix,(float(x),float(-W/2+D),float(D)),
                  (thickness,"TUB_WIDTH-2*(CORE_T+2*SKIN_T)",
                   "TUB_HEIGHT-CORE_T-2*SKIN_T"),color))
paths = [(name,component(name,origin,lengths,color)) for name,origin,lengths,color in specs]
assembly = S.Parts.NewDisplay(str(ASSEMBLY), NXOpen.Part.Units.Millimeters)
for key, value in P.items():
    assembly.Expressions.CreateExpression("Number",key+"="+str(value))
identity = NXOpen.Matrix3x3()
identity.Xx = identity.Yy = identity.Zz = 1.0
for name, path in paths:
    item, status = assembly.ComponentAssembly.AddComponent(str(path), "Entire Part", name,
                          NXOpen.Point3d(0.,0.,0.), identity, -1)
    status.Dispose()
save(assembly)
manifest = {"revision":"V01_LAYOUT_ONLY", "parameters":P,
            "components":[name for name,path in paths],
            "limitations":["No structural verification", "No AMZ replica geometry",
              "Core represented by equivalent solid volumes, not individual cells",
              "No adhesive, inserts, suspension or rollover structure",
              "Local expressions only; origins and assembly parameters not associative",
              "SKIN_T and PLY_T assumed; no measured material properties"]}
(ROOT / "MODEL_NOTES.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
if not ASSEMBLY.is_file():
    raise RuntimeError("Assembly was not saved")
print("MONOCOQUE_V01_OK: assembly and 12 sandwich components saved in " + str(ROOT))
