# OsdagBridge report generator improvements

## Changes made

- Centralized page geometry, table padding, row spacing, rules, repeated table-header styling, and chart palette in src/osdagbridge/core/reports/styles.py. The report preamble consumes these settings once, so every chapter inherits the same document theme.
- Kept report tables that can span pages as longtable and retained repeated \endfirsthead / \endhead blocks. Global needspace page-bottom reservation now uses the shared style values. Wider page margins and a larger footer clearance reduce crowding around the standard header and footer.
- Removed negative vertical shifts from the footer rule and moved the software-default note into the footer text block, keeping footer content inside the reserved footer area.
- Split Chapter 3 vehicle live loads and footway pressure into separate tables. Vehicle names come from the selected Loading tab flags; impact, braking, and centrifugal-force basis are explicit. The footway table reports the selected mode and its pressure.
- Added temporary chart generation in report_charts.py. Chapter 5 receives component utilization ratios and a dashed UR=1.0 limit. Chapter 7 receives structural steel, concrete, and reinforcement summaries. Images are written under the PDF build's temporary images directory and embedded from there.
- Extended BOQ calculations to include the designed end diaphragms using their section mass, bay spacing, girder depth, brace layout, and two support locations. The quantity appears in the Chapter 7 table and the steel chart.

## Design choices

styles.py owns stable document-wide visual rules; the chapter modules keep their domain-specific column definitions and table content. Generated chart assets are temporary, avoiding stale images beside user reports. Chart values are derived from the design/quantity payload. When a component check or quantity is unavailable, the chart labels it as unavailable rather than inventing a value.

## Verification and deliverables

The user identified `PROPERTY INVESTMENT RESEARCH.pdf` as Report_Before and `new_aftr_report.pdf` as the manually saved Report_After. The mapped files were copied to `output/pdf/Report_Before.pdf` and `output/pdf/Report_After_Provided.pdf`; the originals in Downloads were left untouched. Visual review showed the provided after file still had the old combined live-load table, no utilization or quantity charts, and no end-diaphragm BOQ total.

The saved `inputs.osi` was regenerated from the updated source. The final 81-page report is `output/pdf/Report_After.pdf`. Chapter 3 separates vehicle live loads and footway pressure. Chapter 5 includes component utilization ratios and a UR=1.0 capacity line. Chapter 7 includes steel and concrete/reinforcement charts and an end-diaphragm total of 2.24 MT. The utilization chart uses the same cross-bracing checks that Chapter 5 reports for cross-braced end diaphragms.

The export now creates CAD views from the available bridge generator and embeds them in Chapter 6, including the bridge layout, girder views, and cross-bracing/end-diaphragm layouts. It also draws section-profile schematics from the selected member types and designations; these are explicitly labeled as schematic profiles and the designation remains the dimensional reference. The CAD export uses a temporary output folder, preventing report generation from overwriting the application's shared image assets. Missing CAD imports were corrected so headless export can produce the views.

The first export exposed two report-generator issues that were corrected: LaTeX's font cache needed a writable `TEXMFVAR`/`TEXMFCONFIG` path, and report generation could return a pre-existing PDF path after a failed compile. The cache now uses a project-local temporary path, and the generator only reports success when the current run produced a PDF. The final PDF compiled successfully, and its Chapter 6 drawings were rendered for visual review. LaTeX reports some overfull horizontal boxes in the source document; these are non-fatal and the report build completes.

The report changes are published to the `task1-repeated-table-headers` branch of `https://github.com/sunav1411/OsdagBridge`. The configured upstream is `https://github.com/Nidhikhare12/OsdagBridge.git`. The user confirmed that the collaborator invitation to `Nidhikhare12` has been sent.
