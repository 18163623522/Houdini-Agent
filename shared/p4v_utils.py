import os
import subprocess
import winreg


def find_p4v_executable():
    """查找 P4V 可执行文件路径（Windows）。"""
    common_paths = [
        r"C:\\Program Files\\Perforce\\p4v.exe",
        r"C:\\Program Files (x86)\\Perforce\\p4v.exe",
        r"C:\\Program Files\\Helix Visual Client\\p4v.exe",
        r"C:\\Program Files (x86)\\Helix Visual Client\\p4v.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    # 注册表
    try:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Perforce\\p4v") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                p4v_path = os.path.join(install_path, "p4v.exe")
                if os.path.exists(p4v_path):
                    return p4v_path
        except (FileNotFoundError, OSError):
            pass
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Perforce\\p4v") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                p4v_path = os.path.join(install_path, "p4v.exe")
                if os.path.exists(p4v_path):
                    return p4v_path
        except (FileNotFoundError, OSError):
            pass
    except Exception:
        pass

    # PATH 中查找
    try:
        result = subprocess.run(['where', 'p4v'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            p4v_path = result.stdout.strip().splitlines()[0]
            if os.path.exists(p4v_path):
                return p4v_path
    except Exception:
        pass

    # 环境变量
    p4v_home = os.environ.get('P4V_HOME')
    if p4v_home:
        p4v_path = os.path.join(p4v_home, 'p4v.exe')
        if os.path.exists(p4v_path):
            return p4v_path

    return None


def is_p4v_running():
    """粗略检查 P4V 是否在运行（不依赖 psutil）。"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq p4v.exe'], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and 'p4v.exe' in result.stdout:
            return True
    except Exception:
        pass
    return False


def launch_p4v(parent_widget=None):
    """启动 P4V 程序；若已在运行直接返回 already_running。

    返回：True | False | "already_running"
    """
    try:
        from PySide6 import QtWidgets
    except Exception:
        QtWidgets = None

    if is_p4v_running():
        return "already_running"

    p4v_path = find_p4v_executable()
    if not p4v_path:
        if QtWidgets:
            QtWidgets.QMessageBox.warning(
                parent_widget,
                "P4V 未找到",
                "未找到 Perforce P4V 程序。\n\n请确认已安装 Perforce Visual Client (P4V)。",
                QtWidgets.QMessageBox.Ok,
            )
        return False

    try:
        subprocess.Popen([p4v_path], shell=True)
        return True
    except Exception as e:
        if QtWidgets:
            QtWidgets.QMessageBox.critical(
                parent_widget,
                "启动失败",
                f"启动 P4V 失败:\n{e}",
                QtWidgets.QMessageBox.Ok,
            )
        return False
