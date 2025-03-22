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
import base64
import traceback
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from PyQt5.QtCore import QObject, pyqtSignal, QMetaObject, Qt, Q_ARG
from app.log import log
from app.operation_executor import execute

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
            log.error("创建自启动项失败：未能导入相关函数")
            return False
            
        def remove_autostart_entry():
            log.error("移除自启动项失败：未能导入相关函数")
            return False
            
        def check_autostart_enabled():
            return False

class WebServer(QObject):
    """Web服务器类，提供界面和API服务"""
    
    # 定义信号
    togglePaintingSignal = pyqtSignal()
    minimizeSignal = pyqtSignal()
    maximizeSignal = pyqtSignal()
    exitSignal = pyqtSignal()
    
    def __init__(self, app_instance=None):
        """初始化Web服务器"""
        super().__init__()
        
        log.info("WebServer初始化")
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
            self.minimizeSignal.connect(self.app_instance.showMinimized)  # 改为调用标准最小化方法
            self.exitSignal.connect(self.app_instance.clean_exit)
        
        log.info("WebServer初始化完成")
    
    def _register_routes(self):
        """注册所有路由和API端点"""
        log.info("注册路由")
        # 页面路由
        @self.app.route('/')
        def index():
            """显示加载页面"""
            log.info("访问加载页面")
            return render_template('loading.html')
            
        @self.app.route('/console')
        def console():
            log.info("访问控制台页面")
            is_running = self._is_painting_running()
            
            system_info = self._get_system_info()
            return render_template('console.html', is_running=is_running, system_info=system_info)
        
        @self.app.route('/settings')
        def settings():
            log.info("访问设置页面")
            settings_data = self._load_settings()
            return render_template('settings.html', settings=settings_data)
        
        @self.app.route('/gestures')
        def gestures():
            """显示手势管理页面"""
            log.info("访问手势管理页面")
            gestures_data = self._load_gestures()
            log.info(f"加载了 {len(gestures_data)} 个手势配置项")
            return render_template('gestures.html', gestures=gestures_data)
        
        # 静态资源路由
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            return send_from_directory(self.app.static_folder, filename)
        
        @self.app.route('/static/js/form-controls.js')
        def form_controls_js():
            """提供表单控件JS文件"""
            log.info("加载表单控件增强脚本 - UI已优化")
            return send_file(os.path.join(os.path.dirname(__file__), 'ui/static/js/form-controls.js'))
        
        # API端点
        @self.app.route('/api/log', methods=['POST'])
        def log_message():
            """接收前端日志信息"""
            try:
                data = request.json
                message = data.get('message', '')
                level = data.get('level', 'info')
                module = data.get('module', 'ui')
                
                # 使用log函数记录日志
                log(module, message, level=level)
                return jsonify({'success': True})
            except Exception as e:
                log.error(f"记录前端日志失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/toggle_painting', methods=['POST'])
        def toggle_painting():
            log.info("API: 切换绘画状态")
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
                log.error(f"切换绘画状态失败: {str(e)}")
                return jsonify({'success': False, 'message': f'错误: {str(e)}'})
        
        @self.app.route('/api/painting_status', methods=['GET'])
        def painting_status():
            """获取当前绘画状态"""
            log.info("API: 查询绘画状态")
            is_running = self._is_painting_running()
            return jsonify({'success': True, 'is_running': is_running})
        
        @self.app.route('/api/minimize', methods=['POST'])
        def minimize_window():
            """最小化窗口API"""
            log.info("API: 最小化窗口")
            if self.app_instance:
                result = self.app_instance.minimize_window()
                return jsonify(result)
            else:
                # 如果没有app_instance，则通过信号触发
                self.minimizeSignal.emit()
                return jsonify({"success": True})
        
        @self.app.route('/api/exit', methods=['POST'])
        def exit_app():
            log.info("API: 退出应用")
            if not self.app_instance:
                return jsonify({'success': False, 'message': '应用实例未初始化'})
            
            try:
                # 使用信号在主线程中执行退出
                self.exitSignal.emit()
                return jsonify({'success': True})
            except Exception as e:
                log.error(f"退出失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/system_info')
        def system_info():
            """获取系统信息"""
            info = self._get_system_info()
            info['is_painting_running'] = self._is_painting_running()
            info['autostart_enabled'] = check_autostart_enabled()
            
            # 添加当前设置数据，用于前端局部刷新
            info['settings'] = self._load_settings()
            
            return jsonify(info)
        
        @self.app.route('/api/autostart', methods=['POST'])
        def autostart():
            """设置开机自启动"""
            log.info("API: 设置开机自启动")
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
            log.info("API: 保存设置")
            try:
                settings_data = request.json
                self._save_settings(settings_data)
                return jsonify({'success': True})
            except Exception as e:
                log.error(f"保存设置失败: {str(e)}")
                print(f"保存设置失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/reset_settings', methods=['POST'])
        def reset_settings():
            log.info("API: 重置设置")
            try:
                self._reset_settings()
                return jsonify({'success': True})
            except Exception as e:
                log.error(f"重置设置失败: {str(e)}")
                print(f"重置设置失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)})
                
        @self.app.route('/api/gestures', methods=['GET', 'POST'])
        def manage_gestures():
            """手势API，用于获取、添加、更新和删除手势"""
            try:
                if request.method == 'GET':
                    # 获取所有手势
                    log.info("获取所有手势")
                    gestures = self._load_gestures()
                    return jsonify({"success": True, "gestures": gestures})
                
                elif request.method == 'POST':
                    # 处理操作
                    data = request.json
                    operation = data.get('operation')
                    
                    if operation == 'add':
                        # 添加新手势
                        gesture_name = data.get('name')
                        directions = data.get('directions')
                        action = data.get('action')
                        
                        log.info(f"添加新手势：{gesture_name}，方向序列：{directions}")
                        log.info(f"收到添加手势请求数据: {data}")
                        
                        # 验证输入数据
                        if not gesture_name or not directions or not action:
                            log.warning(f"添加手势失败：参数不完整 name={gesture_name}, directions={directions}, action={'有值' if action else '无值'}")
                            return jsonify({"success": False, "message": "参数不完整"}), 400
                        
                        result = self._add_gesture(gesture_name, directions, action)
                        if result['success']:
                            log.info(f"手势'{gesture_name}'添加成功")
                            return jsonify({"success": True, "message": f"手势 '{gesture_name}' 添加成功"})
                        else:
                            return jsonify({"success": False, "message": result['message']}), 400
                    
                    elif operation == 'update':
                        # 更新手势
                        old_name = data.get('old_name')
                        new_name = data.get('new_name')
                        directions = data.get('directions')
                        action = data.get('action')
                        
                        log.info(f"更新手势：{old_name} -> {new_name}，方向序列：{directions}")
                        log.info(f"收到更新手势请求数据: {data}")
                        
                        # 验证输入数据
                        if not old_name or not new_name or not directions or not action:
                            log.warning(f"更新手势失败：参数不完整 old_name={old_name}, new_name={new_name}, directions={directions}, action={'有值' if action else '无值'}")
                            return jsonify({"success": False, "message": "参数不完整"}), 400
                        
                        result = self._update_gesture(old_name, new_name, directions, action)
                        if result['success']:
                            log.info(f"手势'{old_name}'更新为'{new_name}'成功")
                            return jsonify({"success": True, "message": f"手势 '{new_name}' 更新成功"})
                        else:
                            return jsonify({"success": False, "message": result['message']}), 400
                    
                    elif operation == 'delete':
                        # 删除手势
                        gesture_name = data.get('name')
                        
                        log.info(f"删除手势：{gesture_name}")
                        
                        # 验证输入数据
                        if not gesture_name:
                            log.warning("删除手势失败：未指定手势名称")
                            return jsonify({"success": False, "message": "未指定手势名称"}), 400
                        
                        result = self._delete_gesture(gesture_name)
                        if result:
                            log.info(f"手势'{gesture_name}'删除成功")
                            return jsonify({"success": True, "message": f"手势 '{gesture_name}' 删除成功"})
                        else:
                            return jsonify({"success": False, "message": "删除手势失败，可能不存在该手势"}), 404
                    
                    else:
                        log.warning(f"未知的手势操作: {operation}")
                        return jsonify({"success": False, "message": "未知操作"}), 400
            
            except Exception as e:
                log.error(f"手势管理API异常: {str(e)}")
                return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
        
        @self.app.route('/api/test_gesture', methods=['POST'])
        def test_gesture():
            """测试手势执行效果"""
            try:
                data = request.json
                action_base64 = data.get('action')
                
                log.info("请求测试手势执行")
                
                if not action_base64:
                    log.warning("测试手势失败：未提供动作代码")
                    return jsonify({"success": False, "message": "未提供动作代码"}), 400
                    
                # 执行动作代码
                from app.operation_executor import execute
                
                log.info("开始测试执行手势动作")
                result = execute(action_base64)
                
                if result:
                    log.info("手势测试执行成功")
                    return jsonify({"success": True, "message": "动作执行成功"})
                else:
                    log.warning("手势测试执行失败")
                    return jsonify({"success": False, "message": "动作执行失败"}), 500
                    
            except Exception as e:
                log.error(f"测试手势API异常: {str(e)}")
                return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    def start(self):
        """启动Web服务器（在单独的线程中运行）"""
        if self.running:
            return
        
        log.info("启动Web服务器")
        
        def run_server():
            self.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True  # 设为守护线程，主程序退出时自动结束
        self.server_thread.start()
        self.running = True
        log.info("Web服务器线程已启动")
    
    def stop(self):
        """停止Web服务器"""
        self.running = False
        log.info("停止Web服务器")
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
            log.error(f"加载设置失败: {str(e)}")
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
                
            log.info("设置已保存")
            
            # 如果绘画实例已经在运行，立即应用新设置
            if self.app_instance and hasattr(self.app_instance, 'painter') and self.app_instance.painter is not None:
                try:
                    # 更新运行中的绘画实例的参数
                    result = self.app_instance.painter.update_drawing_settings(settings_data)
                    if result:
                        log.info("绘画设置已即时应用到运行中的实例")
                    else:
                        log.warning("运行时更新绘画设置失败")
                except Exception as e:
                    log.error(f"更新运行中的绘画设置时出错: {str(e)}")
            
            return True
        except Exception as e:
            log.error(f"保存设置失败: {str(e)}")
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
            
            log.info("设置已重置为默认值")
            
            # 如果绘画实例已经在运行，立即应用重置后的设置
            if self.app_instance and hasattr(self.app_instance, 'painter') and self.app_instance.painter is not None:
                try:
                    # 更新运行中的绘画实例的参数
                    result = self.app_instance.painter.update_drawing_settings(config['drawing_settings'])
                    if result:
                        log.info("默认设置已即时应用到运行中的实例")
                    else:
                        log.warning("运行时更新默认设置失败")
                except Exception as e:
                    log.error(f"重置并更新运行中的绘画设置时出错: {str(e)}")
            
            return True
        except Exception as e:
            log.error(f"重置设置失败: {str(e)}")
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
            log.error(f"检查绘画状态失败: {str(e)}")
            return False 
    
    def _load_gestures(self):
        """加载手势数据"""
        gestures_path = self._get_gestures_path()
        
        try:
            if os.path.exists(gestures_path):
                with open(gestures_path, 'r', encoding='utf-8') as f:
                    gestures_data = json.load(f)
                    log.info(f"已加载手势数据，包含 {len(gestures_data.get('gestures', {}))} 个手势")
                    return gestures_data.get('gestures', {})
            else:
                log.warning("手势文件不存在，将返回空列表")
                return {}
        except Exception as e:
            log.error(f"加载手势数据失败: {str(e)}")
            traceback.print_exc()
            return {}
    
    def _check_gesture_validity(self, directions, gestures_data, current_name=None):
        """检查手势的合法性
        
        参数:
            directions: 待检查的方向序列
            gestures_data: 当前手势库数据
            current_name: 当前手势名称（用于更新手势时跳过自身）
            
        返回:
            (is_valid, message): 是否合法及原因
        """
        arrow_symbols = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']
        
        # 检查是否包含合法的箭头符号
        has_arrows = any(symbol in directions for symbol in arrow_symbols)
        if not has_arrows:
            return False, "手势不包含有效的箭头符号"
        
        # 提取方向序列中的所有箭头符号
        gesture_arrows = [c for c in directions if c in arrow_symbols]
        
        # 检查是否有连续的同方向
        for i in range(1, len(gesture_arrows)):
            if gesture_arrows[i] == gesture_arrows[i-1]:
                return False, f"手势包含连续的同方向: {gesture_arrows[i-1]}{gesture_arrows[i]}"
        
        # 检查是否有多组相同的手势
        if len(gesture_arrows) >= 4:
            for pattern_len in range(2, len(gesture_arrows) // 2 + 1):
                for i in range(len(gesture_arrows) - pattern_len * 2 + 1):
                    pattern = gesture_arrows[i:i+pattern_len]
                    # 查找相同模式重复
                    for j in range(i + pattern_len, len(gesture_arrows) - pattern_len + 1):
                        if gesture_arrows[j:j+pattern_len] == pattern:
                            pattern_str = ''.join(pattern)
                            return False, f"手势包含重复的模式: {pattern_str}"
        
        # 检查是否与库中其他手势触发条件相同
        gesture_str = ''.join(gesture_arrows)
        for name, data in gestures_data.items():
            # 跳过当前正在更新的手势
            if name == current_name:
                continue
                
            existing_arrows = [c for c in data['directions'] if c in arrow_symbols]
            existing_str = ''.join(existing_arrows)
            
            if gesture_str == existing_str:
                return False, f"与已有手势 '{name}' 的触发条件相同"
        
        return True, ""
    
    def _save_gestures(self, gestures_data):
        """保存手势数据"""
        gestures_path = self._get_gestures_path()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(gestures_path), exist_ok=True)
            
            # 保存数据
            with open(gestures_path, 'w', encoding='utf-8') as f:
                json.dump({'gestures': gestures_data}, f, ensure_ascii=False, indent=2)
            
            log.info(f"手势数据保存成功，共 {len(gestures_data)} 个手势")
            return True
        except Exception as e:
            log.error(f"保存手势数据失败: {str(e)}")
            traceback.print_exc()
            return False
    
    def _get_gestures_path(self):
        """获取手势文件路径"""
        # 与settings文件保持在同一目录
        return os.path.join(os.path.dirname(self._get_settings_path()), 'gestures.json') 
    
    def _add_gesture(self, name, directions, action):
        """添加新手势"""
        gestures_data = self._load_gestures()
        
        # 检查名称是否已存在
        if name in gestures_data:
            log.warning(f"添加手势失败: 手势名称 '{name}' 已存在")
            return {'success': False, 'message': f'手势名称 "{name}" 已存在'}
        
        # 检查手势合法性
        is_valid, error_message = self._check_gesture_validity(directions, gestures_data)
        if not is_valid:
            log.warning(f"添加手势失败: 手势 '{name}' {error_message}")
            return {'success': False, 'message': f"手势无效: {error_message}"}
            
        # 添加手势
        gestures_data[name] = {
            'directions': directions,
            'action': action
        }
        
        # 保存手势库
        if self._save_gestures(gestures_data):
            log.info(f"已添加新手势: {name}，方向序列: {directions}")
            return {'success': True, 'message': '手势添加成功'}
        else:
            return {'success': False, 'message': '保存手势数据失败'}
    
    def _update_gesture(self, old_name, new_name, directions, action):
        """更新手势"""
        gestures_data = self._load_gestures()
        
        # 检查原手势是否存在
        if old_name not in gestures_data:
            log.warning(f"更新手势失败: 手势 '{old_name}' 不存在")
            return {'success': False, 'message': f'手势 "{old_name}" 不存在'}
        
        # 如果名称有变更，检查新名称是否已存在
        if old_name != new_name and new_name in gestures_data:
            log.warning(f"更新手势失败: 新手势名称 '{new_name}' 已存在")
            return {'success': False, 'message': f'手势名称 "{new_name}" 已存在'}
        
        # 检查手势合法性（更新时传入当前名称以避免与自身比较）
        is_valid, error_message = self._check_gesture_validity(directions, gestures_data, old_name)
        if not is_valid:
            log.warning(f"更新手势失败: 手势 '{new_name}' {error_message}")
            return {'success': False, 'message': f"手势无效: {error_message}"}
        
        # 删除旧手势
        if old_name in gestures_data:
            del gestures_data[old_name]
        
        # 添加新手势
        gestures_data[new_name] = {
            'directions': directions,
            'action': action
        }
        
        # 保存手势库
        if self._save_gestures(gestures_data):
            log.info(f"已更新手势: {old_name} -> {new_name}，方向序列: {directions}")
            return {'success': True, 'message': '手势更新成功'}
        else:
            return {'success': False, 'message': '保存手势数据失败'}
    
    def _delete_gesture(self, name):
        """删除手势"""
        gestures_data = self._load_gestures()
        
        # 检查手势是否存在
        if name not in gestures_data:
            log.warning(f"删除手势失败: 手势 '{name}' 不存在")
            return {'success': False, 'message': f'手势 "{name}" 不存在'}
        
        # 删除手势
        del gestures_data[name]
        
        # 保存手势库
        if self._save_gestures(gestures_data):
            log.info(f"已删除手势: {name}")
            return {'success': True, 'message': '手势删除成功'}
        else:
            return {'success': False, 'message': '保存手势数据失败'} 