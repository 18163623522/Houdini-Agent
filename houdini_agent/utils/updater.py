# -*- coding: utf-8 -*-
"""
Houdini Agent - 自动更新模块

通过 GitHub API 检查新版本，下载并覆盖本地文件，
然后通知调用方重启插件窗口。

线程安全：check / download / apply 均可在后台线程调用，
UI 回调通过 Qt Signal 回到主线程。
"""

import os
import sys
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Tuple

# ---------- 常量 ----------

GITHUB_OWNER = "Kazama-Suichiku"
GITHUB_REPO = "Houdini-Agent"
GITHUB_BRANCH = "main"

# GitHub API 端点
_API_LATEST_COMMIT = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
_API_VERSION_FILE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/VERSION?ref={GITHUB_BRANCH}"
_ARCHIVE_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

# 项目根目录（VERSION 文件所在目录）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_VERSION_FILE = _PROJECT_ROOT / "VERSION"

# 更新时需要保留（不覆盖）的路径
_PRESERVE_PATHS = frozenset({
    "config",           # 用户 API key 等配置
    "cache",            # 对话缓存、文档索引
    "trainData",        # 训练数据
    ".git",             # git 仓库
})


# ==========================================================
# 版本工具
# ==========================================================

def get_local_version() -> str:
    """读取本地 VERSION 文件，返回版本字符串，失败返回 '0.0.0'"""
    try:
        return _VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return "0.0.0"


def _parse_version(v: str) -> Tuple[int, ...]:
    """把 '6.5.0' 解析为 (6, 5, 0) 用于比较"""
    parts = []
    for seg in v.strip().split("."):
        try:
            parts.append(int(seg))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _version_gt(remote: str, local: str) -> bool:
    """remote > local ?"""
    return _parse_version(remote) > _parse_version(local)


# ==========================================================
# 检查更新
# ==========================================================

