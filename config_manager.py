import os
import configparser
from PyQt6.QtGui import QColor

class ConfigManager:
    def __init__(self):
        self.config_file = 'settings.ini'
        self.config = configparser.ConfigParser()
        self.default_settings = {
            'redundancy': '25',
            'sort_method': '自然排序',
            'modified_color': '#FFFFC8'
        }
    
    def load_settings(self):
        """加载设置，如果配置文件不存在则创建默认配置"""
        if not os.path.exists(self.config_file):
            return self._create_default_settings()
        
        try:
            self.config.read(self.config_file, encoding='utf-8')
            settings = {
                'redundancy': self.config.getint('Settings', 'redundancy'),
                'sort_method': self.config.get('Settings', 'sort_method'),
                'modified_color': QColor(self.config.get('Settings', 'modified_color'))
            }
            return settings
        except Exception as e:
            print(f'Error loading settings: {e}')
            return self._create_default_settings()
    
    def save_settings(self, settings):
        """保存设置到配置文件"""
        try:
            self.config['Settings'] = {
                'redundancy': str(settings['redundancy']),
                'sort_method': settings['sort_method'],
                'modified_color': settings['modified_color'].name()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f'Error saving settings: {e}')
            return False
    
    def _create_default_settings(self):
        """创建默认设置"""
        self.config['Settings'] = self.default_settings
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
        return {
            'redundancy': int(self.default_settings['redundancy']),
            'sort_method': self.default_settings['sort_method'],
            'modified_color': QColor(self.default_settings['modified_color'])
        }