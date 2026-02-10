# Houdini AI Assistant

Houdini AI 助手，提供智能节点操作、联网搜索、Python 代码执行等功能。

Cursor 风格的极简 UI，专注于 AI 交互。

## 🌟 核心特性

### AI Agent 模式（Cursor 风格 UI）

全新的 **Cursor 风格深色主题界面**：

- 🎨 **深色主题**：与 Cursor/VS Code 一致的深色 UI
- 📦 **可折叠区块**：思考过程、工具调用、结果都可展开/折叠
- ⏹️ **真正的停止功能**：可随时中断正在进行的 AI 请求
- 💬 **上下文管理**：自动压缩长对话，保持上下文连贯性
- 🔄 **流式输出**：实时显示 AI 思考和回复过程
- ⌨️ **快捷键支持**：Ctrl+Enter 发送消息

### 智能节点操作

- **多轮工具调用**：AI 可以自主决定读取节点、分析网络、修改参数
- **智能节点操作**：先读取网络结构，再获取详细参数，然后执行操作
- **Function Calling**：使用 OpenAI 兼容的工具调用协议

### 支持的 AI 提供商
| 提供商 | 模型 | 特点 |
|--------|------|------|
| **DeepSeek**（推荐） | deepseek-chat, deepseek-coder | 性价比高，响应快 |
| **智谱GLM** | glm-4.6v-flash（免费）, glm-4-flash, glm-4-plus, glm-4-air | 国内访问稳定 |
| **OpenAI** | gpt-4o-mini, gpt-4o, gpt-4-turbo | 能力强大 |

## 项目结构

```
HOUDINI-ASSET-MANAGER/
├── launcher.py                  # 启动器
├── lib/                         # 内置依赖库（requests 等）
│   ├── requests/
│   ├── urllib3/
│   ├── certifi/
│   └── ...
├── config/                      # 配置目录（自动创建）
│   └── houdini_ai.ini          # AI 助手配置（API Key 等）
├── cache/                       # 缓存目录（快照等）
├── shared/                      # 共享模块
│   ├── common_utils.py         # 路径/配置工具
│   └── p4v_utils.py            # P4V 集成
└── HOUDINI_HIP_MANAGER/        # Houdini 工具
    ├── main.py                 # 入口
    ├── core/                   # 核心逻辑
    │   ├── hip_manager.py      # HIP 文件管理器
    │   └── asset_checker.py    # 资产检查器
    ├── ui/                     # UI 组件
    │   ├── ai_tab.py          # AI Agent 助手（Cursor 风格）
    │   ├── cursor_widgets.py  # Cursor 风格 UI 组件
    │   ├── chat_window.py     # 对话窗口
    │   ├── widgets.py         # 自定义控件
    │   └── dialogs.py         # 对话框
    └── utils/                  # 工具函数
        ├── ai_client.py       # AI API 客户端（支持 Function Calling）
        ├── hip_utils.py       # HIP 文件操作
        └── mcp/               # 节点操作系统
            ├── client.py      # 节点操作客户端（工具执行器）
            └── ...
```

## 快速开始

### 环境要求
- Windows
- Python 3.9+
- PySide6
- Houdini 20.5+ / 21+

### 依赖库

项目包含一个 `lib/` 目录，内置了以下依赖库，无需额外安装：

- `requests` - HTTP 请求库
- `urllib3` - URL 处理
- `certifi` - SSL 证书
- `charset_normalizer` - 字符编码检测
- `idna` - 国际化域名

代码会自动从 `lib/` 目录加载这些库。

### 在 Houdini 中使用

```python
import sys
sys.path.insert(0, r"C:\path\to\HOUDINI-ASSET-MANAGER")
import launcher
launcher.show_tool()
```

### 配置 API Key

1. **环境变量（推荐）**
   ```powershell
   # DeepSeek
   [Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', '<你的Key>', 'User')
   
   # GLM-4.7（智谱AI）
   [Environment]::SetEnvironmentVariable('GLM_API_KEY', '<你的Key>', 'User')
   
   # OpenAI
   [Environment]::SetEnvironmentVariable('OPENAI_API_KEY', '<你的Key>', 'User')
   ```

