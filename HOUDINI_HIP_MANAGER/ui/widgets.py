import os
import hou
from PySide6 import QtWidgets, QtGui, QtCore
from datetime import datetime
from HOUDINI_HIP_MANAGER.utils.hip_utils import get_snapshot_path, safe_load_hip, delete_hip_file
from shared.p4v_utils import launch_p4v

class FloatingIcon(QtWidgets.QWidget):
    """浮动图标组件，用于快速访问主窗口"""
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(40, 40)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        
        pixmap = QtGui.QPixmap(40, 40)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(0, 123, 255, 200))
        painter.drawEllipse(0, 0, 40, 40)
        painter.setPen(QtGui.QColor("white"))
        painter.setFont(QtGui.QFont("Arial", 15, QtGui.QFont.Bold))
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "H")
        painter.end()
        
        self.icon_label.setPixmap(pixmap)
        layout.addWidget(self.icon_label)
        
        self.draggable = False
        self.offset = None
        
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.move(screen_geometry.width() - 60, 20)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.draggable = True
            # Qt6: 使用 globalPosition().toPoint() 替代 globalPos()
            global_pos = event.globalPosition().toPoint()
            self.offset = global_pos - self.pos()
            self.drag_start_pos = global_pos
            # 接受事件,防止传播
            event.accept()
        elif event.button() == QtCore.Qt.RightButton:
            # Qt6: 使用 globalPosition().toPoint() 替代 globalPos()
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()
        
    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() == QtCore.Qt.LeftButton:
            # Qt6: 使用 globalPosition().toPoint() 替代 globalPos()
            new_pos = event.globalPosition().toPoint() - self.offset
            self.move(new_pos)
            # 接受事件,防止传播导致重绘
            event.accept()
        
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.draggable = False
            if hasattr(self, 'drag_start_pos'):
                # Qt6: 使用 globalPosition().toPoint() 替代 globalPos()
                global_pos = event.globalPosition().toPoint()
                distance = (global_pos - self.drag_start_pos).manhattanLength()
                if distance < 5:
                    if self.main_window.isVisible():
                        self.main_window.hide()
                        self.main_window.is_minimized_to_icon = True
                    else:
                        # 恢复窗口前先确保窗口状态正常
                        self.main_window.setWindowState(
                            self.main_window.windowState() & ~QtCore.Qt.WindowMinimized
                        )
                        self.main_window.show()
                        self.main_window.raise_()
                        self.main_window.activateWindow()
                        self.main_window.is_minimized_to_icon = False
            event.accept()
    
    def show_context_menu(self, position):
        menu = QtWidgets.QMenu(self)
        
        if self.main_window.isVisible():
            show_action = menu.addAction("隐藏窗口")
            show_action.triggered.connect(self.main_window.hide)
        else:
            show_action = menu.addAction("显示窗口")
            show_action.triggered.connect(self.restore_window)
        
        menu.addSeparator()
        p4v_action = menu.addAction("打开P4V")
        p4v_action.triggered.connect(lambda: launch_p4v(self.main_window))
        
        menu.addSeparator()
        
        quit_action = menu.addAction("退出程序")
        quit_action.triggered.connect(self.quit_application)
        
        # Qt6: 使用 exec() 替代 exec_()
        menu.exec(position)
    
    def restore_window(self):
        """从浮动图标恢复窗口"""
        # 确保窗口状态正常（移除最小化标志）
        self.main_window.setWindowState(
            self.main_window.windowState() & ~QtCore.Qt.WindowMinimized
        )
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        self.main_window.is_minimized_to_icon = False
    
    def quit_application(self):
        if self.main_window:
            self.main_window.force_quit_application()
        self.close()
        QtWidgets.QApplication.quit()

