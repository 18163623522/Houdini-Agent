"""
Houdini Asset Manager - 启动器
Houdini 资产管理工具
"""

import sys
import os

# ============================================================
# 强制使用本地 lib 目录中的依赖库
# ============================================================
_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_LIB_DIR = os.path.join(_ROOT_DIR, 'lib')

if os.path.exists(_LIB_DIR):
    # 移除已存在的路径（如果有），然后添加到最前面
    if _LIB_DIR in sys.path:
        sys.path.remove(_LIB_DIR)
    sys.path.insert(0, _LIB_DIR)

# ============================================================

def detect_dcc():
    """检测当前运行的 DCC 软件"""
    try:
        import hou
        return "houdini"
    except ImportError:
        pass
    
    return None

def launch_houdini_manager():
    """启动 Houdini HIP Manager"""
    tool_path = os.path.join(os.path.dirname(__file__), "HOUDINI_HIP_MANAGER")
    if tool_path not in sys.path:
        sys.path.insert(0, tool_path)
    
    try:
        # 重新加载以支持热更新
        if 'main' in sys.modules:
            import importlib
            import main
            importlib.reload(main)
        else:
            import main
        
        return main.show_tool()
    except Exception as e:
        print(f"启动 Houdini HIP Manager 失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def launch():
    """自动检测并启动管理器"""
    dcc = detect_dcc()
    
    if dcc == "houdini":
        print("检测到 Houdini 环境，启动 HIP Manager...")
        return launch_houdini_manager()
    else:
        print("错误：未检测到 Houdini 环境")
        print("请在 Houdini 中运行此工具。")
        return None

# 全局变量存储窗口实例
_manager_window = None

def show_tool():
    """统一入口函数"""
    global _manager_window
    _manager_window = launch()
    return _manager_window

if __name__ == "__main__":
    show_tool()
