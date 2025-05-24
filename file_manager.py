import os
from datetime import datetime
import re

def natural_sort_key(s):
    """实现自然排序的键函数"""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    return [convert(c) for c in re.split('([0-9]+)', s)]

class FileManager:
    def __init__(self):
        self.current_directory = ''
        self.files = []
        self.is_folder_mode = False
    
    def load_directory(self, directory_path, is_folder_mode=False):
        """加载目录内容"""
        self.current_directory = directory_path
        self.is_folder_mode = is_folder_mode
        self.files = []
        
        try:
            items = os.listdir(directory_path)
            for item in items:
                full_path = os.path.join(directory_path, item)
                # 根据模式筛选文件或文件夹
                if is_folder_mode and os.path.isdir(full_path) or \
                   not is_folder_mode and os.path.isfile(full_path):
                    self.files.append(self._get_file_info(full_path))
            return True
        except Exception as e:
            print(f'Error loading directory: {e}')
            return False
    
    def _get_file_info(self, file_path):
        """获取文件或文件夹信息"""
        stat = os.stat(file_path)
        name = os.path.basename(file_path)
        return {
            'name': name,
            'type': '文件夹' if os.path.isdir(file_path) else os.path.splitext(name)[1] or '文件',
            'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'original_name': name,
            'new_name': name,
            'path': file_path,
            'is_modified': False,
            'name_length': len(name)
        }
    
    def sort_files(self, key='name', reverse=False, use_natural_sort=True):
        """排序文件列表"""
        if key == 'name':
            if use_natural_sort:
                self.files.sort(key=lambda x: natural_sort_key(x['name']), reverse=reverse)
            else:
                self.files.sort(key=lambda x: x['name'].lower(), reverse=reverse)
        elif key == 'modified_time':
            self.files.sort(key=lambda x: x['modified_time'], reverse=reverse)
        else:
            self.files.sort(key=lambda x: x[key], reverse=reverse)
    
    def rename_file(self, index, new_name):
        """重命名文件"""
        if 0 <= index < len(self.files):
            self.files[index]['new_name'] = new_name
            self.files[index]['is_modified'] = new_name != self.files[index]['original_name']
            return True
        return False
    
    def apply_changes(self):
        """应用重命名更改"""
        success_count = 0
        errors = []
        
        for file_info in self.files:
            if file_info['original_name'] != file_info['new_name']:
                old_path = file_info['path']
                new_path = os.path.join(os.path.dirname(old_path), file_info['new_name'])
                
                try:
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        file_info['path'] = new_path
                        file_info['original_name'] = file_info['new_name']
                        success_count += 1
                    else:
                        errors.append(f'文件已存在: {file_info["new_name"]}')
                except Exception as e:
                    errors.append(f'重命名失败 {file_info["original_name"]}: {str(e)}')
        
        return success_count, errors