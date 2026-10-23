import os
from pathlib import Path
import NXOpen
import NXOpen.UF

out_dir = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
report_path = out_dir / "SHADE_METHODS.txt"
if report_path.exists():
    raise RuntimeError("Refusing to overwrite diagnostic report")
session = NXOpen.Session.GetSession()
if session is None:
    raise RuntimeError("NX session unavailable")
ufs = NXOpen.UF.UFSession.GetUFSession()
disp = ufs.Disp
shade_type = disp.ShadeMethod
lines = ["SHADE_METHOD_DIAGNOSTIC"]
for name in dir(shade_type):
    if name.startswith("_"):
        continue
    try:
        value = getattr(shade_type, name)
        lines.append(f"{name}={value!r} type={type(value).__name__}")
    except Exception as exc:
        lines.append(f"{name}=ERROR {type(exc).__name__}: {exc}")
try:
    options = disp.BatchShadeOptions
    lines.append(f"BatchShadeOptions={options!r} type={type(options).__name__}")
    for name in dir(options):
        if not name.startswith("_"):
            try:
                lines.append(f"option {name}={getattr(options, name)!r}")
            except Exception as exc:
                lines.append(f"option {name}=ERROR {type(exc).__name__}: {exc}")
except Exception as exc:
    lines.append(f"BatchShadeOptions=ERROR {type(exc).__name__}: {exc}")
report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("SHADE_METHOD_DIAGNOSTIC_OK")
