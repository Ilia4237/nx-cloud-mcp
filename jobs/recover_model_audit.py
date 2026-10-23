import os
from pathlib import Path
source=Path("C:/Users/bobri/Siemens_Local_Agent/data/jobs/99db38b6333b9758eb4cfee9/MONOCOQUE_MODEL_AUDIT.json")
report=source.read_text(encoding="utf-8")
if not report.strip():
    raise RuntimeError("Audit report is empty")
target=Path(os.environ["SIEMENS_JOB_DIR"])/"MONOCOQUE_MODEL_AUDIT.txt"
if target.exists():
    raise RuntimeError("Target already exists")
target.write_text(report,encoding="utf-8")
print("AUDIT_REPORT_RECOVERED; NX model not opened or modified")
