import os
import hou
from PySide6 import QtWidgets, QtGui, QtCore
from HOUDINI_HIP_MANAGER.ui.widgets import CustomAttributeWidget
from HOUDINI_HIP_MANAGER.utils.common_utils import load_config, save_config

class SnapshotViewer(QtWidgets.QDialog):
    """快照预览对话框"""
    def __init__(self, snapshot_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快照预览")
        self.setMinimumSize(400, 250)
        self.setWindowFlags(QtCore.Qt.Window)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        lbl = QtWidgets.QLabel()
        pix = QtGui.QPixmap(snapshot_path) if snapshot_path and os.path.exists(snapshot_path) else QtGui.QPixmap()
        if pix.isNull():
            pix = QtGui.QPixmap(400, 250)
            pix.fill(QtGui.QColor("darkgray"))
        lbl.setPixmap(pix.scaled(400, 250, QtCore.Qt.KeepAspectRatio))
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                background-color: white;
                border: 1px solid #007BFF;
                border-radius: 4px;
                font-size: 14px;
            }
        """)

class AttributeConfigDialog(QtWidgets.QDialog):
    """属性配置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("配置允许的属性")
        self.setMinimumSize(550, 380)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        
        self.allowed_attrs = {"point": "", "prim": "", "vertex": "", "detail": ""}
        self.load_config()
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        info_label = QtWidgets.QLabel("配置各类型属性的允许列表，属性名称用逗号分隔：")
        info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 6px;
                background-color: #e7f3ff;
                border-radius: 4px;
                border: 1px solid #007BFF;
            }
        """)
        
        attrs_container = QtWidgets.QWidget()
        attrs_layout = QtWidgets.QGridLayout(attrs_container)
        attrs_layout.setSpacing(8)
        
        self.attr_widgets = {}
        attr_configs = [
            ("point", "点属性 (Point Attributes)", 0, 0),
            ("prim", "图元属性 (Prim Attributes)", 0, 1),
            ("vertex", "顶点属性 (Vertex Attributes)", 1, 0),
            ("detail", "细节属性 (Detail Attributes)", 1, 1)
        ]
        
        for attr_type, attr_name, row, col in attr_configs:
            widget = CustomAttributeWidget(attr_type, attr_name, self.allowed_attrs[attr_type])
            self.attr_widgets[attr_type] = widget
            attrs_layout.addWidget(widget, row, col)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)
        
        reset_btn = QtWidgets.QPushButton("重置")
        reset_btn.clicked.connect(self.reset_config)
        
        cancel_btn = QtWidgets.QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QtWidgets.QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)
        save_btn.setDefault(True)
        
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addWidget(info_label)
        layout.addWidget(attrs_container, 1)
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 70px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton[text="重置"] {
                background-color: #6c757d;
            }
            QPushButton[text="重置"]:hover {
                background-color: #545b62;
            }
            QPushButton[text="取消"] {
                background-color: #6c757d;
            }
            QPushButton[text="取消"]:hover {
                background-color: #545b62;
            }
        """)
    
    def load_config(self):
        config, _ = load_config("asset_checker")
        for key, value in config.items():
            if key in self.allowed_attrs:
                self.allowed_attrs[key] = value
    
    def reset_config(self):
        reply = QtWidgets.QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有配置吗？这将清空所有属性设置。",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            for widget in self.attr_widgets.values():
                widget.set_value("")
    
    def save_config(self):
        try:
            for attr_type, widget in self.attr_widgets.items():
                self.allowed_attrs[attr_type] = widget.get_value()
            
            success, config_path = save_config("asset_checker", self.allowed_attrs)
            if success:
                QtWidgets.QMessageBox.information(
                    self, "成功", 
                    f"配置已保存到：\n{config_path}",
                    QtWidgets.QMessageBox.Ok
                )
                self.accept()
            else:
                QtWidgets.QMessageBox.critical(
                    self, "错误", 
                    "保存配置失败",
                    QtWidgets.QMessageBox.Ok
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "错误", 
                f"保存配置失败:\n{str(e)}",
                QtWidgets.QMessageBox.Ok
            )
