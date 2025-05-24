import re
from datetime import datetime
import uuid
import os

class RenameRuleProcessor:
    def __init__(self):
        self.template_variables = {
            'name': lambda file_info: os.path.splitext(file_info['original_name'])[0],
            'ext': lambda file_info: os.path.splitext(file_info['original_name'])[1][1:],
            'date': lambda _: datetime.now().strftime('%Y.%m.%d'),
            'date.modify': lambda file_info: datetime.fromtimestamp(os.path.getmtime(file_info['path'])).strftime('%Y.%m.%d'),
            'time': lambda _: datetime.now().strftime('%Hh%Mm%Ss'),
            'time.modify': lambda file_info: datetime.fromtimestamp(os.path.getmtime(file_info['path'])).strftime('%Hh%Mm%Ss'),
        }
    
    def batch_replace(self, file_info, old_str, new_str='', include_ext=True):
        """批量替换指定字符串"""
        if not old_str:
            return file_info['original_name']
        
        if include_ext:
            name = file_info['original_name']
            return name.replace(old_str, new_str)
        else:
            name, ext = os.path.splitext(file_info['original_name'])
            return name.replace(old_str, new_str) + ext
    
    def insert_text(self, file_info, text, position='start', n=0, target='', include_ext=True):
        """在指定位置插入文本
        position: 'start'/'end'/'nth'/'nth_last'/'before'/'after'
        """
        name, ext = os.path.splitext(file_info['original_name'])
        result = name
        
        if position == 'start':
            result = text + result
        elif position == 'end':
            result = result + text
        elif position == 'nth':
            if len(name) <= n:
                result = result + text
            else:
                result = name[:n] + text + name[n:]
        elif position == 'nth_last':
            if len(name) <= n:
                result = text + result
            else:
                pos = len(name) - n
                result = name[:pos] + text + name[pos:]
        elif position == 'before' and target:
            if target in name:
                result = name.replace(target, text + target)
        elif position == 'after' and target:
            if target in name:
                result = name.replace(target, target + text)
        
        if not include_ext:
            # 如果不包含扩展名，则强制使用原始扩展名
            return result + ext
        return result + (ext if not include_ext else '')
    
    def pad_numbers(self, file_info, width, include_ext=True):
        """数字补零处理"""
        name, ext = os.path.splitext(file_info['original_name'])
        
        def pad_match(match):
            return str(int(match.group())).zfill(width)
        
        result = re.sub(r'\d+', pad_match, name)
        if not include_ext:
            # 如果不包含扩展名，则强制使用原始扩展名
            return result + ext
        return result + ext
    
    def sanitize_filename(self, filename):
        """确保文件名合法"""
        # Windows文件名不能包含的字符
        invalid_chars = r'[<>:"/\\|?*]'
        # 替换非法字符为下划线
        return re.sub(invalid_chars, '_', filename)

    def apply_template(self, file_info, template, index=0, include_ext=True):
        """应用命名模板"""
        name, ext = os.path.splitext(file_info['original_name'])
        result = template
        
        # 处理编号
        number_pattern = r'<#+(?::([0-9]+))?>'
        for match in re.finditer(number_pattern, template):
            hash_part = match.group().split(':')[0]
            width = hash_part.count('#')
            start = int(match.group(1)) if match.group(1) else 1
            number = str(index + start).zfill(width)
            result = result.replace(match.group(), number)
        
        # 处理UUID
        uuid_pattern = r'<uuid(?::(\d+))?(?::(upper|lower))?>'
        for match in re.finditer(uuid_pattern, result):
            length = int(match.group(1)) if match.group(1) else 32
            style = match.group(2)
            uuid_str = str(uuid.uuid4()).replace('-', '')[:length]
            if style == 'upper':
                uuid_str = uuid_str.upper()
            elif style == 'lower':
                uuid_str = uuid_str.lower()
            result = result.replace(match.group(), uuid_str)
        
        # 处理日期时间格式
        # 替换未带格式化参数的变量
        for var_name in self.template_variables:
            simple_tag = f'<{var_name}>'
            if simple_tag in result:
                value = self.template_variables[var_name](file_info)
                result = result.replace(simple_tag, value)

        
        # 处理大小写转换
        for var_name in ['name', 'ext']:
            base_value = self.template_variables[var_name](file_info)
            result = result.replace(f'<{var_name}:upper>', base_value.upper())
            result = result.replace(f'<{var_name}:lower>', base_value.lower())
            result = result.replace(f'<{var_name}>', base_value)
        
        if not include_ext:
            # 如果不包含扩展名，则强制使用原始扩展名
            return result + ext
        return result
    
    def apply_regex(self, file_info, pattern, repl, include_ext=True):
        """应用正则表达式替换"""
        try:
            if include_ext:
                return re.sub(pattern, repl, file_info['original_name'])
            else:
                name, ext = os.path.splitext(file_info['original_name'])
                return re.sub(pattern, repl, name) + ext
        except re.error:
            return file_info['original_name']