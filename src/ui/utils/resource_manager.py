import os
import sys
import logging
import tempfile
import traceback
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
    _debug_mode = False
    
    @staticmethod
    def set_debug_mode(debug=False):
        """设置调试模式
        
        Args:
            debug: 是否启用调试模式
        """
        ResourceManager._debug_mode = debug
        if debug:
            log.debug("资源管理器已设置为调试模式")
    
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
            
            if ResourceManager._debug_mode:
                log.debug(f"图标目录路径: {icons_dir}")
                log.debug(f"图标目录是否存在: {os.path.exists(icons_dir)}")
                if os.path.exists(icons_dir):
                    log.debug(f"图标目录内容: {os.listdir(icons_dir)}")
            
            # 检查资源文件是否存在
            resource_file_path = os.path.join(icons_dir, "icons.qrc")
            
            if ResourceManager._debug_mode:
                log.debug(f"资源文件路径: {resource_file_path}")
                log.debug(f"资源文件是否存在: {os.path.exists(resource_file_path)}")
                
                # 检查internal目录
                internal_dir = os.path.join(icons_dir, "internal")
                log.debug(f"internal目录路径: {internal_dir}")
                log.debug(f"internal目录是否存在: {os.path.exists(internal_dir)}")
                if os.path.exists(internal_dir):
                    log.debug(f"internal目录内容: {os.listdir(internal_dir)}")
            
            # 尝试直接设置资源搜索路径
            QDir.addSearchPath("icons", icons_dir)
            QDir.addSearchPath("icons", os.path.join(icons_dir, "internal"))
            
            # 测试资源路径是否正确
            if ResourceManager._debug_mode:
                test_paths = [
                    ("主图标目录", QDir.searchPaths("icons")[0], "close.svg"),
                    ("内部图标目录", QDir.searchPaths("icons")[1] if len(QDir.searchPaths("icons")) > 1 else None, "checkbox_checked.svg")
                ]
                
                for name, path, test_file in test_paths:
                    if path:
                        full_path = os.path.join(path, test_file)
                        log.debug(f"测试 {name}: {full_path} 存在: {os.path.exists(full_path)}")
            
            # 标记为已注册
            ResourceManager._resources_registered = True
            
            log.info(f"已设置资源搜索路径: {icons_dir}")
            log.info("资源注册成功")
            
            return True
        except Exception as e:
            error_msg = f"注册资源文件时出错: {str(e)}"
            log.error(error_msg)
            if ResourceManager._debug_mode:
                log.debug(f"详细错误: {traceback.format_exc()}")
                
                # 记录搜索路径信息
                try:
                    log.debug(f"当前图标搜索路径: {QDir.searchPaths('icons')}")
                except:
                    log.debug("无法获取当前搜索路径")
            return False 