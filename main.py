import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QButtonGroup, QRadioButton, QScrollBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon
from settings_dialog import SettingsDialog
from file_manager import FileManager
from config_manager import ConfigManager
from rename_dialog import RenameDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('批量重命名工具')
        self.setMinimumSize(800, 600)
        
        # 加载程序图标
        icon_path = os.path.join(os.path.dirname(__file__), 'static\icon')
        if os.path.exists(icon_path):
            ico_file = os.path.join(icon_path, 'icon.ico')
            png_file = os.path.join(icon_path, 'icon.png')
            if os.path.exists(ico_file):
                self.setWindowIcon(QIcon(ico_file))
            elif os.path.exists(png_file):
                self.setWindowIcon(QIcon(png_file))
        
        # 初始化文件管理器和配置管理器
        self.file_manager = FileManager()
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.load_settings()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部区域
        top_layout = QVBoxLayout()
        
        # 创建目录显示和刷新按钮区域
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel('当前目录：未选择')
        dir_layout.addWidget(self.dir_label)
        top_layout.addLayout(dir_layout)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        self.import_btn = QPushButton('导入目录')
        self.refresh_btn = QPushButton('重置并刷新')
        self.settings_btn = QPushButton('设置')
        self.rename_btn = QPushButton('高级重命名')
        self.apply_btn = QPushButton('应用更改')
        self.apply_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)
        
        # 统一按钮大小
        for btn in [self.import_btn, self.refresh_btn, self.settings_btn, self.rename_btn, self.apply_btn]:
            btn.setFixedWidth(100)
        
        # 创建文件/文件夹选择按钮组
        mode_group = QButtonGroup(self)
        self.file_radio = QRadioButton('文件模式')
        self.folder_radio = QRadioButton('文件夹模式')
        self.file_radio.setChecked(True)
        mode_group.addButton(self.file_radio)
        mode_group.addButton(self.folder_radio)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.file_radio)
        button_layout.addWidget(self.folder_radio)
        button_layout.addWidget(self.settings_btn)
        button_layout.addWidget(self.rename_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        top_layout.addLayout(button_layout)
        main_layout.addLayout(top_layout)
        
        # 创建表格区域
        tables_layout = QHBoxLayout()
        
        # 修改区域表格
        edit_widget = QWidget()
        edit_layout = QVBoxLayout(edit_widget)
        self.edit_table = QTableWidget()
        self.edit_table.setColumnCount(1)
        self.edit_table.setHorizontalHeaderLabels(['重命名'])
        edit_layout.addWidget(self.edit_table)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.addWidget(edit_widget)
        
        # 原文件信息区域表格
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(3)
        self.info_table.setHorizontalHeaderLabels(['原文件名', '类型', '修改时间'])
        self.info_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        


        # 隐藏右侧表格的滚动条
        self.info_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        info_layout.addWidget(self.info_table)
        info_layout.setContentsMargins(0, 0, 0, 0)
        tables_layout.addWidget(info_widget)
        
        # 设置表格区域的拉伸因子为2:3
        tables_layout.setStretch(0, 2)
        tables_layout.setStretch(1, 3)
        
        # 同步表格滚动
        self.edit_table.verticalScrollBar().valueChanged.connect(
            self.info_table.verticalScrollBar().setValue)
        self.info_table.verticalScrollBar().valueChanged.connect(
            self.edit_table.verticalScrollBar().setValue)
        
        main_layout.addLayout(tables_layout)
        
        # 连接信号
        self.import_btn.clicked.connect(self.import_directory)
        self.settings_btn.clicked.connect(self.open_settings)
        self.rename_btn.clicked.connect(self.open_rename_dialog)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.refresh_btn.clicked.connect(self.refresh_directory)
        self.info_table.horizontalHeader().sectionClicked.connect(self.handle_sort)
        self.edit_table.itemChanged.connect(self.handle_rename)
        self.file_radio.toggled.connect(self.handle_mode_change)
        self.folder_radio.toggled.connect(self.handle_mode_change)
        
        # 初始化排序状态
        self.sort_column = 1  # 默认按文件名排序
        self.sort_order = Qt.SortOrder.AscendingOrder
        
    def import_directory(self):
        directory = QFileDialog.getExistingDirectory(self, '选择目录')
        if directory:
            self.dir_label.setText(f'当前目录：{directory}')
            is_folder_mode = self.folder_radio.isChecked()
            if self.file_manager.load_directory(directory, is_folder_mode):
                # 应用默认排序方式
                self.file_manager.sort_files(
                    key='name',
                    reverse=False,
                    use_natural_sort=self.settings['sort_method'] == '自然排序'
                )
                self.update_tables()
                self.apply_btn.setEnabled(True)
                self.refresh_btn.setEnabled(True)
                self.rename_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, '错误', '无法加载目录')
    
    def refresh_directory(self):
        if self.file_manager.current_directory:
            if any(file_info['is_modified'] for file_info in self.file_manager.files):
                reply = QMessageBox.question(self, '确认刷新',
                    '刷新操作将撤销所有未保存的修改，是否继续？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # 保存当前排序状态
            current_sort_key = {
                0: 'name',
                1: 'type',
                2: 'modified_time'
            }.get(self.sort_column, 'name')
            current_sort_reverse = self.sort_order == Qt.SortOrder.DescendingOrder
            use_natural_sort = current_sort_key == 'name' and self.settings['sort_method'] == '自然排序'
            
            is_folder_mode = self.folder_radio.isChecked()
            if self.file_manager.load_directory(self.file_manager.current_directory, is_folder_mode):
                # 恢复排序状态
                self.file_manager.sort_files(
                    key=current_sort_key,
                    reverse=current_sort_reverse,
                    use_natural_sort=use_natural_sort
                )
                self.update_tables()
            else:
                QMessageBox.warning(self, '错误', '无法刷新目录')
    
    def handle_mode_change(self):
        if self.file_manager.current_directory:
            self.refresh_directory()
    
    def update_tables(self):
        files = self.file_manager.files
        self.edit_table.setRowCount(len(files))
        self.info_table.setRowCount(len(files))
        
        # 计算最大文件名长度
        max_name_length = max([file_info['name_length'] for file_info in files]) if files else 0
        redundancy = self.settings.get('redundancy', 25)
        char_width = 4
        name_width = (max_name_length + redundancy) * char_width  # 假设每个字符宽度为4像素
        
        # 设置列宽
        self.edit_table.setColumnWidth(0, self.width() * 2 // 5 - 15 * char_width) #重命名名列宽度
        self.info_table.setColumnWidth(0, min(name_width, self.width() * 3 // 5 - 15 * char_width)) #原文件名列宽度不超过窗口大小的3/5（修改区域宽度：原文件信息区域=2:3）
        self.info_table.setColumnWidth(1, 11 * char_width) #类型列宽度
        self.info_table.setColumnWidth(2, 33 * char_width) #修改时间列宽度 
        
        for i, file_info in enumerate(files):
            # 更新修改区域
            name_item = QTableWidgetItem(file_info['new_name'])
            self.edit_table.setItem(i, 0, name_item)
            if file_info['is_modified']:
                name_item.setBackground(self.settings['modified_color'])
            
            # 更新信息区域
            original_name_item = QTableWidgetItem(file_info['original_name'])
            type_item = QTableWidgetItem(file_info['type'])
            time_item = QTableWidgetItem(file_info['modified_time'])
            
            # 设置信息区域的背景色
            for item in [original_name_item, type_item, time_item]:
                item.setBackground(QColor(245, 245, 245))
            
            self.info_table.setItem(i, 0, original_name_item)
            self.info_table.setItem(i, 1, type_item)
            self.info_table.setItem(i, 2, time_item)
    
    def handle_sort(self, column):
        if column == self.sort_column:
            # 切换排序顺序
            self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.sort_column = column
            self.sort_order = Qt.SortOrder.AscendingOrder
        
        # 根据列类型选择排序方式
        key = {
            0: 'name',
            1: 'type',
            2: 'modified_time'
        }.get(column, 'name')
        
        use_natural_sort = key == 'name' and self.settings['sort_method'] == '自然排序'
        self.file_manager.sort_files(
            key=key,
            reverse=self.sort_order == Qt.SortOrder.DescendingOrder,
            use_natural_sort=use_natural_sort
        )
        self.update_tables()
    
    def handle_rename(self, item):
        if item.column() == 0:  # 处理重命名列
            row = item.row()
            new_name = item.text()
            if self.file_manager.rename_file(row, new_name):
                if self.file_manager.files[row]['is_modified']:
                    item.setBackground(self.settings['modified_color'])
                else:
                    item.setBackground(Qt.GlobalColor.white)
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.set_settings(self.settings)
        if dialog.exec():
            self.settings = dialog.get_settings()
            self.config_manager.save_settings(self.settings)
    
    def apply_changes(self):
        if self.file_manager.current_directory:
            if any(file_info['is_modified'] for file_info in self.file_manager.files):
                reply = QMessageBox.question(self, '确认',
                    '应用更改后无法撤销，是否继续？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return
        success_count, errors = self.file_manager.apply_changes()
        if success_count >0:
            message = f'成功重命名 {success_count} 个项目'
        elif  success_count == 0:
            message = '尚未进行修改'
        if errors:
            message += '\n\n失败项目：\n' + '\n'.join(errors)
        QMessageBox.information(self, '重命名结果', message)
        if success_count > 0:
            self.update_tables()

    def open_rename_dialog(self):
        dialog = RenameDialog(self.file_manager, self)
        if dialog.exec():
            self.update_tables()
    
    def closeEvent(self, event):
        if any(file_info['is_modified'] for file_info in self.file_manager.files):
            reply = QMessageBox.question(self, '确认退出',
                '有未保存的修改，关闭程序将丢失这些修改，是否继续？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()