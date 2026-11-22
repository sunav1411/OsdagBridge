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

Python syntax compilation, whitespace checks, LaTeX string checks, chart generation, and a synthetic end-diaphragm quantity calculation were run. Matplotlib and the bundled `pdflatex.exe` are available in the `osdagbridge-env` Conda environment. The desktop application completed a bridge design analysis and populated the design output dock. The report options workflow was opened, but the PDF export was not completed: the Save As dialog was inadvertently pointed at an existing Downloads PDF, and the overwrite prompt was cancelled without modifying that file. No `Report_After.pdf` or original `Report_Before.pdf` has been produced. A genuine before/after PDF pair and visual page-by-page comparison therefore remain outstanding; the input-only `inputs.osi` file is not represented as a completed report.

The report changes are published to the `task1-repeated-table-headers` branch of `https://github.com/sunav1411/OsdagBridge`. The configured upstream is `https://github.com/Nidhikhare12/OsdagBridge.git`. The user confirmed that the collaborator invitation to `Nidhikhare12` has been sent.