2. **工具内设置**
   - 点击"设置 API Key…"按钮
   - 勾选"保存到本机配置"

## AI Agent 功能详解

### 工作原理

AI Agent 模式实现了类似 Cursor 的多轮工具调用：

```
用户请求 → AI 分析 → 调用工具 → 获取结果 → AI 继续分析 → 调用更多工具 → ... → 最终回复
```

### 可用工具

| 工具 | 功能 |
|------|------|
| `get_network_structure` | 获取节点网络拓扑（节点名、类型、连接） |
| `get_node_details` | 获取节点详细参数 |
| `set_node_parameter` | 设置节点参数 |
| `create_node` | 创建单个节点 |
| `create_nodes_batch` | 批量创建节点网络 |
| `connect_nodes` | 连接两个节点 |
| `delete_node` | 删除节点 |
| `search_node_types` | 搜索节点类型 |
| `check_errors` | **检查节点/网络的错误和警告** |
| `execute_python` | 在 Houdini Python 环境中执行代码 |
| `web_search` | 联网搜索 Houdini 文档和信息 |
| `fetch_webpage` | 获取网页内容 |
| `add_todo` | 添加任务到 Todo 列表 |
| `update_todo` | 更新任务状态 |
| `verify_and_summarize` | 验证结果并生成总结 |

### Todo 任务系统

AI 会使用 **Todo 任务系统** 来规划和跟踪复杂任务：

```
用户请求 → AI 创建 Todo 列表 → 逐个执行任务 → 更新状态 → 验证结果 → 生成总结
```

**工作流程：**

1. **任务规划**：AI 使用 `add_todo` 创建任务清单
2. **执行跟踪**：每完成一个步骤，AI 使用 `update_todo` 更新状态
3. **结果验证**：完成所有任务后，AI 使用 `verify_and_summarize` 检查结果
4. **自动修正**：如果结果不符合预期，AI 会自动返回修正

**UI 显示：**

- Todo 列表显示在对话区域上方
- 不同状态有不同图标：○ 待处理 / ◎ 进行中 / ● 已完成 / ✗ 错误
- 可以清空或折叠 Todo 列表

### 错误检查与自动修复

AI 会**自动检查节点错误和警告**，并尝试修复：

1. **创建后检查**：每次创建节点后，AI 会调用 `check_errors` 检查是否有报错
2. **自动分析**：根据错误信息分析问题原因（缺少输入、参数错误等）
3. **主动修复**：通过调整参数、修改连接或更换节点类型来修复问题
4. **验证修复**：修复后再次检查，确保问题已解决

这模拟了真实 Houdini 用户的工作流程：创建节点 → 检查错误 → 修复 → 验证。

### 减少幻觉机制

AI 被设计为**主动使用联网搜索**来获取真实的节点信息：

1. **参数名验证**：设置参数前，AI 会搜索官方文档确认正确的参数名
2. **不依赖记忆**：AI 不会凭空猜测参数名，而是通过搜索确认
3. **使用最新文档**：**仅使用 Houdini 21 官方文档**（https://www.sidefx.com/docs/houdini/）

### Houdini 21 文档规则

AI 搜索 Houdini 信息时会：
- 使用 `site:sidefx.com Houdini 21` 限定搜索范围
- 直接访问官方节点文档：`https://www.sidefx.com/docs/houdini/nodes/sop/节点名.html`
- 避免使用过时的 Houdini 18/19/20 文档

### 使用示例

**示例 1：查看网络结构**
```
用户：帮我看看当前网络有哪些节点
AI：[调用 get_network_structure]
AI：当前网络包含 5 个节点：box1, scatter1, copytopoints1...
```

