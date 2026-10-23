import os
from pathlib import Path
import NXOpen
import NXOpen.UF

root = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
report = root / "PREVIEW_REPORT.txt"
image = root / "MONOCOQUE_PREVIEW.jpg"
source = Path("C:/Users/bobri/NX_Rollback_Backup_20261023_035742/NX_Automation/Monocoque_EDU_v04.prt")
if report.exists() or image.exists():
    raise RuntimeError("Output already exists")
def log(message):
    with report.open("a", encoding="utf-8") as stream:
        stream.write(message + "\n")
log("Starting JPEG PREVIEW attempt; no model save calls")
try:
    if not source.is_file():
        raise FileNotFoundError(str(source))
    session = NXOpen.Session.GetSession()
    uf = NXOpen.UF.UFSession.GetUFSession()
    part, status = session.Parts.Open(str(source))
    try:
        if part is None:
            raise RuntimeError("Part not loaded")
        display_status = session.Parts.SetDisplay(part, True, True)
    finally:
        if status is not None:
            status.Dispose()
    log("Part loaded and assigned for display")
    view = part.ModelingViews.WorkView
    view.Orient(NXOpen.View.Canned.Isometric, NXOpen.View.ScaleAdjustment.Fit)
    view.Fit()
    log("Isometric view fitted; entering BatchShade PREVIEW JPEG 1280x720")
    uf.Disp.BatchShade(str(image), 1280, 720, uf.Disp.ShadeMethod.PREVIEW)
    if not image.is_file() or image.stat().st_size < 3:
        raise RuntimeError("JPEG not created")
    with image.open("rb") as stream:
        if stream.read(3) != b"\xff\xd8\xff":
            raise RuntimeError("Output lacks JPEG signature")
    log("JPEG_CREATED bytes=" + str(image.stat().st_size))
    print("JPEG_CREATED")
except Exception as error:
    log(type(error).__name__ + ": " + str(error))
    raise
