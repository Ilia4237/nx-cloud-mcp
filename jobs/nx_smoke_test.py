import NXOpen

session = NXOpen.Session.GetSession()
if session is None:
    raise RuntimeError("NXOpen session is unavailable")
print("NX_SMOKE_TEST_OK: NXOpen session acquired; no parts opened, modified or saved.")
