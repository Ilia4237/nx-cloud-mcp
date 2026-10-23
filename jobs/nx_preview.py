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
disp = ufs.Disp

def call_variants(func, variants):
    errors = []
    for args in variants:
        try:
            result = func(*args)
            return args, result, None
        except Exception as exc:
            errors.append(f"{args!r}: {type(exc).__name__}: {exc}")
    return None, None, " | ".join(errors)

method_candidates = []
for container in [disp, ufs]:
    for group in ["ShadeMethod", "UFDispShadeMethod", "ShadeMode"]:
        obj = getattr(container, group, None)
        if obj is None:
            continue
        for name in ["Preview", "HighQuality", "Normal", "Wireframe"]:
            value = getattr(obj, name, None)
            if value is not None:
                method_candidates.append(value)
method_candidates += [0, 1, 2, 3]

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
    try:
        part.ModelingViews.WorkView.Fit()
    except Exception as exc:
        diagnostics.append(f"fit: {exc}")

    variants = []
    for method in method_candidates:
        variants.append((str(png_path), 1280, 720, method))
    variants.append((str(png_path), 1280, 720))
    variants.append((str(png_path),))
    args, result, errors = call_variants(disp.BatchShade, variants)
    diagnostics.append(f"batchshade_args={args!r}")
    diagnostics.append(f"batchshade_result={result!r}")
    diagnostics.append(f"batchshade_errors={errors}")
    diagnostics.append(f"disp_attributes={sorted([n for n in dir(disp) if not n.startswith('_')])}")

    if not png_path.is_file() or png_path.stat().st_size == 0:
        report_path.write_text(
            "NX_PREVIEW_FAILED\n"
            f"Part: {part_path}\n"
            "No part was modified or saved.\n"
            + "\n".join(diagnostics) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError("NX BatchShade did not create a non-empty PNG")
    report_path.write_text(
        "NX_PREVIEW_OK\n"
        f"Part: {part_path}\n"
        "Mode: read-only BatchShade preview; no part was modified or saved.\n"
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
