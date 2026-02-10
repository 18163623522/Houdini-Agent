"""
🚀 HIP Manager - Houdini Shelf Tool 快速脚本
复制此代码到 Houdini Shelf Tool 中即可使用
"""

import sys
import os

# 工具路径
tool_path = r"C:\Users\KazamaSuichiku\Desktop\houdini-hip-manager"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

# 重新加载模块（支持热更新）
if 'main' in sys.modules:
    import importlib
    import main
    importlib.reload(main)
else:
    import main

# 启动工具
main.show_tool()