class CustomAttributeWidget(QtWidgets.QWidget):
    """自定义属性配置组件"""
    def __init__(self, attr_type, attr_name, initial_value="", parent=None):
        super().__init__(parent)
        self.attr_type = attr_type
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        title_label = QtWidgets.QLabel(attr_name)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 4px;
                background-color: #007BFF;
                color: white;
                border-radius: 3px;
                text-align: center;
            }
        """)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.input_field = QtWidgets.QTextEdit()
        self.input_field.setPlainText(initial_value)
        self.input_field.setMaximumHeight(80)
        self.input_field.setPlaceholderText(f"输入{attr_name}（逗号分隔，如：P,N,name）")
        
        layout.addWidget(title_label)
        layout.addWidget(self.input_field)
        
        self.setStyleSheet("""
            CustomAttributeWidget {
                border: 1px solid #007BFF;
                border-radius: 6px;
                background-color: white;
                margin: 3px;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 8px;
                font-size: 14px;
                background-color: #fafafa;
            }
            QTextEdit:focus {
                border: 2px solid #007BFF;
                background-color: white;
            }
        """)
    
    def get_value(self):
        return self.input_field.toPlainText().strip()
    
    def set_value(self, value):
        self.input_field.setPlainText(value)

class LogDisplayWidget(QtWidgets.QWidget):
    """日志和历史显示组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        self.tab_widget = QtWidgets.QTabWidget()
        
        log_tab = QtWidgets.QWidget()
        log_layout = QtWidgets.QVBoxLayout(log_tab)
        log_layout.setContentsMargins(4, 4, 4, 4)
        log_layout.setSpacing(4)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setMinimumHeight(80)
        self.log_text.setPlaceholderText("日志信息将显示在这里...")
        self.log_text.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        
        log_button_layout = QtWidgets.QHBoxLayout()
        copy_btn = QtWidgets.QPushButton("复制日志")
        copy_btn.clicked.connect(self.copy_log)
        clear_btn = QtWidgets.QPushButton("清除日志")
        clear_btn.clicked.connect(self.clear_log)
        log_button_layout.addWidget(copy_btn)
        log_button_layout.addWidget(clear_btn)
        log_button_layout.addStretch()
        
        log_layout.addWidget(self.log_text)
        log_layout.addLayout(log_button_layout)
        log_layout.addStretch()
        
        history_tab = QtWidgets.QWidget()
        history_layout = QtWidgets.QVBoxLayout(history_tab)
        history_layout.setContentsMargins(4, 4, 4, 4)
        history_layout.setSpacing(4)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["节点路径", "导出时间", "文件路径"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setMinimumHeight(120)
        self.table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setFixedHeight(50)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setAlternatingRowColors(False)
        
        reload_btn = QtWidgets.QPushButton("重新加载选中文件")
        reload_btn.clicked.connect(self.reload_selected)
        
        history_layout.addWidget(self.table)
        history_layout.addWidget(reload_btn)
        
        self.tab_widget.addTab(log_tab, "系统日志")
        self.tab_widget.addTab(history_tab, "导出历史")
        
        layout.addWidget(self.tab_widget)
        
        self.load_history()
        
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #007BFF;
                background-color: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                color: #333;
                padding: 4px 8px;
                margin: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #007BFF;
                color: white;
            }
            QTextEdit {
                border: 1px solid #007BFF;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                font-family: 'Consolas', 'Monaco', monospace;
                padding: 4px;
                line-height: 1.2;
            }
            QTextEdit:focus {
                border: 2px solid #0056b3;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton[text="清除日志"] {
                background-color: #6c757d;
            }
            QPushButton[text="清除日志"]:hover {
                background-color: #545b62;
            }
            QPushButton[text="重新加载选中文件"] {
                background-color: #007BFF;
            }
            QPushButton[text="重新加载选中文件"]:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                border: 1px solid #007BFF;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                font-weight: normal;
                gridline-color: #d0d0d0;
                alternate-background-color: white;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #e0e0e0;
                color: #000000;
                background-color: white;
            }
            QTableWidget::item:alternate {
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #e3f2fd;
                color: #000000;
            }
            QHeaderView::section {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 6px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-right: 1px solid #0056b3;
                border-bottom: 1px solid #0056b3;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #007BFF;
                border: 1px solid #0056b3;
            }
            QTableWidget::verticalHeader {
                background-color: white;
                border-right: 1px solid #d0d0d0;
            }
            QTableWidget QHeaderView::section:vertical {
                background-color: white;
                color: #000000;
                border-right: 1px solid #d0d0d0;
                border-bottom: 1px solid #e0e0e0;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 2px;
            }
        """)
    
    def add_log(self, message, log_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if log_type == "success":
            color = "#28a745"
        elif log_type == "warning":
            color = "#ffc107"
        elif log_type == "error":
            color = "#dc3545"
        else:
            color = "#007bff"
        
        formatted_message = f'<span style="color: #666;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{log_type.upper()}]</span> {message}'
        self.log_text.append(formatted_message)
        cursor = self.log_text.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def copy_log(self):
        try:
            plain_text = self.log_text.toPlainText()
            if plain_text.strip():
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(plain_text)
                self.add_log("日志内容已复制到剪贴板", "success")
            else:
                self.add_log("没有日志内容可复制", "warning")
        except Exception as e:
            self.add_log(f"复制失败: {e}", "error")
    
    def clear_log(self):
        reply = QtWidgets.QMessageBox.question(
            self, "确认清除", 
            "确定要清除所有日志内容吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.log_text.clear()
            self.add_log("日志已清除", "info")
    
    def load_history(self):
        self.table.setRowCount(0)
        try:
            from HOUDINI_HIP_MANAGER.utils.common_utils import get_history_path
            history_path = get_history_path("export")
        except:
            history_path = os.path.join(os.getcwd(), "export_history.txt")
            
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line in lines:
                    if "|" in line:
                        parts = line.strip().split("|")
                        if len(parts) >= 3:
                            node_path, timestamp, file_path = parts[0], parts[1], parts[2]
                            row = self.table.rowCount()
                            self.table.insertRow(row)
                            
                            node_item = QtWidgets.QTableWidgetItem(node_path)
                            node_item.setToolTip(f"节点路径: {node_path}")
                            
                            time_item = QtWidgets.QTableWidgetItem(timestamp)
                            time_item.setToolTip(f"导出时间: {timestamp}")
                            
                            file_item = QtWidgets.QTableWidgetItem(os.path.basename(file_path))
                            file_item.setToolTip(f"完整路径: {file_path}")
                            
                            self.table.setItem(row, 0, node_item)
                            self.table.setItem(row, 1, time_item)
                            self.table.setItem(row, 2, file_item)
                            
                self.table.resizeColumnsToContents()
                for col in range(3):
                    if self.table.columnWidth(col) < 120:
                        self.table.setColumnWidth(col, 120)
            except Exception as e:
                print(f"加载历史记录失败: {e}")
    
    def add_history(self, node_path, file_path):
        try:
            from HOUDINI_HIP_MANAGER.utils.common_utils import get_history_path
            history_path = get_history_path("export")
        except:
            history_path = os.path.join(os.getcwd(), "export_history.txt")
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(f"{node_path}|{timestamp}|{file_path}\n")
            self.load_history()
        except Exception as e:
            print(f"添加历史记录失败: {e}")
    
    def reload_selected(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            file_item = self.table.item(current_row, 2)
            if file_item:
                file_name = file_item.text()
                file_tooltip = file_item.toolTip()
                if "完整路径: " in file_tooltip:
                    full_path = file_tooltip.replace("完整路径: ", "")
                    self.load_bgeo_asset(full_path)
                else:
                    self.add_log("无法获取文件的完整路径", "error")
            else:
                self.add_log("未找到选中的文件信息", "error")
        else:
            self.add_log("请先选中一个文件", "warning")
    
    def load_bgeo_asset(self, file_path):
        try:
            if not os.path.exists(file_path):
                self.add_log(f"文件不存在: {os.path.basename(file_path)}", "error")
                return
            
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.bgeo', '.geo', '.bgeo.sc', '.geo.sc']:
                self.add_log(f"不支持的文件格式: {file_ext}", "warning")
                return
            
            network_editor = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
            if not network_editor:
                self.add_log("未找到网络编辑器", "error")
                return
            
            current_network = network_editor.pwd()
            if not current_network:
                self.add_log("未找到当前网络", "error")
                return
            
            if current_network.childTypeCategory().name() != "Sop":
                self.add_log("当前网络不是SOP网络，无法创建file节点", "warning")
                return
            
            file_node_name = f"file_{os.path.splitext(os.path.basename(file_path))[0]}"
            counter = 1
            original_name = file_node_name
            while current_network.node(file_node_name):
                file_node_name = f"{original_name}_{counter}"
                counter += 1
            
            file_node = current_network.createNode("file", file_node_name)
            file_node.parm("file").set(file_path)
            file_node.moveToGoodPosition()
            file_node.setSelected(True, clear_all_selected=True)
            network_editor.homeToSelection()
            
            success_msg = f"成功创建file节点加载资产: {os.path.basename(file_path)}"
            self.add_log(success_msg, "success")
            
            main_window = self.parent()
            from HOUDINI_HIP_MANAGER.core.hip_manager import HipManager
            while main_window and not isinstance(main_window, HipManager):
                main_window = main_window.parent()
            if main_window:
                main_window.minimizeToIcon()
                
        except Exception as e:
            error_msg = f"加载资产失败: {str(e)}"
            self.add_log(error_msg, "error")

class HipLoaderThread(QtCore.QThread):
    """HIP文件加载线程"""
    hip_loaded = QtCore.Signal(str, str)
    error = QtCore.Signal(str, str)
    progress = QtCore.Signal(int, int)

    def __init__(self, hip_files):
        super().__init__()
        self.hip_files = hip_files

    def run(self):
        total = len(self.hip_files)
        batch_size = 10
        for i in range(0, total, batch_size):
            if self.isInterruptionRequested():
                break
            batch = self.hip_files[i:i + batch_size]
            for hip_path, snapshot in batch:
                if snapshot and os.path.exists(snapshot):
                    self.hip_loaded.emit(hip_path, snapshot)
                else:
                    self.error.emit(hip_path, "该场景没有生成快照")
                self.progress.emit(i + len(batch), total)
            import time
            time.sleep(0.05)


class LoadingSpinner(QtWidgets.QWidget):
    """旋转加载动画控件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(50)  # 50ms 刷新一次，约 20 FPS
        self.setFixedSize(32, 32)
        # 设置背景透明且不自动填充
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        # 优化绘制性能
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
        
    def start(self):
        """开始旋转"""
        if not self._timer.isActive():
            self._angle = 0
            self._timer.start()
            self.setVisible(True)
        
    def stop(self):
        """停止旋转"""
        if self._timer.isActive():
            self._timer.stop()
        self.setVisible(False)
        self._angle = 0
        
    def _rotate(self):
        """每次旋转 15 度"""
        self._angle = (self._angle + 15) % 360
        # 只更新自己的区域，不触发父窗口重绘
        self.update(self.rect())
        
    def paintEvent(self, event):
        """绘制旋转的加载图标"""
        if not self.isVisible():
            return
            
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # 将坐标原点移到控件中心
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        
        # 绘制 8 个圆点组成的旋转图案
        radius = 10
        dot_radius = 2.5
        for i in range(8):
            angle = i * 45
            # 计算每个点的位置
            x = radius * 0.8
            y = 0
            
            # 根据位置计算透明度（前面的点更亮）
            alpha = int(255 * (1 - i / 8.0))
            color = QtGui.QColor(26, 115, 232, alpha)  # #1a73e8 蓝色
            
            painter.save()
            painter.rotate(angle)
            painter.setBrush(color)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QPointF(x, y), dot_radius, dot_radius)
            painter.restore()
