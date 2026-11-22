"""Single source of truth for the generated report's LaTeX theme."""

PAGE_GEOMETRY = r"a4paper, left=0.82in, right=0.82in, top=0.9in, bottom=0.95in, headheight=15pt, headsep=18pt, footskip=32pt"
TABLE_COLUMN_PADDING = "5pt"
TABLE_ROW_STRETCH = "1.12"
TABLE_EXTRA_ROW_HEIGHT = "0.8pt"
TABLE_RULE_WIDTH = "0.45pt"
TABLE_HEADER_COLOR = "91B014"
TABLE_HEADER_TEXT_COLOR = "FFFFFF"
TABLE_HEADER_FONT = r"\bfseries\small"
TABLE_CELL_FONT = r"\small"
TABLE_BOTTOM_RESERVE = r"6\baselineskip"
TABLE_SPACING = {"pre": "0pt", "post": "6pt"}
COMPACT_TABLE_COLUMN_PADDING = "4pt"
DENSE_TABLE_COLUMN_PADDING = "3.5pt"
NARROW_TABLE_COLUMN_PADDING = "3pt"
COMPACT_TABLE_ROW_STRETCH = "1.25"
PALETTE = {
    "brand": "91B014",
    "steel": "4C78A8",
    "concrete": "72A77A",
    "reinforcement": "E4A04B",
    "pass": "4C9A67",
    "fail": "C83E4D",
}


def latex_preamble_settings() -> str:
    """Return shared package settings and layout dimensions."""
    return rf"""
\usepackage{{xcolor}}
\usepackage{{colortbl}}
\definecolor{{osdagGreen}}{{HTML}}{{{PALETTE['brand']}}}
\definecolor{{reportHeader}}{{HTML}}{{{TABLE_HEADER_COLOR}}}
\definecolor{{reportHeaderText}}{{HTML}}{{{TABLE_HEADER_TEXT_COLOR}}}
\newcommand{{\ReportTableHeader}}{{\rowcolor{{reportHeader}}\color{{reportHeaderText}}{TABLE_HEADER_FONT}}}
\newcommand{{\ReportTableCompact}}{{\setlength{{\tabcolsep}}{{{COMPACT_TABLE_COLUMN_PADDING}}}}}
\newcommand{{\ReportTableDense}}{{\setlength{{\tabcolsep}}{{{DENSE_TABLE_COLUMN_PADDING}}}}}
\newcommand{{\ReportTableNarrow}}{{\setlength{{\tabcolsep}}{{{NARROW_TABLE_COLUMN_PADDING}}}}}
\newcommand{{\ReportCompactRows}}{{\renewcommand{{\arraystretch}}{{{COMPACT_TABLE_ROW_STRETCH}}}}}
\setlength{{\tabcolsep}}{{{TABLE_COLUMN_PADDING}}}
\renewcommand{{\arraystretch}}{{{TABLE_ROW_STRETCH}}}
\setlength{{\extrarowheight}}{{{TABLE_EXTRA_ROW_HEIGHT}}}
\setlength{{\arrayrulewidth}}{{{TABLE_RULE_WIDTH}}}
\setlength{{\LTpre}}{{{TABLE_SPACING['pre']}}}
\setlength{{\LTpost}}{{{TABLE_SPACING['post']}}}
\rowcolors{{2}}{{white}}{{black!3}}
\newcommand{{\ReportRule}}{{\hbox to \headwidth{{\color{{osdagGreen}}\leaders\hrule height 1pt\hfill}}}}
\BeforeBeginEnvironment{{table}}{{\needspace{{{TABLE_BOTTOM_RESERVE}}}}}
\BeforeBeginEnvironment{{longtable}}{{\needspace{{{TABLE_BOTTOM_RESERVE}}}}}
"""


def latex_geometry_package() -> str:
    return rf"\usepackage[{PAGE_GEOMETRY}]{{geometry}}"


def longtable_header(cells: str) -> str:
    """Standard repeated header block for a longtable."""
    return (r"\rowcolor{reportHeader}\color{reportHeaderText}" + TABLE_HEADER_FONT
            + cells + r" \\" + "\n\\hline\n\\endfirsthead\n"
            + r"\rowcolor{reportHeader}\color{reportHeaderText}" + TABLE_HEADER_FONT
            + cells + r" \\" + "\n\\hline\n\\endhead\n")
