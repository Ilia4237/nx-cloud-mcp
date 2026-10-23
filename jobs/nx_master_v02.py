import os
import json
from pathlib import Path
import NXOpen

root = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
path = root / "MASTER_V02.prt"
if path.exists():
    raise RuntimeError("Refusing to overwrite MASTER_V02")
s = NXOpen.Session.GetSession()
p = s.Parts.NewDisplay(str(path), NXOpen.Part.Units.Millimeters)
mm = p.UnitCollection.FindObject("MilliMeter")
values = {"REAR_X":"100", "HIP_X":"700", "PEDAL_X":"1300", "FRONT_X":"1900",
          "REAR_W":"600", "HIP_W":"650", "PEDAL_W":"520", "FRONT_W":"360",
          "REAR_H":"480", "HIP_H":"520", "PEDAL_H":"420", "FRONT_H":"300",
          "FLOOR_Z":"40"}
expr = {}
for name, formula in values.items():
    expr[name] = p.Expressions.CreateNumberExpression(name+"="+formula, mm)

def cg(obj, point):
    g = NXOpen.Sketch.ConstraintGeometry()
    g.Geometry = obj
    g.PointType = point
    g.SplineDefiningPointIndex = 0
    return g

def dg(obj, assoc):
    g = NXOpen.Sketch.DimensionGeometry()
    g.Geometry = obj
    g.AssocType = assoc
    g.AssocValue = 0
    return g

def sketch(name, yz, vertices):
    matrix = NXOpen.Matrix3x3()
    matrix.Xx = 1.0
    if yz:
        matrix.Yz = 1.0
        matrix.Zy = -1.0
    else:
        matrix.Yy = matrix.Zz = 1.0
    xform = p.Xforms.CreateXform(NXOpen.Point3d(0.,0.,0.), matrix,
                                 NXOpen.SmartObject.UpdateOption.WithinModeling, 1.0)
    csys = p.CoordinateSystems.CreateCoordinateSystem(xform, NXOpen.SmartObject.UpdateOption.WithinModeling)
    b = p.Sketches.CreateSketchInPlaceBuilder2(NXOpen.Sketch.Null)
    try:
        b.Csystem = csys
        sk = b.Commit()
    finally:
        b.Destroy()
    sk.SetName(name)
    sk.Feature.SetName(name)
    sk.Activate(NXOpen.Sketch.ViewReorient.FalseValue)
    def xyz(u,v):
        return NXOpen.Point3d(float(u),0.,float(v)) if yz else NXOpen.Point3d(float(u),float(v),0.)
    anchor = p.Points.CreatePoint(xyz(0.,0.))
    sk.AddGeometry(anchor, NXOpen.Sketch.InferConstraintsOption.InferNoConstraints)
    sk.CreateFixedConstraint(cg(anchor,NXOpen.Sketch.ConstraintPointType.NoneValue))
    lines = []
    for i,(u,v,uf,vf) in enumerate(vertices):
        nxt = vertices[(i+1) % len(vertices)]
        line = p.Curves.CreateLine(xyz(u,v),xyz(nxt[0],nxt[1]))
        sk.AddGeometry(line, NXOpen.Sketch.InferConstraintsOption.InferNoConstraints)
        lines.append(line)
    for i,line in enumerate(lines):
        sk.CreateCoincidentConstraint(cg(line,NXOpen.Sketch.ConstraintPointType.EndVertex),
             cg(lines[(i+1) % len(lines)],NXOpen.Sketch.ConstraintPointType.StartVertex))
        u,v,uf,vf = vertices[i]
        for axis,formula,kind in [("X",uf,NXOpen.Sketch.ConstraintType.HorizontalDim),
                                   ("Y",vf,NXOpen.Sketch.ConstraintType.VerticalDim)]:
            e = p.Expressions.CreateNumberExpression(name+"_"+axis+str(i)+"="+formula,mm)
            sk.CreateDimension(kind,dg(anchor,NXOpen.Sketch.AssocType.NoneValue),
                 dg(line,NXOpen.Sketch.AssocType.StartPoint),xyz(u+30,v+30),e)
    sk.Update()
    status,dof = sk.GetStatus()
    if dof != 0 or status != NXOpen.Sketch.Status.WellConstrained:
        raise RuntimeError(name+" is not fully constrained: "+str(status)+", DOF="+str(dof))
    sk.Deactivate(NXOpen.Sketch.ViewReorient.FalseValue,NXOpen.Sketch.UpdateLevel.Model)
    return sk,lines

stations = [(100,600,480,"REAR"),(700,650,520,"HIP"),
            (1300,520,420,"PEDAL"),(1900,360,300,"FRONT")]
plan = [(x,-w/2,n+"_X",n+"_W/2") for x,w,h,n in stations]
plan += [(x,w/2,n+"_X",n+"_W/2") for x,w,h,n in reversed(stations)]
side = [(x,40,n+"_X","FLOOR_Z") for x,w,h,n in stations]
side += [(x,h,n+"_X",n+"_H") for x,w,h,n in reversed(stations)]
top,lines = sketch("PLAN",False,plan)
profile,unused = sketch("PROFILE",True,side)
mark = s.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible,"Width rebuild check")
try:
    p.Expressions.Edit(expr["HIP_W"],"700")
    if s.UpdateManager.DoUpdate(mark):raise RuntimeError("Width update failed")
    if abs(abs(lines[1].StartPoint.Y)-350.) > 0.01:
        raise RuntimeError("PLAN did not follow HIP_W")
finally:
    p.Expressions.Edit(expr["HIP_W"],"650")
    s.UpdateManager.DoUpdate(mark)
if abs(abs(lines[1].StartPoint.Y)-325.) > 0.01:
    raise RuntimeError("Width restore failed")
p.ModelingViews.WorkView.Fit()
saved = p.Save(NXOpen.BasePart.SaveComponents.TrueValue,NXOpen.BasePart.CloseAfterSave.FalseValue)
saved.Dispose()
(root/"MASTER_CHECK.json").write_text(json.dumps({"width_rebuild":"passed", "sketches":["PLAN","PROFILE"],
    "axes":"X forward, Y left, Z up; origin 100 mm behind rear section", 
    "scope":"master sketches only; no skins, core, FEA or cross-part links", 
    "dimensions":"preliminary, not verified for driver or rules"},indent=2),encoding="utf-8")
print("MASTER_V02_OK: fully constrained PLAN and PROFILE; width rebuild passed")
