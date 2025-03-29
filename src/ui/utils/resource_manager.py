import os
import sys
import logging
import tempfile
from PyQt5.QtCore import QResource, QFile, QDir

# 导入日志模块
try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class ResourceManager:
    """资源管理器，用于管理Qt资源文件"""
    
    # 资源文件
    _resource_file = None
    _resources_registered = False
    
    @staticmethod
    def register_resources():
        """注册资源文件"""
        try:
            # 如果已经注册过，直接返回
            if ResourceManager._resources_registered:
                log.debug("资源已经注册，跳过重复注册")
                return True
                
            # 获取图标目录路径
            icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")
            
            # 检查资源文件是否存在
            resource_file_path = os.path.join(icons_dir, "icons.qrc")
            
            # 尝试直接设置资源搜索路径
            QDir.addSearchPath("icons", icons_dir)
            QDir.addSearchPath("icons", os.path.join(icons_dir, "internal"))
            
            # 标记为已注册
            ResourceManager._resources_registered = True
            
            log.info(f"已设置资源搜索路径: {icons_dir}")
            log.info("资源注册成功")
            
            return True
        except Exception as e:
            log.error(f"注册资源文件时出错: {str(e)}")
            return False 