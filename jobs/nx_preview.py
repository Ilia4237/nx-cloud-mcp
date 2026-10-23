import os
from pathlib import Path
import NXOpen
import NXOpen.UF

out_dir = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
part_path = Path(r"C:\Users\bobri\NX_Rollback_Backup_20261023_035742\NX_Automation\Monocoque_EDU_v04.prt")
png_path = out_dir / "MONOCOQUE_PREVIEW.png"
report_path = out_dir / "MONOCOQUE_PREVIEW.txt"
if png_path.exists() or report_path.exists():
    raise RuntimeError("Refusing to overwrite preview files")
if not part_path.is_file():
    raise FileNotFoundError(f"Part not found: {part_path}")

session = NXOpen.Session.GetSession()
if session is None:
    raise RuntimeError("NX session unavailable")
ufs = NXOpen.UF.UFSession.GetUFSession()

opened = session.Parts.Open(str(part_path))
part, load_status = opened if isinstance(opened, tuple) else (opened, None)
if part is None:
    raise RuntimeError("NX could not open the part")
try:
    session.Parts.SetDisplay(part, True, True)
finally:
    if load_status is not None:
        load_status.Dispose()

try:
    view = part.ModelingViews.WorkView
    try:
        view.Orient(NXOpen.View.Canned.Isometric)
    except Exception:
        pass
    try:
        view.Fit()
    except Exception:
        pass
    ufs.Disp.CreateImage(str(png_path), NXOpen.UF.UFDisp.ImageFormat.Png, NXOpen.UF.UFDisp.BackgroundColor.White)
    if not png_path.is_file() or png_path.stat().st_size == 0:
        raise RuntimeError("NX did not create a non-empty PNG")
    report_path.write_text(
        "NX_PREVIEW_OK\n"
        f"Part: {part_path}\n"
        "Mode: read-only preview; no part was modified or saved.\n"
        f"PNG: {png_path.name}\n",
        encoding="utf-8",
    )
    print("NX_PREVIEW_OK")
finally:
    if part is not None:
        try:
            whole_tree = getattr(NXOpen.BasePart.CloseWholeTree, "False")
            close_modified = getattr(NXOpen.BasePart.CloseModified, "CloseModified")
            part.Close(whole_tree, close_modified, None)
        except Exception:
            pass
