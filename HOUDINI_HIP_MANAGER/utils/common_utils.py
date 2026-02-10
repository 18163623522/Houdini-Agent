import os
from datetime import datetime
try:
    from shared.common_utils import get_config_dir
except Exception:
    # 兜底：根据当前文件位置推断 repo 根并创建 config 目录
    def get_config_dir():
        current = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(current)))
        config_dir = os.path.join(repo_root, 'config')
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

def load_config(config_name):
    """加载配置文件（仅使用统一的 repo/config 路径）。"""
    try:
        config_dir = get_config_dir()
        path = os.path.join(config_dir, f"houdini_{config_name}.ini")
        config = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.strip().split(":", 1)
                        config[key] = value
        return config, path
    except Exception:
        return {}, ""

def save_config(config_name, config):
    """保存配置文件（仅写入统一的 repo/config 路径）。"""
    try:
        config_dir = get_config_dir()
        path = os.path.join(config_dir, f"houdini_{config_name}.ini")
        with open(path, "w", encoding="utf-8") as f:
            for key, value in config.items():
                f.write(f"{key}:{value}\n")
        return True, path
    except Exception:
        return False, ""

def get_history_path(history_name):
    """获取历史记录文件路径"""
    history_dir = get_config_dir()
    return os.path.join(history_dir, f"hou_{history_name}_history.txt")

def add_to_history(history_name, entry):
    """添加记录到历史文件"""
    try:
        history_path = get_history_path(history_name)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(f"{entry}|{timestamp}\n")
        return True
    except Exception:
        return False

def load_history(history_name):
    """加载历史记录"""
    try:
        history_path = get_history_path(history_name)
        if not os.path.exists(history_path):
            return []
            
        with open(history_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        history = []
        for line in lines:
            if "|" in line:
                parts = line.strip().split("|")
                history.append(parts)
                
        return history
    except Exception:
        return []
