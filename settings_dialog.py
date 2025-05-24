from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QComboBox, QPushButton, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 冗余量设置
        redundancy_layout = QHBoxLayout()
        redundancy_label = QLabel('文件名列宽冗余量：')
        self.redundancy_spinbox = QSpinBox()
        self.redundancy_spinbox.setRange(0, 100)
        self.redundancy_spinbox.setValue(25)
        redundancy_layout.addWidget(redundancy_label)
        redundancy_layout.addWidget(self.redundancy_spinbox)
        layout.addLayout(redundancy_layout)
        
        # 文件名排序方法设置
        sort_layout = QHBoxLayout()
        sort_label = QLabel(' 文件名排序方式：')
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['自然排序', '字母排序'])
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        layout.addLayout(sort_layout)
        
        # 修改行背景色设置
        color_layout = QHBoxLayout()
        color_label = QLabel('已修改项标注颜色：')
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 25)
        self.modified_color = QColor(255, 255, 200)  # 默认浅黄色
        self.update_color_button()
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)
        
        # 确定和取消按钮
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton('确定')
        cancel_button = QPushButton('取消')
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
    
    def update_color_button(self):
        self.color_button.setStyleSheet(
            f'background-color: {self.modified_color.name()};'
            'border: 1px solid black;'
        )
    
    def choose_color(self):
        color = QColorDialog.getColor(self.modified_color, self)
        if color.isValid():
            self.modified_color = color
            self.update_color_button()
    
    def get_settings(self):
        return {
            'redundancy': self.redundancy_spinbox.value(),
            'sort_method': self.sort_combo.currentText(),
            'modified_color': self.modified_color
        }
    
    def set_settings(self, settings):
        self.redundancy_spinbox.setValue(settings.get('redundancy', 25))
        sort_method = settings.get('sort_method', '自然排序')
        index = self.sort_combo.findText(sort_method)
        if index >= 0:
            self.sort_combo.setCurrentIndex(index)
        self.modified_color = settings.get('modified_color', QColor(255, 255, 200))
        self.update_color_button()