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

def set_first(obj, names, value):
    errors = []
    for name in names:
        try:
            setattr(obj, name, value)
            return name, None
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    return None, "; ".join(errors)

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
    view = part.ModelingViews.WorkView
    for orientation in [
        getattr(NXOpen, "ViewCanned", None),
        getattr(NXOpen, "View", None),
    ]:
        canned = getattr(orientation, "Isometric", None) if orientation is not None else None
        if canned is not None:
            try:
                view.Orient(canned)
                diagnostics.append(f"orientation={orientation.__name__}")
                break
            except Exception as exc:
                diagnostics.append(f"orient {orientation.__name__}: {exc}")
    try:
        view.Fit()
    except Exception as exc:
        diagnostics.append(f"fit: {exc}")

    builder = part.ImageCaptureManager.CreateImageCaptureBuilder()
    png_format = NXOpen.Gateway.ImageCaptureBuilder.ImageFormat.Png
    graphics_area = NXOpen.Gateway.ImageCaptureBuilder.CaptureMethodType.GraphicsArea
    for prop, value in [
        ("CaptureMethod", graphics_area),
        ("File", str(png_path)),
        ("ImageFile", str(png_path)),
        ("Format", png_format),
        ("ImageFormat", png_format),
    ]:
        name, error = set_first(builder, [prop], value)
        diagnostics.append(f"{prop}={name} error={error}")
    commit_error = None
    try:
        builder.Commit()
    except Exception as exc:
        commit_error = f"{type(exc).__name__}: {exc}"
    diagnostics.append(f"commit={commit_error}")
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
