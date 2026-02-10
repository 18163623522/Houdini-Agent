import os
import hou
import hashlib
import tempfile
from datetime import datetime
try:
    from shared.common_utils import get_cache_dir
except Exception:
    def get_cache_dir():
        current = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(current)))
        cache_dir = os.path.join(repo_root, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

# 确保在模块导入时就创建 cache 目录
try:
    _cache_dir_bootstrap = get_cache_dir()
    os.makedirs(_cache_dir_bootstrap, exist_ok=True)
except Exception:
    pass

def get_snapshot_path(hip_path):
    """获取HIP文件快照路径"""
    # 使用仓库 cache 目录
    temp_dir = get_cache_dir()
    hip_hash = hashlib.md5(hip_path.encode("utf-8")).hexdigest()
    return os.path.join(temp_dir, f"hip_preview_{hip_hash}.png")

def has_geometry_in_node(node):
    """检查节点是否包含几何体"""
    try:
        if isinstance(node, hou.SopNode) and node.geometry() and node.geometry().prims():
            return True
        for child in node.children():
            if has_geometry_in_node(child):
                return True
    except hou.OperationFailed:
        pass
    return False

def generate_hip_snapshot(hip_path, force=False):
    """生成HIP文件快照"""
    snapshot_path = get_snapshot_path(hip_path).replace("\\", "/")
    if not force and os.path.exists(snapshot_path):
        return snapshot_path

    if force and os.path.exists(snapshot_path):
        try:
            os.remove(snapshot_path)
        except Exception:
            pass

    current_hip = hou.hipFile.path()
    viewer = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)
    viewport = viewer.curViewport() if viewer else None

    camera_settings = None
    if viewport:
        try:
            camera_settings = viewport.saveView()
        except Exception:
            pass

    try:
        hou.hipFile.load(hip_path, suppress_save_prompt=True, ignore_load_warnings=True)
        has_geometry = any(has_geometry_in_node(node) for node in hou.node("/obj").children())
        if not has_geometry:
            return None

        if viewer and viewport:
            hou.hscript("viewdisplay -e 1")
            try:
                if not viewport.isActive3D():
                    return None
            except AttributeError:
                pass

            if camera_settings:
                try:
                    viewport.restoreView(camera_settings)
                except Exception:
                    hou.hscript("viewhome")
            else:
                hou.hscript("viewhome")

            try:
                viewport.draw()
            except Exception:
                pass

            try:
                fbsettings = viewer.flipbookSettings().stash()
                fbsettings.frameRange((1, 1))
                fbsettings.output(snapshot_path)
                fbsettings.outputToMPlay(False)
                fbsettings.resolution((640, 360))
                viewer.flipbook(settings=fbsettings)
                if os.path.exists(snapshot_path):
                    return snapshot_path
                else:
                    return None
            except Exception:
                return None
        else:
            return None
    except Exception:
        return None
    finally:
        if current_hip and os.path.exists(current_hip):
            try:
                hou.hipFile.load(current_hip, suppress_save_prompt=True, ignore_load_warnings=True)
            except Exception:
                pass

def get_recent_hips(keyword=None, sort_by="time"):
    """获取最近使用的HIP文件列表"""
    try:
        prefs = hou.getenv("HOUDINI_USER_PREF_DIR") or os.getcwd()
    except:
        prefs = os.getcwd()
    
    hist_file = os.path.join(prefs, "file.history")
    if not os.path.exists(hist_file):
        return []

    with open(hist_file, "r", encoding="utf-8") as f:
        files = [line.strip() for line in f if line.strip()]

    hips = []
    for f in files:
        f = str(f)
        if not os.path.exists(f):
            continue
        if f.lower().endswith((".hip", ".hiplc", ".hipnc")):
            if keyword and keyword.lower() not in os.path.basename(f).lower():
                continue
            snapshot = get_snapshot_path(f) if os.path.exists(get_snapshot_path(f)) else None
            hips.append((f, snapshot))

    seen = set()
    unique = []
    for f, snapshot in hips:
        if f not in seen:
            seen.add(f)
            unique.append((f, snapshot, os.path.getsize(f) if os.path.exists(f) else 0, os.path.getmtime(f) if os.path.exists(f) else 0))

    if sort_by == "name":
        unique.sort(key=lambda x: os.path.basename(x[0]).lower())
    elif sort_by == "size":
        unique.sort(key=lambda x: x[2], reverse=True)
    else:
        unique.sort(key=lambda x: x[3], reverse=True)

    return [(f, s) for f, s, _, _ in unique[:1000]]

def safe_load_hip(path, parent_widget=None):
    """安全加载HIP文件"""
    from PySide6 import QtWidgets
    
    path = str(path)
    if not os.path.exists(path):
        QtWidgets.QMessageBox.critical(parent_widget, "错误", f"文件不存在:\n{path}", QtWidgets.QMessageBox.Ok)
        return False
    try:
        hou.hipFile.load(path, suppress_save_prompt=True, ignore_load_warnings=True)
        return True
    except Exception as e:
        QtWidgets.QMessageBox.critical(parent_widget, "错误", f"打开失败:\n{e}", QtWidgets.QMessageBox.Ok)
        return False

def save_hip_file(save_path, parent_widget=None):
    """保存HIP文件"""
    from PySide6 import QtWidgets
    
    try:
        hou.hipFile.save(save_path)
        
        prefs = hou.getenv("HOUDINI_USER_PREF_DIR") or os.getcwd()
        hist_file = os.path.join(prefs, "file.history")
        with open(hist_file, "a", encoding="utf-8") as f:
            f.write(f"{save_path}\n")
        
        from .hip_utils import generate_hip_snapshot
        snapshot = generate_hip_snapshot(save_path, force=True)
        snapshot = generate_hip_snapshot(save_path, force=True)
        return snapshot
    except Exception as e:
        QtWidgets.QMessageBox.critical(parent_widget, "错误", f"保存失败:\n{e}", QtWidgets.QMessageBox.Ok)
        return None

def delete_hip_file(hip_path, parent_widget=None):
    """删除HIP文件及其快照"""
    from PySide6 import QtWidgets
    
    snapshot_path = get_snapshot_path(hip_path)
    try:
        if os.path.exists(hip_path):
            os.remove(hip_path)
        if os.path.exists(snapshot_path):
            os.remove(snapshot_path)
        prefs = hou.getenv("HOUDINI_USER_PREF_DIR") or os.getcwd()
        hist_file = os.path.join(prefs, "file.history")
        if os.path.exists(hist_file):
            with open(hist_file, "r", encoding="utf-8") as f:
                files = [line.strip() for line in f if line.strip() and line.strip() != hip_path]
            with open(hist_file, "w", encoding="utf-8") as f:
                for f_path in files:
                    f.write(f"{f_path}\n")
        return True
    except Exception as e:
        QtWidgets.QMessageBox.critical(parent_widget, "错误", f"删除失败 {os.path.basename(hip_path)}:\n{e}", QtWidgets.QMessageBox.Ok)
        return False
