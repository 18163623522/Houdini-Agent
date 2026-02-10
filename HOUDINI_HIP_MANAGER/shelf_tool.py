"""
Houdini Shelf Tool Entry Point for HIP Manager
将此代码复制到 Houdini 的 Shelf Tool 中使用
"""

import sys
import os

# 添加工具路径到 Python 路径
tool_path = r"C:\Users\KazamaSuichiku\Desktop\houdini-hip-manager"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

# 导入并运行工具
try:
    # 如果已经导入过，需要重新加载以获取最新更改
    if 'main' in sys.modules:
        import importlib
        import main
        importlib.reload(main)
    else:
        import main
    
    # 运行工具
    main.show_tool()
    
except Exception as e:
    import hou
    hou.ui.displayMessage(
        f"启动 HIP Manager 失败:\n\n{str(e)}", 
        severity=hou.severityType.Error,
        title="HIP Manager Error"
    )
    import traceback
    print("=" * 60)
    print("HIP Manager Error Traceback:")
    print("=" * 60)
    traceback.print_exc()
    print("=" * 60)
