from PyQt6.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton,
                             QCheckBox, QTextEdit, QMessageBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt
from rename_rules import RenameRuleProcessor
import os

class RenameDialog(QDialog):
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.rule_processor = RenameRuleProcessor()
        self.setWindowTitle('高级重命名')
        self.setModal(True)
        self.setMinimumSize(600, 400)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_batch_replace_tab(), '批量替换')
        tab_widget.addTab(self.create_insert_text_tab(), '插入字符')
        tab_widget.addTab(self.create_pad_numbers_tab(), '序号补齐')
        tab_widget.addTab(self.create_template_tab(), '重新命名')
        tab_widget.addTab(self.create_regex_tab(), '正则替换')
        layout.addWidget(tab_widget)
        
        # 创建预览和确认按钮
        preview_btn = QPushButton('预览')
        preview_btn.clicked.connect(self.preview_changes)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        
        # 添加是否包含扩展名的选项
        self.include_ext_check = QCheckBox('包含文件扩展名')
        self.include_ext_check.setChecked(False)
        
        # 创建底部按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.include_ext_check)
        button_layout.addStretch()
        button_layout.addWidget(preview_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.current_tab = 0
        tab_widget.currentChanged.connect(self.handle_tab_change)
    
    def create_batch_replace_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 添加说明文本
        help_text = "将文件名中指定的字符串替换为新的字符串，留空新字符串则删除匹配内容"
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        # 添加输入框
        old_layout = QHBoxLayout()
        old_layout.addWidget(QLabel('查找：'))
        self.old_text = QLineEdit()
        old_layout.addWidget(self.old_text)
        layout.addLayout(old_layout)
        
        new_layout = QHBoxLayout()
        new_layout.addWidget(QLabel('替换为：'))
        self.new_text = QLineEdit()
        new_layout.addWidget(self.new_text)
        layout.addLayout(new_layout)
        
        layout.addStretch()
        return tab
    
    def create_insert_text_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 添加说明文本
        help_text = "在指定位置插入新的字符串"
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        # 添加输入框
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel('插入文本：'))
        self.insert_text = QLineEdit()
        text_layout.addWidget(self.insert_text)
        layout.addLayout(text_layout)
        
        # 添加位置选择
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel('插入位置：'))
        self.position_combo = QComboBox()
        self.position_combo.addItems(['开始处', '末尾处', '第N个字符后', '倒数第N个字符前',
                                    '指定字符之前', '指定字符之后'])
        position_layout.addWidget(self.position_combo)
        layout.addLayout(position_layout)
        
        # 添加数字输入框和目标字符输入框
        self.n_input = QSpinBox()
        self.n_input.setRange(1, 999)
        self.n_input.hide()
        
        self.target_input = QLineEdit()
        self.target_input.hide()
        
        extra_layout = QHBoxLayout()
        self.n_label = QLabel('位置：')
        self.n_label.hide()
        self.target_label = QLabel('目标字符：')
        self.target_label.hide()
        
        extra_layout.addWidget(self.n_label)
        extra_layout.addWidget(self.n_input)
        extra_layout.addWidget(self.target_label)
        extra_layout.addWidget(self.target_input)
        extra_layout.addStretch()
        layout.addLayout(extra_layout)
        
        # 根据选择显示/隐藏相关输入框
        self.position_combo.currentIndexChanged.connect(self.update_insert_options)
        
        layout.addStretch()
        return tab
    
    def create_pad_numbers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 添加说明文本
        help_text = "为文件名中的数字补零，使其在排序时保持一致"
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        # 添加位数选择
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel('补齐位数：'))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10)
        self.width_spin.setValue(2)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        layout.addLayout(width_layout)
        
        layout.addStretch()
        return tab
    
    def create_template_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 添加说明文本

        help_text = "使用模板重命名文件，支持以下变量：\n"
        help_text += "（”[]“括号内为可选项，无论使用或不使用都应该删除括号）\n"
        help_text += "<name[:upper/:lower]> - 原文件名(不含后缀)，可指定大小写\n"
        help_text += "<ext[:upper/:lower]> - 原后缀名，可指定大小写\n"
        help_text += "<##:i> - 编号（#的重复次数为位数，i为起始编号）\n"
        help_text += "<date>- 当前日期，形式固定为：year.month.day\n"
        help_text += "<date.modify> - 文件修改日期，形式固定为：year.month.day\n"
        help_text += "<time>- 当前时间，形式固定为：00h00m00s\n"
        help_text += "<time.modify> - 文件修改时间，形式固定为：00h00m00s\n"
        help_text += "<uuid[:n][:upper/:lower]> - 随机字符串，可指定长度n和大小写\n"
        
        help_text_edit = QTextEdit()
        help_text_edit.setPlainText(help_text)
        help_text_edit.setReadOnly(True)
        help_text_edit.setMaximumHeight(200)
        layout.addWidget(help_text_edit)
        
        # 添加模板输入框
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel('命名模板：'))
        self.template_edit = QLineEdit()
        template_layout.addWidget(self.template_edit)
        layout.addLayout(template_layout)
        
        layout.addStretch()
        return tab
    
    def create_regex_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 添加说明文本
        help_text = "使用正则表达式替换文件名中的内容（使用方法自行搜索）\n"
        help_text += "常用正则表达式：\n"
        help_text += ". - 匹配任意字符\n"
        help_text += "\\d - 匹配数字\n"
        help_text += "\\w - 匹配字母数字下划线\n"
        help_text += "* - 匹配0次或多次\n"
        help_text += "+ - 匹配1次或多次\n"
        help_text += "? - 匹配0次或1次\n"
        help_text += "[] - 匹配字符集合\n"
        help_text += "() - 分组\n"
        help_text += "\\1,\\2.. - 引用分组"
        
        help_text_edit = QTextEdit()
        help_text_edit.setPlainText(help_text)
        help_text_edit.setReadOnly(True)
        help_text_edit.setMaximumHeight(200)
        layout.addWidget(help_text_edit)
        
        # 添加输入框
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel('匹配模式：'))
        self.pattern_edit = QLineEdit()
        pattern_layout.addWidget(self.pattern_edit)
        layout.addLayout(pattern_layout)
        
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel('替换为：'))
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)
        
        layout.addStretch()
        return tab
    
    def update_insert_options(self):
        index = self.position_combo.currentIndex()
        # 显示/隐藏数字输入框
        show_n = index in [2, 3]  # 第N个字符后，倒数第N个字符前
        self.n_label.setVisible(show_n)
        self.n_input.setVisible(show_n)
        
        # 显示/隐藏目标字符输入框
        show_target = index in [4, 5]  # 指定字符之前/之后
        self.target_label.setVisible(show_target)
        self.target_input.setVisible(show_target)
    
    def handle_tab_change(self, index):
        self.current_tab = index
    
    def preview_changes(self):
        try:
            new_names = self.get_preview_names()
            if not new_names:
                return
            
            # 更新文件管理器中的新名称
            for i, new_name in enumerate(new_names):
                self.file_manager.rename_file(i, new_name)
            
            # 关闭当前对话框，让用户可以看到主窗口的预览效果
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'预览失败：{str(e)}')
    
    def get_preview_names(self):
        include_ext = self.include_ext_check.isChecked()
        files = self.file_manager.files
        
        if self.current_tab == 0:  # 批量替换
            old_str = self.old_text.text()
            new_str = self.new_text.text()
            if not old_str:
                QMessageBox.warning(self, '错误', '请输入要替换的内容')
                return None
            return [self.rule_processor.batch_replace(file_info, old_str, new_str, include_ext)
                    for file_info in files]
        
        elif self.current_tab == 1:  # 插入字符
            text = self.insert_text.text()
            if not text:
                QMessageBox.warning(self, '错误', '请输入要插入的内容')
                return None
            
            position_map = {
                0: 'start',
                1: 'end',
                2: 'nth',
                3: 'nth_last',
                4: 'before',
                5: 'after'
            }
            position = position_map[self.position_combo.currentIndex()]
            n = self.n_input.value() if position in ['nth', 'nth_last'] else 0
            target = self.target_input.text() if position in ['before', 'after'] else ''
            
            return [self.rule_processor.insert_text(file_info, text, position, n, target, include_ext)
                    for file_info in files]
        
        elif self.current_tab == 2:  # 序号补齐
            width = self.width_spin.value()
            return [self.rule_processor.pad_numbers(file_info, width)
                    for file_info in files]
        
        elif self.current_tab == 3:  # 重新命名
            template = self.template_edit.text()
            if not template:
                QMessageBox.warning(self, '错误', '请输入命名模板')
                return None
            return [self.rule_processor.apply_template(file_info, template, i, include_ext)
                    for i, file_info in enumerate(files)]
        
        elif self.current_tab == 4:  # 正则替换
            pattern = self.pattern_edit.text()
            repl = self.replace_edit.text()
            if not pattern:
                QMessageBox.warning(self, '错误', '请输入正则表达式')
                return None
            return [self.rule_processor.apply_regex(file_info, pattern, repl, include_ext)
                    for file_info in files]
        
        return None