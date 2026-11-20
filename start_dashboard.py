#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-Click Launcher for the Wildlife Camouflage AI Mission Control Dashboard.
Opens the web browser automatically at http://localhost:5000.
"""

import sys
import os
import time
import webbrowser
import threading

# Add workspace root to Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.app import app, main

def open_browser():
    time.sleep(1.2)
    url = "http://localhost:5000"
    print(f"\n[INFO] Opening Mission Control Dashboard in your browser: {url}\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == '__main__':
    # Launch browser after a short delay
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run dashboard main
    main()
