Axis Property Solutions — APS One-Click Market Intelligence
Date: 2025-10-20

How to run:
1) Put your vendor CSV in input\ as test.csv
2) Double-click RUN_ME.bat
3) Your outputs will appear in APS_Market_Intelligence_Live\

Acceptance tests (must pass):
- Zero-edit run creates test_DEMO.pdf
- CoreLogic file with spaces runs clean
- Heat map (teal-yellow-red) renders with no white boxes (map rasterized 300 DPI)
- ZIP breakdown ranks Tier-1 density correctly
- Alias robustness: AVM/Estimated Value etc. map correctly
- 18-point health check prints
- PDF text is selectable (vector), map is the only raster
- Scored CSV includes all required/derived fields, UTF-8



py -m uvicorn engine.aps_api:app --reload