import os
import sys
import hou
from PySide6 import QtWidgets

# 强制重新加载模块，避免缓存问题
def _reload_modules():
    modules_to_reload = [
        'HOUDINI_HIP_MANAGER.ui.ai_tab',
        'HOUDINI_HIP_MANAGER.ui.chat_window',
        'HOUDINI_HIP_MANAGER.ui.widgets',
        'HOUDINI_HIP_MANAGER.ui.dialogs',
        'HOUDINI_HIP_MANAGER.core.hip_manager',
        'HOUDINI_HIP_MANAGER.core.asset_checker',
        'HOUDINI_HIP_MANAGER.utils.ai_client',
        'HOUDINI_HIP_MANAGER.utils.mcp',
    ]
    for mod_name in modules_to_reload:
        if mod_name in sys.modules:
            try:
                import importlib
                importlib.reload(sys.modules[mod_name])
            except Exception:
                pass

from HOUDINI_HIP_MANAGER.core.hip_manager import HipManager

_hip_manager_window = None

def show_tool():
    global _hip_manager_window
    
    # 每次调用时强制重新加载模块
    _reload_modules()
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication([])
    else:
        app = QtWidgets.QApplication.instance()

    try:
        if _hip_manager_window is not None:
            if _hip_manager_window.isVisible():
                _hip_manager_window.minimizeToIcon()
                return _hip_manager_window
            elif hasattr(_hip_manager_window, 'floating_icon') and _hip_manager_window.floating_icon and _hip_manager_window.floating_icon.isVisible():
                _hip_manager_window.floating_icon.hide()
                _hip_manager_window.show()
                _hip_manager_window.raise_()
                _hip_manager_window.activateWindow()
                _hip_manager_window.is_minimized_to_icon = False
                return _hip_manager_window
            else:
                if hasattr(_hip_manager_window, 'floating_icon') and _hip_manager_window.floating_icon:
                    _hip_manager_window.floating_icon.close()
                _hip_manager_window.force_quit = True
                _hip_manager_window.close()
                _hip_manager_window = None
    except Exception:
        pass

    try:
        _hip_manager_window = HipManager()
        _hip_manager_window.show()
        _hip_manager_window.raise_()
        _hip_manager_window.activateWindow()
        return _hip_manager_window
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "错误", f"创建 HIP Manager 窗口失败:\n{e}", QtWidgets.QMessageBox.Ok)
        return None

if __name__ == "__main__":
    show_tool()
