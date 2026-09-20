"""
Offscreen GUI Rendering & View Export Engine for Mount Angel Library.
Standardized on the maker framework headless rendering pipeline.
"""

import os
import time

try:
    import FreeCAD
    import FreeCADGui
    HAS_GUI = bool(getattr(FreeCAD, "GuiUp", False))
except Exception:
    FreeCADGui = None
    HAS_GUI = False


def is_gui_up():
    """Dynamically checks whether FreeCAD's GUI is running."""
    try:
        import FreeCAD
        import FreeCADGui
        if FreeCADGui is None:
            return False
        if bool(getattr(FreeCAD, "GuiUp", False)):
            return True
        return hasattr(FreeCADGui, "getMainWindow") and FreeCADGui.getMainWindow() is not None
    except Exception:
        return False


def cleanup_backup_files(path_or_dir):
    """Removes any stray .FCBak files in the specified path or directory."""
    if os.path.isfile(path_or_dir):
        directory = os.path.dirname(path_or_dir)
        basename = os.path.splitext(os.path.basename(path_or_dir))[0]
    else:
        directory = path_or_dir
        basename = None

    if not directory or not os.path.exists(directory):
        return

    try:
        for fname in os.listdir(directory):
            if fname.endswith(".FCBak"):
                if basename is None or fname.startswith(basename):
                    fpath = os.path.join(directory, fname)
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass
    except Exception:
        pass


def configure_freecad_preferences():
    """
    Applies performance and lifecycle preferences to FreeCAD:
    - Disables view transition animations to prevent snapshot lag.
    - Disables backup file generation (CreateBackupFiles = False).
    """
    if not is_gui_up():
        return

    try:
        param_view = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
        param_view.SetBool("EnableAnimation", False)
        param_view.SetInt("TransitionTime", 0)
    except Exception as e:
        print(f"Preference note (View): {e}")

    try:
        param_doc = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document")
        param_doc.SetBool("CreateBackupFiles", False)
        param_doc.SetInt("CountBackupFiles", 0)
    except Exception as e:
        print(f"Preference note (Document): {e}")


def _hide_auxiliary_markers(gui_doc):
    """Hides origin axes, datums, and auxiliary wireframes for clean architectural renders."""
    if not gui_doc:
        return
    app_doc = getattr(gui_doc, "Document", None)
    if not app_doc:
        return
    for obj in app_doc.Objects:
        type_id = getattr(obj, "TypeId", "")
        name = getattr(obj, "Name", "").lower()
        is_hidden = (
            type_id in ("App::Origin", "App::Line", "App::Plane", "App::Point")
            or "origin" in name
            or "_axis" in name
            or "_plane" in name
            or name in ("x_axis", "y_axis", "z_axis", "xy_plane", "xz_plane", "yz_plane")
        )
        if is_hidden:
            try:
                g_o = gui_doc.getObject(obj.Name)
                if g_o:
                    g_o.Visibility = False
            except Exception:
                pass


def export_standard_views(gui_doc, base_prefix, width=1920, height=1080, bg_type="White", camera_type="Perspective"):
    """
    Exports standard architectural projections:
    - Isometric (Home Perspective View: `<base_prefix>.png`)
    - Top (Plan View: `<base_prefix>_top.png`)
    - Front (South Elevation: `<base_prefix>_front.png`)
    - Back (North Elevation: `<base_prefix>_back.png`)
    - Left (West Elevation: `<base_prefix>_left.png`)
    - Right (East Elevation: `<base_prefix>_right.png`)
    """
    if not is_gui_up() or not gui_doc:
        return

    FreeCADGui.updateGui()
    view = gui_doc.activeView()
    if not view:
        return

    configure_freecad_preferences()
    _hide_auxiliary_markers(gui_doc)

    try:
        view.setCameraType(camera_type)
    except Exception as e:
        print(f"Camera type note: {e}")

    back_fn = getattr(view, "viewRear", getattr(view, "viewBack", lambda: None))
    views_to_export = [
        ("top", view.viewTop, "Top Plan View"),
        ("front", view.viewFront, "South Elevation View"),
        ("back", back_fn, "North Elevation View"),
        ("left", view.viewLeft, "West Side Elevation View"),
        ("right", view.viewRight, "East Side Elevation View"),
        ("home", view.viewIsometric, "Home Perspective View"),
    ]

    out_dir = os.path.dirname(base_prefix)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    for name, set_view_func, label in views_to_export:
        if not set_view_func:
            continue
        try:
            set_view_func()
            FreeCADGui.updateGui()
            time.sleep(0.2)
            FreeCADGui.updateGui()

            view.fitAll()
            FreeCADGui.updateGui()
            time.sleep(0.2)
            FreeCADGui.updateGui()

            if name == "home":
                filepath = f"{base_prefix}.png"
            else:
                filepath = f"{base_prefix}_{name}.png"

            view.saveImage(filepath, width, height, bg_type)
            print(f"Exported {label}: {filepath}")
        except Exception as e:
            print(f"Error rendering {name} view: {e}")

    try:
        view.setCameraType(camera_type)
        view.viewIsometric()
        FreeCADGui.updateGui()
        time.sleep(0.1)
        view.fitAll()
        FreeCADGui.updateGui()
    except Exception:
        pass


def save_model(doc, fc_path, camera_type="Perspective"):
    """
    Saves the FreeCAD document with active viewport framed in Isometric Perspective,
    and cleans up .FCBak files.
    """
    configure_freecad_preferences()

    if is_gui_up() and hasattr(FreeCADGui, "getDocument"):
        try:
            gui_d = FreeCADGui.getDocument(doc.Name)
            if gui_d:
                view = gui_d.activeView()
                if view:
                    view.setCameraType(camera_type)
                    view.viewIsometric()
                    FreeCADGui.updateGui()
                    time.sleep(0.1)
                    view.fitAll()
                    FreeCADGui.updateGui()
        except Exception:
            pass

    doc.recompute()
    out_dir = os.path.dirname(fc_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    doc.saveAs(fc_path)
    print(f"Saved model: {fc_path}")
    cleanup_backup_files(fc_path)


def close_model(doc_or_name):
    """Cleanly closes document and flushes GUI events."""
    name = doc_or_name if isinstance(doc_or_name, str) else getattr(doc_or_name, "Name", str(doc_or_name))
    try:
        FreeCAD.closeDocument(name)
        if is_gui_up():
            FreeCADGui.updateGui()
            time.sleep(0.1)
    except Exception as e:
        print(f"Note closing document {name}: {e}")
