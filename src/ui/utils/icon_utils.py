import os
import tempfile
from PIL import Image
import io
import base64

def svg_to_ico(svg_path: str, sizes: list = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]) -> str:
    """
    将SVG文件转换为ICO文件并保存到临时目录
    
    Args:
        svg_path: SVG文件路径
        sizes: 图标尺寸列表，默认为常用尺寸
        
    Returns:
        str: 生成的ICO文件路径
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.gettempdir()
        ico_filename = os.path.join(temp_dir, "gestrokey.ico")
        
        # 读取SVG文件
        with open(svg_path, 'rb') as f:
            svg_data = f.read()
            
        # 创建不同尺寸的图标
        images = []
        for size in sizes:
            # 将SVG转换为PNG
            from PyQt5.QtCore import QByteArray, QBuffer
            from PyQt5.QtGui import QImage, QPainter
            from PyQt5.QtSvg import QSvgRenderer
            
            # 创建SVG渲染器
            renderer = QSvgRenderer()
            renderer.load(QByteArray(svg_data))
            
            # 创建QImage
            image = QImage(size[0], size[1], QImage.Format_ARGB32)
            image.fill(0)  # 透明背景
            
            # 创建QPainter
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            
            # 将QImage转换为PIL Image
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            image.save(buffer, "PNG")
            pil_image = Image.open(io.BytesIO(buffer.data().data()))
            buffer.close()
            
            images.append(pil_image)
        
        # 保存为ICO，包含所有尺寸
        images[0].save(ico_filename, format='ICO', sizes=[(img.width, img.height) for img in images])
        
        return ico_filename
    except Exception as e:
        print(f"转换SVG到ICO时出错: {e}")
        return None 