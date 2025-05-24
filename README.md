# 文件批量重命名工具

这是一个用Python和PyQt6开发的批量重命名工具。
（小白自用工具，内含大量AIGC。欢迎大佬们修改完善）

## 功能特点

- 支持批量重命名文件或文件夹
- 双窗格界面设计（修改区域和原文件信息区域）
- 自定义设置（列宽冗余量、排序方式、修改行背景色）
- 智能自然排序

## 安装步骤

1. 确保已安装Python 3.8或更高版本
2. 创建虚拟环境并安装依赖包：
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行程序：
   ```
   python main.py
   ```
2. 点击"导入目录"按钮选择要处理的文件夹
3. 在修改区域中双击或按Enter键编辑文件名
4. 点击原文件信息区域的表头可以进行排序

## 打包为exe

使用PyInstaller打包程序：

```

 pyinstaller main.py --onefile --windowed --add-data "static;static"
```

打包后的exe文件将在dist目录中生成。
