# 📚 Houdini Shelf Tool 设置指南

## 🎯 快速设置步骤

### 方法一：创建 Shelf Tool（推荐）

#### 1️⃣ 打开 Houdini

#### 2️⃣ 创建新的 Shelf Tool
- 在 Houdini 顶部的 Shelf 区域右键点击
- 选择 **"New Tool..."** 或 **"新建工具..."**

#### 3️⃣ 配置 Tool 信息
- **Name（名称）**：`hip_manager`
- **Label（标签）**：`HIP Manager`
- **Icon（图标）**：可以选择一个喜欢的图标，或使用默认

#### 4️⃣ 复制脚本代码
在 **Script** 标签页中，粘贴以下代码：

```python
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
```

#### 5️⃣ 保存并使用
- 点击 **"Accept"** 或 **"确定"** 保存
- 现在你可以在 Shelf 上看到 **HIP Manager** 按钮
- 点击按钮即可启动工具！

---

### 方法二：Python Shell（临时测试）

如果你只是想临时测试工具，可以在 Houdini 的 Python Shell 中运行：

#### 1️⃣ 打开 Python Shell
- 在 Houdini 菜单栏：**Windows** → **Python Shell**

#### 2️⃣ 运行以下代码：

```python
import sys
import os

# 添加工具路径
tool_path = r"C:\Users\KazamaSuichiku\Desktop\houdini-hip-manager"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

# 导入并运行
import main
main.show_tool()
```

---

### 方法三：通过 123.py 或 456.py 启动脚本

#### 1️⃣ 编辑 Houdini 启动脚本
找到以下路径之一：
- `$HOME/houdiniX.X/scripts/123.py` （每次启动 Houdini 运行）
- `$HOME/houdiniX.X/scripts/456.py` （打开场景后运行）

在 Windows 上通常是：
```
C:\Users\KazamaSuichiku\Documents\houdiniX.X\scripts\
```

#### 2️⃣ 添加以下代码：

```python
# 添加 HIP Manager 到 sys.path
import sys
import os

hip_manager_path = r"C:\Users\KazamaSuichiku\Desktop\houdini-hip-manager"
if hip_manager_path not in sys.path:
    sys.path.insert(0, hip_manager_path)

print("HIP Manager 路径已添加到 Python 环境")
```

#### 3️⃣ 在 Shelf Tool 中使用简化代码：

```python
import main
main.show_tool()
```

---

## 🔧 常见问题解决

### ❌ 如果出现 "模块未找到" 错误

检查路径是否正确：
```python
import os
print(os.path.exists(r"C:\Users\KazamaSuichiku\Desktop\houdini-hip-manager\main.py"))
# 应该返回 True
```

### ❌ 如果工具不更新

使用带 `importlib.reload()` 的版本（方法一中已包含）

### ❌ 如果缺少依赖

确保已安装 PySide6：
```bash
# 在命令行中运行（使用 Houdini 的 Python）
hython -m pip install PySide6
```

或者在 Houdini 的 Python Shell 中：
```python
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
```

---

## 🎨 自定义图标（可选）

### 创建自定义图标：

#### 1️⃣ 准备图标文件
- 创建一个 32x32 或 64x64 像素的 PNG 文件
- 保存为 `hip_manager_icon.png`
- 放在工具文件夹中

#### 2️⃣ 在 Shelf Tool 设置中
- 点击图标预览区域
- 选择 **"Choose File..."**
- 选择你的图标文件

---

## 📋 快捷键设置（可选）

### 为工具添加快捷键：

#### 1️⃣ 打开快捷键编辑器
- **Edit** → **Hotkeys...**

#### 2️⃣ 搜索你的工具
- 搜索 "hip_manager" 或 "HIP Manager"

#### 3️⃣ 设置快捷键
- 建议：`Ctrl+Shift+H` 或 `Alt+H`

---

## ✅ 验证安装

运行以下代码验证工具是否正确安装：

```python
import sys
import os

tool_path = r"C:\Users\KazamaSuichiku\Desktop\houdini-hip-manager"

print("=" * 60)
print("HIP Manager 安装检查")
print("=" * 60)
print(f"工具路径: {tool_path}")
print(f"路径存在: {os.path.exists(tool_path)}")
print(f"main.py 存在: {os.path.exists(os.path.join(tool_path, 'main.py'))}")
print(f"在 sys.path 中: {tool_path in sys.path}")
print("=" * 60)

# 尝试导入
try:
    if tool_path not in sys.path:
        sys.path.insert(0, tool_path)
    import main
    print("✅ main 模块导入成功！")
    print(f"show_tool 函数存在: {hasattr(main, 'show_tool')}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
print("=" * 60)
```

---

## 🚀 一键启动脚本

你也可以将 `shelf_tool.py` 的内容直接复制到 Shelf Tool 中使用。

---

## 💡 提示

1. **重新加载功能**：每次点击 Shelf Tool 都会重新加载代码，方便开发调试
2. **错误提示**：如果启动失败，会在 Houdini 中显示错误对话框
3. **控制台输出**：详细的错误信息会打印在 Houdini 控制台中

---

## 📞 需要帮助？

如果遇到问题，检查：
1. 路径是否正确
2. Python 环境是否有 PySide6
3. 文件权限是否正确
4. Houdini 控制台的错误信息

祝使用愉快！🎉
