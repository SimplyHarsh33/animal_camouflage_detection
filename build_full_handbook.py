# -*- coding: utf-8 -*-
"""
Master Builder: Compiles HTML and generates PDF using headless Microsoft Edge.
"""

import os
import sys
import subprocess
import time

from build_sections import get_cover, get_toc
from sections_ch1_to_ch3 import get_ch1, get_ch2, get_ch3
from sections_ch4_to_ch6 import get_ch4, get_ch5, get_ch6
from sections_ch7_to_ch9 import get_ch7, get_ch8, get_ch9
from sections_ch10_viva import get_ch10

OUTPUT_HTML = os.path.abspath("Autonomous_Camouflage_Animal_Detection_Master_Handbook.html")
OUTPUT_PDF = os.path.abspath("Autonomous_Camouflage_Animal_Detection_Master_Handbook.pdf")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print("[1/3] Assembling HTML Document from Modular Chapters...")

html_header = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Autonomous Camouflage Animal Detection — Master Technical Handbook</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {
    size: A4 portrait;
    margin: 16mm 14mm 16mm 14mm;
    @bottom-right {
      content: "Page " counter(page);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 8pt;
      color: #64748b;
    }
    @bottom-left {
      content: "Autonomous Camouflage Animal Detection | ROS 2 & Gazebo Technical Handbook";
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 8pt;
      color: #64748b;
    }
  }

  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    font-size: 10pt;
    line-height: 1.55;
    margin: 0;
    padding: 0;
  }

  .page-break {
    page-break-after: always;
    break-after: page;
  }

  .avoid-break {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* Cover Page */
  .cover-container {
    height: 100%;
    min-height: 250mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 10mm 5mm;
  }

  .cover-badge {
    display: inline-block;
    padding: 6px 14px;
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
    border-radius: 9999px;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 18px;
  }

  .cover-title {
    font-size: 27pt;
    font-weight: 800;
    line-height: 1.15;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0 0 12px 0;
  }

  .cover-title span {
    color: #059669;
  }

  .cover-subtitle {
    font-size: 13pt;
    font-weight: 500;
    color: #475569;
    line-height: 1.45;
    margin: 0 0 25px 0;
    max-width: 90%;
  }

  .cover-divider {
    height: 4px;
    width: 90px;
    background: linear-gradient(90deg, #059669, #10b981, #34d399);
    border-radius: 2px;
    margin-bottom: 25px;
  }

  .cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-top: 20px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
  }

  .meta-label {
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748b;
    font-weight: 700;
    margin-bottom: 2px;
  }

  .meta-val {
    font-size: 9.5pt;
    font-weight: 600;
    color: #0f172a;
  }

  .cover-highlights {
    margin-top: 24px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .highlight-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
  }

  .highlight-card h4 {
    margin: 0 0 6px 0;
    font-size: 9pt;
    font-weight: 700;
    color: #065f46;
  }

  .highlight-card p {
    margin: 0;
    font-size: 8pt;
    color: #64748b;
    line-height: 1.4;
  }

  .cover-footer {
    border-top: 1px solid #e2e8f0;
    padding-top: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 8.5pt;
    color: #64748b;
  }

  /* Typography & Structure */
  h1.section-title {
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin: 22px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  h1.section-title .section-num {
    background: #059669;
    color: #ffffff;
    font-size: 9pt;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
  }

  h2.sub-title {
    font-size: 12pt;
    font-weight: 700;
    color: #1e293b;
    margin: 16px 0 8px 0;
  }

  h3.sub-sub-title {
    font-size: 10.5pt;
    font-weight: 600;
    color: #334155;
    margin: 12px 0 6px 0;
  }

  p {
    margin: 0 0 9px 0;
    text-align: justify;
  }

  ul, ol {
    margin: 4px 0 9px 20px;
    padding: 0;
  }

  li {
    margin-bottom: 4px;
  }

  /* Callout Boxes */
  .callout {
    border-radius: 8px;
    padding: 12px 14px;
    margin: 12px 0;
    border-left: 4px solid;
    font-size: 9pt;
  }

  .callout-info {
    background: #f0fdf4;
    border-left-color: #10b981;
    color: #065f46;
  }

  .callout-warning {
    background: #fffbeb;
    border-left-color: #f59e0b;
    color: #92400e;
  }

  .callout-navy {
    background: #f8fafc;
    border-left-color: #0284c7;
    color: #0369a1;
  }

  .callout-danger {
    background: #fef2f2;
    border-left-color: #ef4444;
    color: #991b1b;
  }

  .callout-title {
    font-weight: 700;
    font-size: 9.5pt;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  /* Tables */
  table.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 8.5pt;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    overflow: hidden;
  }

  table.custom-table th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 8px 10px;
    font-size: 8.5pt;
  }

  table.custom-table td {
    padding: 7px 10px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }

  table.custom-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  table.custom-table tr:last-child td {
    border-bottom: none;
  }

  .table-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
  }

  .badge-green { background: #dcfce7; color: #166534; }
  .badge-blue { background: #e0f2fe; color: #075985; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-purple { background: #f3e8ff; color: #6b21a8; }
  .badge-gray { background: #f1f5f9; color: #334155; }

  /* Code Blocks */
  .code-block {
    background: #0f172a;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 8pt;
    line-height: 1.45;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 10px 0;
    overflow-x: auto;
    border: 1px solid #1e293b;
    white-space: pre-wrap;
  }

  .code-header {
    background: #1e293b;
    color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.5pt;
    padding: 4px 10px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border-bottom: 1px solid #334155;
    margin: 10px 0 0 0;
    display: flex;
    justify-content: space-between;
  }

  .code-header + .code-block {
    margin-top: 0;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  code.inline-code {
    font-family: 'JetBrains Mono', monospace;
    background: #f1f5f9;
    color: #0f172a;
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 8.5pt;
    border: 1px solid #e2e8f0;
  }

  /* Math equation card */
  .math-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 10px 0;
    text-align: center;
  }

  .math-equation {
    font-family: 'Times New Roman', Times, serif;
    font-style: italic;
    font-size: 11pt;
    color: #0f172a;
    margin: 4px 0;
  }

  .math-explanation {
    font-size: 8pt;
    color: #64748b;
    margin-top: 4px;
    font-style: normal;
  }

  /* SVG Diagrams Container */
  .diagram-container {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px;
    margin: 14px 0;
    text-align: center;
  }

  .diagram-caption {
    font-size: 8pt;
    color: #64748b;
    font-weight: 600;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Viva Card Styling */
  .viva-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px;
    margin: 12px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .viva-q {
    font-size: 9.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }

  .viva-badge {
    background: #0f766e;
    color: #ffffff;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .viva-concept {
    font-size: 8pt;
    font-weight: 600;
    color: #0369a1;
    background: #f0f9ff;
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
    display: inline-block;
  }

  .viva-ans {
    font-size: 9pt;
    color: #334155;
    line-height: 1.5;
  }

  .viva-ans ul, .viva-ans ol {
    margin: 4px 0 4px 18px;
    padding: 0;
  }

  .viva-ans li {
    margin-bottom: 3px;
  }

  /* Two Column Grid */
  .two-col {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 10px 0;
  }

  .card-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
  }

  .card-box h4 {
    margin: 0 0 6px 0;
    font-size: 9.5pt;
    color: #0f172a;
    font-weight: 700;
  }
</style>
</head>
<body>
"""

html_footer = """
</body>
</html>
"""

full_content = (
    html_header
    + get_cover()
    + get_toc()
    + get_ch1()
    + get_ch2()
    + get_ch3()
    + get_ch4()
    + get_ch5()
    + get_ch6()
    + get_ch7()
    + get_ch8()
    + get_ch9()
    + get_ch10()
    + html_footer
)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"[SUCCESS] HTML document compiled: {OUTPUT_HTML} ({os.path.getsize(OUTPUT_HTML)} bytes)")

print("\n[2/3] Rendering Print-Ready PDF with Microsoft Edge Headless Engine...")
cmd = [
    EDGE_PATH,
    "--headless=new",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={OUTPUT_PDF}",
    "--no-pdf-header-footer",
    OUTPUT_HTML
]

res = subprocess.run(cmd, capture_output=True, text=True)
print(f"Edge Process Return Code: {res.returncode}")

time.sleep(2)

if os.path.exists(OUTPUT_PDF):
    size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"\n[3/3] PDF GENERATED SUCCESSFULLY!")
    print(f"File Path: {OUTPUT_PDF}")
    print(f"File Size: {size_mb:.2f} MB")
else:
    print("[ERROR] PDF generation failed!")
    sys.exit(1)
