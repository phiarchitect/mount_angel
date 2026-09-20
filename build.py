"""
Master Build Script for Mount Angel Abbey Library CAD Model.
Executes headlessly via: ./scripts/run_freecad.sh build.py
"""

import os
import sys

repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import FreeCAD
try:
    import FreeCADGui
    FreeCADGui.showMainWindow()
    HAS_GUI = True
except Exception as e:
    print(f"FreeCADGui note: {e}")
    FreeCADGui = None
    HAS_GUI = False

from phiarchitect.mountangel.model import build_library_model
from phiarchitect.mountangel.render import save_model, export_standard_views, close_model

def build_standalone():
    print("================================================================================")
    print("BUILDING MOUNT ANGEL ABBEY LIBRARY (ALVAR AALTO) - 3D PARAMETRIC MODEL")
    print("================================================================================")

    doc_name = "MountAngelLibrary"
    doc = FreeCAD.newDocument(doc_name)
    doc.Label = "Mount Angel Abbey Library"

    # Assemble complete building geometry
    build_library_model(doc)
    doc.recompute()

    # Output paths
    repo_root = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(repo_root, "docs", "model")
    os.makedirs(out_dir, exist_ok=True)

    fc_path = os.path.join(out_dir, "mount_angel.FCStd")
    render_prefix = os.path.join(out_dir, "mount_angel")

    # Export high-res architectural projection views
    if hasattr(FreeCADGui, "getDocument"):
        gui_d = FreeCADGui.getDocument(doc.Name)
        if gui_d:
            print("\nCapturing multi-view projection renders...")
            export_standard_views(gui_d, render_prefix, width=1920, height=1080)

    # Save master FreeCAD document
    save_model(doc, fc_path)
    close_model(doc_name)

    print("\n================================================================================")
    print(f"BUILD SUCCESSFUL!")
    print(f"Model saved to:   {fc_path}")
    print(f"Renders saved to: {out_dir}/")
    print("================================================================================")


if __name__ == "__main__":
    try:
        build_standalone()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os._exit(0)