**示例 2：创建节点网络**
```
用户：创建一个 box，在上面 scatter 100 个点
AI：[调用 create_node: box]
AI：[调用 create_node: scatter]
AI：[调用 connect_nodes: box → scatter]
AI：[调用 set_node_parameter: scatter.npts = 100]
AI：已完成！创建了 box1 和 scatter1，scatter 点数设置为 100
```

**示例 3：修改节点参数（带联网验证）**
```
用户：把 box1 的大小改成 5
AI：[调用 web_search: "Houdini box node size parameter"]
AI：[调用 get_node_details: /obj/geo1/box1]
AI：[调用 set_node_parameter: size=(5,5,5)]
AI：已将 box1 的尺寸修改为 5x5x5
```

**示例 4：执行 Python 代码**
```
用户：用 Python 给所有点添加随机颜色
AI：[调用 execute_python: ...]
AI：已执行代码，为 1000 个点添加了随机 Cd 属性
```

**示例 5：自动检查和修复错误**
```
用户：创建一个山地地形
AI：[调用 create_node: grid, heightfield_noise]
AI：[调用 connect_nodes: ...]
AI：[调用 check_errors]  ← 自动检查节点错误
AI：检测到错误：heightfield_noise 需要 HeightField 输入
AI：[调用 delete_node: heightfield_noise]
AI：[调用 web_search: "Houdini heightfield from polygon"]
AI：[调用 create_node: heightfield_project]
AI：[调用 check_errors]  ← 再次验证
AI：✅ 没有错误，已成功创建山地地形
```

**示例 5：搜索 VEX 知识**
```
用户：VEX 怎么写随机颜色？
AI：[调用 web_search: "Houdini VEX random color attribute"]
AI：[调用 fetch_webpage: sidefx.com/docs/...]
AI：根据官方文档，你可以这样写：@Cd = set(rand(@ptnum), ...)
```

### Agent 模式 vs 普通模式

| 特性 | Agent 模式 | 普通模式 |
|------|-----------|---------|
| 自动读取节点 | ✅ | ❌ |
| 多轮工具调用 | ✅ | ❌ |
| 自主决策 | ✅ | ❌ |
| 响应速度 | 较慢（多次调用） | 快 |

## HIP 文件管理

- 浏览、打开、保存 HIP 文件
- 快照预览
- 搜索和排序
- 删除和批量删除

## 资产检查

- 节点参数检查
- 配置允许的属性
- 导出资产

## GLM-4.7 API 说明

GLM-4.7 是智谱AI 提供的大语言模型，API 格式与 OpenAI 兼容。

**API 端点**：`https://open.bigmodel.cn/api/paas/v4/chat/completions`

**获取 API Key**：
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并创建 API Key
3. 在工具中配置或设置环境变量 `GLM_API_KEY`

**可用模型**：
- `glm-4.6v-flash`：🆓 免费多模态模型（支持图片/视频/文件，支持 Function Call）
- `glm-4-flash`：快速版（性价比高）
- `glm-4-plus`：最强模型
- `glm-4-air`：平衡版
- `glm-4-long`：长文本版（支持 1M 上下文）

## 疑难排查

### API 连接问题
- 使用"测试连接"按钮诊断
- 检查 API Key 是否正确
- 确认网络可访问 API 端点

### Agent 模式不工作
- 确认 AI 提供商支持 Function Calling
- DeepSeek 和 GLM-4.7 都支持工具调用

### 节点操作失败
- 确认在 Houdini 中运行
- 检查节点路径是否正确
- 查看工具执行结果中的错误信息

## 版本历史

- **v5.0** — **Cursor 风格 UI 大更新**
  - 深色主题界面
  - 可折叠的思考过程和工具调用
  - 真正的停止功能（中断请求）
  - 上下文自动压缩
  - 代码块语法高亮
- v4.0 — Agent 模式，支持多轮工具调用，添加 GLM-4.7
- v3.0 — 精简为纯 Houdini 工具
- v2.0 — 多 DCC 支持架构
- v1.0 — 初始版本

## 作者

KazamaSuichiku

## 许可证

内部工具，仅供项目使用
