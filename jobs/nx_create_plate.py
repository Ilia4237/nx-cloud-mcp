import os
from pathlib import Path
import NXOpen
import NXOpen.Features
import NXOpen.GeometricUtilities

folder = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
output = folder / "plate_test.prt"
if output.exists():
    raise RuntimeError("Refusing to overwrite: " + str(output))

session = NXOpen.Session.GetSession()
part = session.Parts.NewDisplay(str(output), NXOpen.Part.Units.Millimeters)
builder = part.Features.CreateBlockFeatureBuilder(NXOpen.Features.Block.Null)
try:
    builder.Type = NXOpen.Features.BlockFeatureBuilderTypes.OriginAndEdgeLengths
    builder.SetOriginAndLengths(NXOpen.Point3d(0.0, 0.0, 0.0), "100", "50", "3")
    builder.BooleanOption.Type = NXOpen.GeometricUtilities.BooleanOperation.BooleanType.Create
    feature = builder.Commit()
finally:
    builder.Destroy()

bodies = list(part.Bodies)
if len(bodies) != 1 or not bodies[0].IsSolidBody:
    raise RuntimeError("Expected exactly one solid body")
save_status = part.Save(NXOpen.BasePart.SaveComponents.TrueValue, NXOpen.BasePart.CloseAfterSave.FalseValue)
save_status.Dispose()
if not output.is_file() or output.stat().st_size == 0:
    raise RuntimeError("Part file was not saved")
print("PLATE_TEST_OK: 100 x 50 x 3 mm; saved to " + str(output))
