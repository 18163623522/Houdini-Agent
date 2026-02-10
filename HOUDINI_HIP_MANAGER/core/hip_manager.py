# -*- coding: utf-8 -*-
"""
Houdini AI 助手 - 主窗口
简化版，只保留 AI 助手功能
支持工作区保存/恢复（窗口状态 + 上下文缓存）
"""

import os
import json
import atexit
import hou
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
from HOUDINI_HIP_MANAGER.ui.ai_tab import AITab
from HOUDINI_HIP_MANAGER.ui.cursor_widgets import CursorTheme


class HipManager(QtWidgets.QMainWindow):
    """Houdini AI 助手主窗口"""
    
    def __init__(self, parent=None):
        # 尝试获取 Houdini 主窗口作为父窗口
        if parent is None:
            try:
                parent = hou.qt.mainWindow()
            except:
                pass
        
        super().__init__(parent)
        self.setWindowTitle("Houdini AI Assistant")
        self.setMinimumSize(420, 600)
        
        # 工作区配置目录
        self._workspace_dir = Path(__file__).parent.parent.parent / "cache" / "workspace"
        self._workspace_dir.mkdir(parents=True, exist_ok=True)
        self._workspace_file = self._workspace_dir / "workspace.json"
        
        # 不使用 WindowStaysOnTopHint，让窗口与 Houdini 同层级
        self.setWindowFlags(QtCore.Qt.Window)
        
        # 设置深色主题
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CursorTheme.BG_PRIMARY};
            }}
        """)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        self.force_quit = False
        self._already_saved = False  # 防止重复保存
        
        self.init_ui(central_widget)
        
        # 加载工作区（窗口状态 + 上下文）
        self._load_workspace()
        
        # 注册多重退出保存钩子（确保 Houdini 退出时能保存）
        # 1. QApplication.aboutToQuit（Qt 正常退出时触发）
        app = QtWidgets.QApplication.instance()
        if app:
            app.aboutToQuit.connect(self._on_app_about_to_quit)
        # 2. atexit（Python 解释器关闭时触发）
        atexit.register(self._atexit_save)
        # 3. Houdini 专用：监听 hipFile 事件（切换场景时也保存）
        try:
            hou.hipFile.addEventCallback(self._on_hip_event)
        except Exception:
            pass

    def init_ui(self, central_widget):
        """初始化UI - 只有 AI 助手"""
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # AI 助手标签页（现在是唯一的内容）
        # 传递工作区目录，让 AITab 可以访问工作区信息
        self.ai_tab = AITab(workspace_dir=self._workspace_dir)
        layout.addWidget(self.ai_tab)

    def force_quit_application(self):
        """强制退出应用程序"""
        self.force_quit = True
        self.close()

    def _save_workspace(self):
        """保存工作区（窗口状态 + 所有会话缓存）"""
        try:
            # 保存窗口状态
            geometry = self.geometry()
            window_state = {
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height(),
                'is_maximized': self.isMaximized()
            }
            
            # 保存所有会话到磁盘（多 tab 持久化）
            has_sessions = False
            tab_count = 0
            if hasattr(self, 'ai_tab') and self.ai_tab:
                has_sessions = self.ai_tab._save_all_sessions()
                tab_count = self.ai_tab.session_tabs.count()
            
            workspace_data = {
                'version': '1.1',
                'window_state': window_state,
                'cache_info': {
                    'has_conversation': has_sessions,
                    'tab_count': tab_count,
                    'use_manifest': True,  # 标识使用新的多会话恢复
                }
            }
            
            with open(self._workspace_file, 'w', encoding='utf-8') as f:
                json.dump(workspace_data, f, ensure_ascii=False, indent=2)
            
            print(f"[Workspace] 工作区已保存: 窗口({window_state['width']}x{window_state['height']}), {tab_count} 个会话标签")
            
        except Exception as e:
            print(f"[Workspace] 保存工作区失败: {str(e)}")
    
    def _load_workspace(self):
        """加载工作区（窗口状态 + 上下文缓存）"""
        try:
            if not self._workspace_file.exists():
                # 没有工作区文件，使用默认设置
                self.resize(450, 700)
                return
            
            with open(self._workspace_file, 'r', encoding='utf-8') as f:
                workspace_data = json.load(f)
            
            # 恢复窗口状态
            window_state = workspace_data.get('window_state', {})
            if window_state:
                x = window_state.get('x', 100)
                y = window_state.get('y', 100)
                width = window_state.get('width', 450)
                height = window_state.get('height', 700)
                is_maximized = window_state.get('is_maximized', False)
                
                self.setGeometry(x, y, width, height)
                if is_maximized:
                    self.setWindowState(QtCore.Qt.WindowMaximized)
            
            # 恢复会话（延迟加载，等 AITab 初始化完成）
            cache_info = workspace_data.get('cache_info', {})
            if cache_info.get('has_conversation') and hasattr(self, 'ai_tab'):
                # 使用 QTimer 延迟加载，确保 AITab 完全初始化
                QtCore.QTimer.singleShot(100, self._load_workspace_cache)
            elif hasattr(self, 'ai_tab'):
                # 即使旧版 workspace 没标记，也尝试恢复 manifest
                QtCore.QTimer.singleShot(100, self._load_workspace_cache)
            
            print(f"[Workspace] 工作区已加载: {self._workspace_file}")
            
        except Exception as e:
            print(f"[Workspace] 加载工作区失败: {str(e)}")
            # 失败时使用默认设置
            self.resize(450, 700)
    
    def _load_workspace_cache(self):
        """延迟加载工作区缓存（优先恢复多会话 manifest，降级到单会话）"""
        try:
            if not hasattr(self, 'ai_tab'):
                return
            
            # 优先尝试多会话恢复
            if self.ai_tab._restore_all_sessions():
                return
            
            # 降级：从 cache_latest.json 恢复单个会话
            cache_dir = self.ai_tab._cache_dir
            latest_cache = cache_dir / "cache_latest.json"
            if latest_cache.exists():
                self.ai_tab._load_cache_silent(latest_cache)
        except Exception as e:
            print(f"[Workspace] 加载缓存失败: {str(e)}")
    
    def _on_app_about_to_quit(self):
        """QApplication 即将退出时保存"""
        self._save_workspace_once()
    
    def _atexit_save(self):
        """Python 退出时的最后保存机会"""
        self._save_workspace_once()
    
    def _on_hip_event(self, event_type):
        """Houdini hipFile 事件回调（切换场景、退出等）"""
        try:
            # hou.hipFileEventType.BeforeClear / BeforeLoad 表示即将切换/关闭场景
            if event_type in (hou.hipFileEventType.BeforeClear,
                              hou.hipFileEventType.BeforeLoad):
                self._save_workspace_once()
        except Exception:
            pass
    
    def _save_workspace_once(self):
        """保存工作区（带去重，防止多个退出钩子重复保存）"""
        if self._already_saved:
            return
        self._already_saved = True
        try:
            self._save_workspace()
        except Exception as e:
            print(f"[Workspace] 退出保存失败: {e}")
        finally:
            # 保存完后重置标记（允许定期保存再次触发）
            self._already_saved = False
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 保存工作区
        self._save_workspace()
        
        if hasattr(self, 'force_quit') and self.force_quit:
            event.accept()
            super().closeEvent(event)
        else:
            # 直接关闭
            event.accept()
            super().closeEvent(event)
