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

def resolve(*names):
    value = None
    for name in names:
        try:
            value = getattr(value, name) if value is not None else name
        except Exception:
            return None
    return value

shade_method = None
for option in [
    resolve(ufs, "Disp", "ShadeMethod", "Preview"),
    resolve(ufs, "Disp", "ShadeMethod", "HighQuality"),
    resolve(ufs, "Disp", "ShadeMethod", "Normal"),
]:
    if option is not None:
        shade_method = option
        break
if shade_method is None:
    raise RuntimeError("Unable to resolve UF Disp ShadeMethod")

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
        view.Fit()
    except Exception:
        pass
    ufs.Disp.BatchShade(str(png_path), 1280, 720, shade_method)
    if not png_path.is_file() or png_path.stat().st_size == 0:
        raise RuntimeError("NX BatchShade did not create a non-empty PNG")
    report_path.write_text(
        "NX_PREVIEW_OK\n"
        f"Part: {part_path}\n"
        "Mode: read-only BatchShade preview; no part was modified or saved.\n"
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