def check_update(timeout: float = 8.0) -> dict:
    """检查 GitHub 上是否有新版本
    
    Returns:
        {
            'has_update': bool,
            'local_version': str,
            'remote_version': str,   # 如果获取失败为 ''
            'remote_commit': str,    # 最新 commit SHA（前 7 位）
            'commit_message': str,   # 最新 commit 消息
            'error': str,            # 出错信息（成功为 ''）
        }
    """
    result = {
        'has_update': False,
        'local_version': get_local_version(),
        'remote_version': '',
        'remote_commit': '',
        'commit_message': '',
        'error': '',
    }
    
    try:
        import requests  # type: ignore
    except ImportError:
        # 尝试从 lib 目录导入
        lib_dir = str(_PROJECT_ROOT / "lib")
        if lib_dir not in sys.path:
            sys.path.insert(0, lib_dir)
        import requests  # type: ignore
    
    # 1) 获取远程 VERSION 文件内容
    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        resp = requests.get(_API_VERSION_FILE, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            import base64
            content_b64 = data.get("content", "")
            remote_ver = base64.b64decode(content_b64).decode("utf-8").strip()
            result['remote_version'] = remote_ver
        else:
            result['error'] = f"GitHub API 返回 {resp.status_code}"
            return result
    except requests.exceptions.Timeout:
        result['error'] = "连接 GitHub 超时，请检查网络"
        return result
    except Exception as e:
        result['error'] = f"检查更新失败: {e}"
        return result
    
    # 2) 获取最新 commit 信息
    try:
        resp2 = requests.get(_API_LATEST_COMMIT, headers=headers, timeout=timeout)
        if resp2.status_code == 200:
            commit_data = resp2.json()
            result['remote_commit'] = commit_data.get("sha", "")[:7]
            result['commit_message'] = commit_data.get("commit", {}).get("message", "").split("\n")[0]
    except Exception:
        pass  # commit 信息获取失败不影响版本判断
    
    # 3) 比较版本
    if result['remote_version']:
        result['has_update'] = _version_gt(result['remote_version'], result['local_version'])
    
    return result


# ==========================================================
# 下载 & 应用更新
# ==========================================================

def download_and_apply(progress_callback=None) -> dict:
    """下载最新版本并覆盖本地文件
    
    Args:
        progress_callback: 可选回调 (stage: str, percent: int) -> None
            stage: 'downloading' | 'extracting' | 'applying' | 'done'
            percent: 0-100
    
    Returns:
        {'success': bool, 'error': str, 'updated_files': int}
    """
    def _progress(stage: str, pct: int):
        if progress_callback:
            try:
                progress_callback(stage, pct)
            except Exception:
                pass
    
    try:
        import requests  # type: ignore
    except ImportError:
        lib_dir = str(_PROJECT_ROOT / "lib")
        if lib_dir not in sys.path:
            sys.path.insert(0, lib_dir)
        import requests  # type: ignore
    
    tmp_dir = None
    try:
        # ---- 1. 下载 ZIP ----
        _progress('downloading', 0)
        resp = requests.get(_ARCHIVE_URL, stream=True, timeout=60)
        resp.raise_for_status()
        
        total_size = int(resp.headers.get('content-length', 0))
        
        tmp_dir = tempfile.mkdtemp(prefix="houdini_agent_update_")
        zip_path = os.path.join(tmp_dir, "update.zip")
        
        downloaded = 0
        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        _progress('downloading', min(95, int(downloaded / total_size * 95)))
        
        _progress('downloading', 100)
        
        # ---- 2. 解压 ----
        _progress('extracting', 0)
        extract_dir = os.path.join(tmp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        _progress('extracting', 100)
        
        # GitHub ZIP 解压后有一个顶层目录，如 Houdini-Agent-main/
        entries = os.listdir(extract_dir)
        if len(entries) == 1 and os.path.isdir(os.path.join(extract_dir, entries[0])):
            source_root = os.path.join(extract_dir, entries[0])
        else:
            source_root = extract_dir
        
        # ---- 3. 覆盖文件 ----
        _progress('applying', 0)
        updated_count = 0
        target_root = str(_PROJECT_ROOT)
        
        for dirpath, dirnames, filenames in os.walk(source_root):
            # 计算相对路径
            rel_dir = os.path.relpath(dirpath, source_root)
            
            # 跳过需要保留的目录
            top_dir = rel_dir.split(os.sep)[0] if rel_dir != '.' else ''
            if top_dir in _PRESERVE_PATHS:
                continue
            
            # 过滤子目录（不递归进入需要保留的目录）
            dirnames[:] = [d for d in dirnames if d not in _PRESERVE_PATHS]
            
            # 确保目标目录存在
            target_dir = os.path.join(target_root, rel_dir) if rel_dir != '.' else target_root
            os.makedirs(target_dir, exist_ok=True)
            
            for fname in filenames:
                src_file = os.path.join(dirpath, fname)
                dst_file = os.path.join(target_dir, fname)
                
                try:
                    shutil.copy2(src_file, dst_file)
                    updated_count += 1
                except PermissionError:
                    # .pyd / .dll 可能被锁定，跳过
                    pass
                except Exception:
                    pass
        
        _progress('applying', 100)
        _progress('done', 100)
        
        return {'success': True, 'error': '', 'updated_files': updated_count}
        
    except Exception as e:
        return {'success': False, 'error': str(e), 'updated_files': 0}
    
    finally:
        # 清理临时目录
        if tmp_dir and os.path.exists(tmp_dir):
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass


# ==========================================================
# 重启插件
# ==========================================================

def restart_plugin():
    """重启 Houdini Agent 插件窗口
    
    通过重新加载模块并调用 show_tool() 来实现"重启"效果。
    必须在 Qt 主线程调用。
    """
    try:
        import importlib
        
        # 强制清除所有已加载的 houdini_agent 模块
        mods_to_remove = [k for k in sys.modules if k.startswith('houdini_agent')]
        for k in mods_to_remove:
            del sys.modules[k]
        
        # 重新导入并启动
        # 注意：main.py 中的 _reload_modules 会处理模块重新加载
        if 'houdini_agent.main' in sys.modules:
            del sys.modules['houdini_agent.main']
        
        from houdini_agent.main import show_tool
        return show_tool()
        
    except Exception as e:
        print(f"[Updater] Restart failed: {e}")
        import traceback
        traceback.print_exc()
        return None
