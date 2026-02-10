import os
import subprocess
import winreg
import psutil

def find_p4v_executable():
    """查找P4V可执行文件路径"""
    common_paths = [
        r"C:\Program Files\Perforce\p4v.exe",
        r"C:\Program Files (x86)\Perforce\p4v.exe",
        r"C:\Program Files\Helix Visual Client\p4v.exe",
        r"C:\Program Files (x86)\Helix Visual Client\p4v.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    try:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Perforce\p4v") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                p4v_path = os.path.join(install_path, "p4v.exe")
                if os.path.exists(p4v_path):
                    return p4v_path
        except (FileNotFoundError, OSError):
            pass
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Perforce\p4v") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                p4v_path = os.path.join(install_path, "p4v.exe")
                if os.path.exists(p4v_path):
                    return p4v_path
        except (FileNotFoundError, OSError):
            pass
    except Exception:
        pass
    
    try:
        result = subprocess.run(['where', 'p4v'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            p4v_path = result.stdout.strip().split('\n')[0]
            if os.path.exists(p4v_path):
                return p4v_path
    except Exception:
        pass
    
    p4v_home = os.environ.get('P4V_HOME')
    if p4v_home:
        p4v_path = os.path.join(p4v_home, "p4v.exe")
        if os.path.exists(p4v_path):
            return p4v_path
    
    return None

def is_p4v_running():
    """检查P4V是否正在运行"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                if proc_name == 'p4v.exe' or proc_name == 'p4v':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq p4v.exe'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0 and 'p4v.exe' in result.stdout:
                return True
        except Exception:
            pass
    except Exception:
        pass
    
    return False

def launch_p4v(parent_widget=None):
    """启动P4V程序"""
    from PySide6 import QtWidgets
    
    if is_p4v_running():
        return "already_running"
    
    p4v_path = find_p4v_executable()
    if not p4v_path:
        QtWidgets.QMessageBox.warning(
            parent_widget, 
            "P4V未找到", 
            "未找到Perforce P4V程序。\n\n请确保已安装Perforce Visual Client (P4V)。",
            QtWidgets.QMessageBox.Ok
        )
        return False
    
    try:
        subprocess.Popen([p4v_path], shell=True)
        return True
    except Exception as e:
        QtWidgets.QMessageBox.critical(
            parent_widget, 
            "启动失败", 
            f"启动P4V失败:\n{str(e)}",
            QtWidgets.QMessageBox.Ok
        )
        return False
