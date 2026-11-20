# -*- coding: utf-8 -*-
"""
Master Compiler for the 4-Subsystem Technical Handbook.
Generates a human-readable HTML document with intuitive formula boxes,
no member counts, and compiles it into a master PDF using Microsoft Edge headless.
"""

import os
import sys
import subprocess
import time

from team_structure import get_cover, get_toc
from part1_robot_kinematics import get_part1
from part2_gazebo_procedural import get_part2
from part3_vision_perception import get_part3
from part4_autonomy_training import get_part4

OUTPUT_HTML = os.path.abspath("Autonomous_Camouflage_Animal_Detection_Team_Master_Handbook.html")
OUTPUT_PDF = os.path.abspath("Autonomous_Camouflage_Animal_Detection_Team_Master_Handbook.pdf")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print("[1/3] Assembling Subsystem Division Master Document...")

html_header = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Autonomous Camouflage Animal Detection — Master Technical Handbook</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {
    size: A4 portrait;
    margin: 18mm 15mm 18mm 15mm;
    @bottom-right {
      content: "Page " counter(page);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 9pt;
      color: #64748b;
    }
    @bottom-left {
      content: "Autonomous Camouflage Animal Detection | Technical Reference & Defense Manual";
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 9pt;
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
    font-size: 11pt;
    line-height: 1.62;
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
    height: 245mm;
    max-height: 250mm;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 6mm 4mm;
    page-break-after: always;
    break-after: page;
  }

  .cover-badge {
    display: inline-block;
    padding: 6px 14px;
    background: #ecfdf5;
    color: #065f46;
    border: 1.5px solid #a7f3d0;
    border-radius: 9999px;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .cover-title {
    font-size: 26pt;
    font-weight: 800;
    line-height: 1.15;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0 0 10px 0;
  }

  .cover-title span {
    color: #059669;
  }

  .cover-subtitle {
    font-size: 11.5pt;
    font-weight: 500;
    color: #475569;
    line-height: 1.45;
    margin: 0 0 16px 0;
  }

  .cover-divider {
    height: 4px;
    width: 90px;
    background: linear-gradient(90deg, #059669, #10b981, #34d399);
    border-radius: 2px;
    margin-bottom: 16px;
  }

  .cover-team-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 4px;
  }

  .team-box-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 10px 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .border-green { border: 2px solid #10b981; }
  .border-purple { border: 2px solid #9333ea; }
  .border-amber { border: 2px solid #f59e0b; }
  .border-blue { border: 2px solid #0284c7; }

  .team-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }

  .team-pill {
    font-size: 8pt;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 999px;
    text-transform: uppercase;
  }

  .pill-green { background: #dcfce7; color: #166534; }
  .pill-purple { background: #f3e8ff; color: #6b21a8; }
  .pill-amber { background: #fef3c7; color: #92400e; }
  .pill-blue { background: #e0f2fe; color: #075985; }

  .team-tag {
    font-size: 7.5pt;
    font-weight: 600;
    color: #64748b;
  }

  .team-card-title {
    margin: 2px 0 4px 0;
    font-size: 9.5pt;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.3;
  }

  .team-card-desc {
    margin: 0 0 6px 0;
    font-size: 8.5pt;
    color: #475569;
    line-height: 1.35;
  }

  .team-files-tag {
    font-size: 7.5pt;
    color: #334155;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2px 6px;
  }

  .cover-footer {
    border-top: 1px solid #e2e8f0;
    padding-top: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 8.5pt;
    color: #64748b;
  }

  /* Part Header Banners */
  .part-header-card {
    border-radius: 12px;
    padding: 18px 20px;
    margin: 10px 0 20px 0;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }

  .part-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 9pt;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
  }

  .badge-green { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
  .badge-purple { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
  .badge-amber { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
  .badge-blue { background: #e0f2fe; color: #075985; border: 1px solid #bae6fd; }

  .part-title {
    margin: 0 0 8px 0;
    font-size: 19pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
  }

  .part-subtitle {
    margin: 0;
    font-size: 11pt;
    color: #475569;
    line-height: 1.5;
  }

  /* Typography & Structure */
  h1.section-title {
    font-size: 17pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2.5px solid #e2e8f0;
    padding-bottom: 8px;
    margin: 22px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  h1.section-title .section-num {
    background: #059669;
    color: #ffffff;
    font-size: 9.5pt;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
  }

  h2.sub-title {
    font-size: 13.5pt;
    font-weight: 700;
    color: #0f172a;
    margin: 18px 0 10px 0;
  }

  h3.sub-sub-title {
    font-size: 11.5pt;
    font-weight: 700;
    color: #334155;
    margin: 14px 0 8px 0;
  }

  p {
    margin: 0 0 11px 0;
    text-align: justify;
  }

  ul, ol {
    margin: 6px 0 12px 24px;
    padding: 0;
  }

  li {
    margin-bottom: 5px;
  }

  /* Callouts */
  .callout {
    border-radius: 10px;
    padding: 13px 16px;
    margin: 14px 0;
    border-left: 5px solid;
    font-size: 10.5pt;
    line-height: 1.55;
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

  .callout-title {
    font-weight: 800;
    font-size: 11pt;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* Tables */
  table.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 10pt;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    overflow: hidden;
  }

  table.custom-table th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 9px 12px;
    font-size: 10pt;
  }

  table.custom-table td {
    padding: 8px 12px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
    line-height: 1.5;
  }

  table.custom-table tr:nth-child(even) td {
    background: #f8fafc;
  }

  table.custom-table tr:last-child td {
    border-bottom: none;
  }

  .table-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 5px;
    font-size: 8.5pt;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Code Blocks */
  .code-block {
    background: #0f172a;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5pt;
    line-height: 1.5;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
    overflow-x: auto;
    border: 1px solid #1e293b;
    white-space: pre-wrap;
  }

  .code-header {
    background: #1e293b;
    color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 8.5pt;
    padding: 6px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border-bottom: 1px solid #334155;
    margin: 12px 0 0 0;
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
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 9.5pt;
    border: 1px solid #cbd5e1;
  }

  /* Human-Readable Formula Card */
  .formula-box {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-left: 5px solid #059669;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 14px 0;
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .formula-title {
    font-size: 10.5pt;
    font-weight: 800;
    color: #065f46;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .formula-main {
    font-size: 12.5pt;
    font-weight: 700;
    color: #0f172a;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 9px 14px;
    margin: 6px 0;
    text-align: center;
    line-height: 1.45;
  }

  .formula-details {
    font-size: 10pt;
    color: #334155;
    margin-top: 6px;
    line-height: 1.5;
  }

  .formula-explanation {
    font-size: 9.5pt;
    color: #475569;
    background: #f1f5f9;
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 8px;
    line-height: 1.5;
  }

  /* SVG Diagrams Container */
  .diagram-container {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    margin: 16px 0;
    text-align: center;
  }

  .diagram-caption {
    font-size: 9pt;
    color: #64748b;
    font-weight: 700;
    margin-top: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Viva Card Styling */
  .viva-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 15px 18px;
    margin: 15px 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .viva-q {
    font-size: 11.5pt;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }

  .viva-badge {
    background: #0f766e;
    color: #ffffff;
    font-size: 8.5pt;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 5px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .viva-concept {
    font-size: 9pt;
    font-weight: 700;
    color: #0369a1;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 10px;
    display: inline-block;
  }

  .viva-ans {
    font-size: 10.5pt;
    color: #334155;
    line-height: 1.6;
  }

  .viva-ans ul, .viva-ans ol {
    margin: 6px 0 6px 20px;
    padding: 0;
  }

  .viva-ans li {
    margin-bottom: 4px;
  }

  /* Two Column Grid */
  .two-col {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin: 12px 0;
  }

  .card-box {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
  }

  .card-box h4 {
    margin: 0 0 8px 0;
    font-size: 11pt;
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

full_team_document = (
    html_header
    + get_cover()
    + get_toc()
    + get_part1()
    + get_part2()
    + get_part3()
    + get_part4()
    + html_footer
)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(full_team_document)

print(f"[SUCCESS] HTML compiled: {OUTPUT_HTML} ({os.path.getsize(OUTPUT_HTML)} bytes)")

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
print(f"Edge Return Code: {res.returncode}")

time.sleep(2)

if os.path.exists(OUTPUT_PDF):
    size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"\n[3/3] PDF GENERATED SUCCESSFULLY!")
    print(f"File Path: {OUTPUT_PDF}")
    print(f"File Size: {size_mb:.2f} MB")
else:
    print("[ERROR] PDF generation failed!")
    sys.exit(1)
