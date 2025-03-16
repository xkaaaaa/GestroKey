"""
Web服务器模块
提供嵌入式Web界面和API服务
"""

import os
import json
import time
import threading
import psutil
import platform
import sys
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from PyQt5.QtCore import QObject, pyqtSignal, QMetaObject, Qt, Q_ARG
from app.log import log

# 应用启动时间
START_TIME = datetime.now()

# 尝试导入主模块中的自启动函数
try:
    from src.main import create_autostart_entry, remove_autostart_entry, check_autostart_enabled
except ImportError:
    try:
        # 相对导入可能失败，尝试绝对导入
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from src.main import create_autostart_entry, remove_autostart_entry, check_autostart_enabled
    except ImportError:
        # 如果导入仍然失败，定义占位函数
        def create_autostart_entry():
            log(__name__, "创建自启动项失败：未能导入相关函数", level="error")
            return False
            
        def remove_autostart_entry():
            log(__name__, "移除自启动项失败：未能导入相关函数", level="error")
            return False
            
        def check_autostart_enabled():
            return False

class WebServer(QObject):
    """Web服务器类，提供界面和API服务"""
    
    # 定义信号
    togglePaintingSignal = pyqtSignal()
    minimizeSignal = pyqtSignal()
    exitSignal = pyqtSignal()
    
    def __init__(self, app_instance=None):
        """初始化Web服务器"""
        super().__init__()
        
        log(__name__, "WebServer初始化")
        self.app = Flask(__name__, 
                         template_folder=os.path.join(os.path.dirname(__file__), 'ui/templates'),
                         static_folder=os.path.join(os.path.dirname(__file__), 'ui/static'))
        self.app_instance = app_instance  # 主应用实例引用
        self.server_thread = None
        self.running = False
        
        # 注册路由
        self._register_routes()
        
        # 连接信号到应用实例方法
        if self.app_instance:
            self.togglePaintingSignal.connect(self.app_instance.toggle_painting)
            self.minimizeSignal.connect(self.app_instance.hide)
            self.exitSignal.connect(self.app_instance.clean_exit)
        
        log(__name__, "WebServer初始化完成")
    
    def _register_routes(self):
        """注册所有路由和API端点"""
        log(__name__, "注册路由")
        # 页面路由
        @self.app.route('/')
        def index():
            """显示加载页面"""
            log(__name__, "访问加载页面")
            return render_template('loading.html')
            
        @self.app.route('/console')
        def console():
            log(__name__, "访问控制台页面")
            is_running = self._is_painting_running()
            
            system_info = self._get_system_info()
            return render_template('console.html', is_running=is_running, system_info=system_info)
        
        @self.app.route('/settings')
        def settings():
            log(__name__, "访问设置页面")
            settings_data = self._load_settings()
            return render_template('settings.html', settings=settings_data)
        
        # 静态资源路由
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            return send_from_directory(self.app.static_folder, filename)
        
        # API端点
        @self.app.route('/api/toggle_painting', methods=['POST'])
        def toggle_painting():
            log(__name__, "API: 切换绘画状态")
            if not self.app_instance:
                return jsonify({'success': False, 'message': '应用实例未初始化'})
            
            try:
                # 使用信号在主线程中执行绘画状态切换
                self.togglePaintingSignal.emit()
                
                # 获取当前状态 - 延迟检查给主线程一些时间来切换状态
                def delayed_response():
                    time.sleep(0.1)  # 短暂延迟确保主线程有时间更新状态
                    is_running = self._is_painting_running()
                    
                    # 使用with语句确保在Flask应用上下文中运行
                    with self.app.app_context():
                        return jsonify({'success': True, 'is_running': is_running})
                
                # 在另一个线程中执行延迟响应
                thread = threading.Thread(target=delayed_response)
                thread.daemon = True
                thread.start()
                
                return jsonify({'success': True, 'message': '状态切换中...'})
            except Exception as e:
                log(__name__, f"切换绘画状态失败: {str(e)}", level="error")
                return jsonify({'success': False, 'message': f'错误: {str(e)}'})
        
        @self.app.route('/api/painting_status', methods=['GET'])
        def painting_status():
            """获取当前绘画状态"""
            log(__name__, "API: 查询绘画状态")
            is_running = self._is_painting_running()
            return jsonify({'success': True, 'is_running': is_running})
        
        @self.app.route('/api/minimize', methods=['POST'])
        def minimize():
            log(__name__, "API: 最小化")
            if not self.app_instance:
                return jsonify({'success': False, 'message': '应用实例未初始化'})
            
            try:
                # 使用信号在主线程中执行最小化
                self.minimizeSignal.emit()
                return jsonify({'success': True})
            except Exception as e:
                log(__name__, f"最小化失败: {str(e)}", level="error")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/exit', methods=['POST'])
        def exit_app():
            log(__name__, "API: 退出应用")
            if not self.app_instance:
                return jsonify({'success': False, 'message': '应用实例未初始化'})
            
            try:
                # 使用信号在主线程中执行退出
                self.exitSignal.emit()
                return jsonify({'success': True})
            except Exception as e:
                log(__name__, f"退出失败: {str(e)}", level="error")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/system_info')
        def system_info():
            """获取系统信息"""
            info = self._get_system_info()
            info['is_painting_running'] = self._is_painting_running()
            info['autostart_enabled'] = check_autostart_enabled()
            return jsonify(info)
        
        @self.app.route('/api/autostart', methods=['POST'])
        def autostart():
            """设置开机自启动"""
            log(__name__, "API: 设置开机自启动")
            data = request.get_json()
            if not data or 'enabled' not in data:
                return jsonify({'success': False, 'message': '缺少参数'})
                
            enabled = data['enabled']
            if enabled:
                success = create_autostart_entry()
            else:
                success = remove_autostart_entry()
                
            return jsonify({
                'success': success, 
                'enabled': check_autostart_enabled(),
                'message': '开机自启设置已更新' if success else '开机自启设置失败'
            })
        
        @self.app.route('/api/save_settings', methods=['POST'])
        def save_settings():
            log(__name__, "API: 保存设置")
            try:
                settings_data = request.json
                self._save_settings(settings_data)
                return jsonify({'success': True})
            except Exception as e:
                log(__name__, f"保存设置失败: {str(e)}", level="error")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/reset_settings', methods=['POST'])
        def reset_settings():
            log(__name__, "API: 重置设置")
            try:
                self._reset_settings()
                return jsonify({'success': True})
            except Exception as e:
                log(__name__, f"重置设置失败: {str(e)}", level="error")
                return jsonify({'success': False, 'message': str(e)})
    
    def start(self):
        """启动Web服务器（在单独的线程中运行）"""
        if self.running:
            return
        
        log(__name__, "启动Web服务器")
        
        def run_server():
            self.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True  # 设为守护线程，主程序退出时自动结束
        self.server_thread.start()
        self.running = True
        log(__name__, "Web服务器线程已启动")
    
    def stop(self):
        """停止Web服务器"""
        self.running = False
        log(__name__, "停止Web服务器")
        # Flask没有优雅的停止方法，依赖于daemon线程自动结束
    
    def _get_system_info(self):
        """获取系统信息"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # 计算运行时间
        uptime = datetime.now() - START_TIME
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(hours)}小时 {int(minutes)}分钟"
        
        return {
            'version': '1.0.0',
            'runtime': uptime_str,
            'memory_usage': f"{memory_info.rss / (1024 * 1024):.1f} MB",
            'platform': platform.system() + ' ' + platform.release()
        }
    
    def _load_settings(self):
        """加载设置数据"""
        settings_path = self._get_settings_path()
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config['drawing_settings']
        except Exception as e:
            log(__name__, f"加载设置失败: {str(e)}", level="error")
            print(f"加载设置失败: {str(e)}")
            # 返回默认设置
            return {
                'base_width': 6,
                'min_width': 3,
                'max_width': 15,
                'speed_factor': 1.2,
                'line_color': '#00BFFF',
                'enable_advanced_brush': True,
                'enable_auto_smoothing': True,
                'force_topmost': True,
                'enable_hardware_acceleration': True,
                'start_with_system': False
            }
    
    def _save_settings(self, settings_data):
        """保存设置数据"""
        settings_path = self._get_settings_path()
        
        try:
            # 读取现有配置
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新绘画设置
            config['drawing_settings'].update(settings_data)
            
            # 写回文件
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            log(__name__, "设置已保存")
            return True
        except Exception as e:
            log(__name__, f"保存设置失败: {str(e)}", level="error")
            print(f"保存设置失败: {str(e)}")
            return False
    
    def _reset_settings(self):
        """重置设置为默认值"""
        settings_path = self._get_settings_path()
        
        try:
            # 读取现有配置
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 重置绘画设置为默认值
            config['drawing_settings'] = {
                'base_width': 6,
                'min_width': 3,
                'max_width': 15,
                'speed_factor': 1.2,
                'fade_duration': 0.5,
                'antialias_layers': 2,
                'min_distance': 20,
                'line_color': '#00BFFF',
                'max_stroke_points': 200,
                'max_stroke_duration': 5,
                'enable_advanced_brush': True,
                'force_topmost': True,
                'enable_auto_smoothing': True,
                'smoothing_factor': 0.6,
                'enable_hardware_acceleration': True
            }
            
            # 写回文件
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            log(__name__, "设置已重置为默认值")
            return True
        except Exception as e:
            log(__name__, f"重置设置失败: {str(e)}", level="error")
            print(f"重置设置失败: {str(e)}")
            return False
    
    def _get_settings_path(self):
        """获取设置文件路径"""
        # 与ink_painter中相同的逻辑
        import sys
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
        else:
            # 开发时使用当前文件的上三级目录（src/app → 根目录）
            return os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'settings.json'
            ) 
    
    def _is_painting_running(self):
        """检查绘画模块是否正在运行"""
        if not self.app_instance:
            return False
            
        try:
            # 检查painter属性是否存在且不为None
            return hasattr(self.app_instance, 'painter') and self.app_instance.painter is not None
        except Exception as e:
            log(__name__, f"检查绘画状态失败: {str(e)}", level="error")
            return False 