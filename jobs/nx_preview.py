import os
from pathlib import Path
import NXOpen
import NXOpen.Gateway

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

def safe_get(obj, name):
    try:
        value = getattr(obj, name)
        return f"{type(value).__name__}: {value!r}"
    except Exception as exc:
        return f"ERROR {type(exc).__name__}: {exc}"

opened = session.Parts.Open(str(part_path))
part, load_status = opened if isinstance(opened, tuple) else (opened, None)
if part is None:
    raise RuntimeError("NX could not open the part")
try:
    session.Parts.SetDisplay(part, True, True)
finally:
    if load_status is not None:
        load_status.Dispose()

diagnostics = []
try:
    builder = part.ImageCaptureManager.CreateImageCaptureBuilder()
    builder.CaptureMethod = NXOpen.Gateway.ImageCaptureBuilder.CaptureMethodType.GraphicsArea
    builder.File = str(png_path)
    builder.ImageFile = str(png_path)
    builder.Format = NXOpen.Gateway.ImageCaptureBuilder.ImageFormat.Png
    for name in ["CaptureMethod", "File", "ImageFile", "Format", "ImageFormat", "ImageSize", "Size"]:
        diagnostics.append(f"before {name}={safe_get(builder, name)}")
    commit_error = None
    try:
        builder.Commit()
    except Exception as exc:
        commit_error = f"{type(exc).__name__}: {exc}"
    diagnostics.append(f"commit={commit_error}")
    for name in ["CaptureMethod", "File", "ImageFile", "Format", "ImageFormat", "ImageSize", "Size"]:
        diagnostics.append(f"after {name}={safe_get(builder, name)}")
    show_error = None
    try:
        builder.ShowResults()
    except Exception as exc:
        show_error = f"{type(exc).__name__}: {exc}"
    diagnostics.append(f"show_results={show_error}")
    try:
        builder.Destroy()
    except Exception:
        pass

    if not png_path.is_file() or png_path.stat().st_size == 0:
        report_path.write_text(
            "NX_PREVIEW_FAILED\n"
            f"Part: {part_path}\n"
            "No part was modified or saved.\n"
            + "\n".join(diagnostics) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError("NX did not create a non-empty PNG")
    report_path.write_text(
        "NX_PREVIEW_OK\n"
        f"Part: {part_path}\n"
        "Mode: read-only preview; no part was modified or saved.\n"
        f"PNG: {png_path.name}\n" + "\n".join(diagnostics) + "\n",
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
