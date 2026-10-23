import os,json,itertools
from pathlib import Path
import NXOpen,NXOpen.Features,NXOpen.UF
s=NXOpen.Session.GetSession()
u=NXOpen.UF.UFSession.GetUFSession()
root=Path(os.environ["SIEMENS_JOB_DIR"])
report=root/"V05_BUILD_REPORT.txt"
target=root/"Monocoque_EDU_v05_unified_reinforcement.prt"
if target.exists() or report.exists(): raise RuntimeError("Output exists")
d={"saved":False,"design_status":"Educational CAD baseline; laminate and strength not validated"}
try:
    p,status=s.Parts.OpenBaseDisplay("C:/Users/bobri/NX_Rollback_Backup_20261023_035742/NX_Automation/Monocoque_EDU_v04.prt")
    if status is not None: status.Dispose()
    d["source"]=p.FullPath
    bodies={b.Name:b for b in p.Bodies}
    main=bodies["V03_FRONT_EXTERNAL_U_STRAP"]
    for name in ("V03_LEFT_DECK_CORNER_STRAP","V03_RIGHT_DECK_CORNER_STRAP"):
        builder=p.Features.CreateBooleanBuilder(NXOpen.Features.BooleanFeature.Null)
        try:
            builder.Operation=NXOpen.Features.Feature.BooleanType.Unite
            builder.Target=main
            builder.Tool=bodies[name]
            builder.RetainTarget=False
            builder.RetainTool=False
            feature=builder.CommitFeature()
            main=list(feature.GetBodies())[0]
        finally: builder.Destroy()
    main.SetName("V05_FRONT_CONTINUOUS_REINFORCEMENT")
    current=list(p.Bodies)
    d["body_count"]=len(current)
    if len(current)!=16: raise RuntimeError("Expected 16 bodies after unite")
    module=next(getattr(u,n) for n in dir(u) if not n.startswith('_') and hasattr(getattr(u,n),'CheckInterference'))
    d["remaining_interferences"]=[]
    for a,b in itertools.combinations(current,2):
        codes=module.CheckInterference(a.Tag,1,[b.Tag])
        if codes[0]==1: d["remaining_interferences"].append([a.Name,b.Name])
    if d["remaining_interferences"]: raise RuntimeError("Interferences remain; output not saved")
    save_status=p.SaveAs(str(target))
    if save_status is not None: save_status.Dispose()
    d["saved"]=target.exists() and target.stat().st_size>0
    d["output"]=str(target)
    if not d["saved"]: raise RuntimeError("Output not verified")
except Exception as e:
    d["error"]=str(e)
finally:
    report.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
