#!/usr/bin/env python
"""
Quick startup script for CreativeApp UI
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    """Start the CreativeApp UI"""
    
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("🚀 CreativeApp - AI Dream Analysis System")
    print("=" * 60)
    print()
    
    # Check if running from correct directory
    if not (project_root / "src" / "ui" / "app.py").exists():
        print("❌ Error: Run this script from the project root directory")
        sys.exit(1)
    
    print("✅ Starting Gradio interface...")
    print("📍 The app will be available at: http://localhost:7860")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Start the app
        subprocess.run(
            [sys.executable, "src/ui/app.py"],
            cwd=project_root,
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n✅ Shutting down CreativeApp...")
        sys.exit(0)

if __name__ == "__main__":
    main()
