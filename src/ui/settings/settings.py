import getpass
import json
import logging
import os
import sys
import time

try:
    from core.logger import get_logger
    from version import APP_NAME, AUTHOR  # 导入应用名称和作者名
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from version import APP_NAME, AUTHOR

# 条件导入Windows注册表操作模块
if sys.platform.startswith("win"):
    import winreg

# 单例模式的设置管理器
_settings_instance = None


class Settings:
    """设置管理器，负责加载、保存和管理应用程序设置"""

    def __init__(self):
        """初始化设置管理器"""
        self.logger = get_logger("Settings")
        self.settings = self._load_default_settings()
        self.settings_file = self._get_settings_file_path()
        self.has_unsaved_changes = False
        self.saved_settings = None  # 用于保存最后一次成功保存的设置

        # 加载设置
        self.load()

    def _load_default_settings(self):
        """加载默认设置"""
        try:
            # 从默认设置文件加载
            default_settings_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "default_settings.json"
            )

            if os.path.exists(default_settings_path):
                with open(default_settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                self.logger.info(f"已从 {default_settings_path} 加载默认设置")
                return settings
            else:
                self.logger.error(f"默认设置文件 {default_settings_path} 不存在")
                raise FileNotFoundError(f"默认设置文件不存在: {default_settings_path}")
        except Exception as e:
            self.logger.error(f"加载默认设置失败: {e}")
            raise

    def _get_settings_file_path(self):
        """获取设置文件路径"""
        if sys.platform.startswith("win"):
            # Windows系统使用用户文档目录
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(
                user_dir, f".{AUTHOR}", APP_NAME.lower(), "config"
            )
        elif sys.platform.startswith("darwin"):
            # macOS系统使用Library/Application Support目录
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(
                user_dir,
                "Library",
                "Application Support",
                f"{AUTHOR}",
                APP_NAME,
                "config",
            )
        else:
            # Linux和其他系统遵循XDG标准，使用~/.config/目录
            xdg_config_home = os.environ.get(
                "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
            )
            config_dir = os.path.join(xdg_config_home, f"{AUTHOR}", APP_NAME, "config")

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

        return os.path.join(config_dir, "settings.json")

    def load(self):
        """从文件加载设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                # 更新设置，确保所有默认设置都存在
                for key, value in loaded_settings.items():
                    if key in self.settings:
                        self.settings[key] = value

                self.logger.info(f"已从 {self.settings_file} 加载设置")
                self.has_unsaved_changes = False
                # 保存当前加载的设置到saved_settings
                self.saved_settings = self.settings.copy()
            else:
                self.logger.info("未找到设置文件，使用默认设置")
                self.save()  # 保存默认设置
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            raise

    def save(self):
        """保存设置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            self.logger.info(f"设置已保存到 {self.settings_file}")
            self.has_unsaved_changes = False
            # 保存当前设置到saved_settings
            self.saved_settings = self.settings.copy()
            return True
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False

    def get(self, key, default=None):
        """获取设置项，支持点号分隔的嵌套键"""
        if "." in key:
            keys = key.split(".")
            value = self.settings
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        else:
            # 向后兼容，支持旧的直接键访问
            if key in self.settings:
                return self.settings[key]
            # 尝试在brush或app分组中查找
            if "brush" in self.settings and key in self.settings["brush"]:
                return self.settings["brush"][key]
            if "app" in self.settings and key in self.settings["app"]:
                return self.settings["app"][key]
            return default

    def set(self, key, value):
        """设置设置项，支持点号分隔的嵌套键"""
        if "." in key:
            keys = key.split(".")
            current = self.settings
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            old_value = current.get(keys[-1])
            if old_value != value:
                current[keys[-1]] = value
                
                # 检查是否与保存的值不同
                saved_value = None
                if self.saved_settings:
                    saved_current = self.saved_settings
                    for k in keys[:-1]:
                        if isinstance(saved_current, dict) and k in saved_current:
                            saved_current = saved_current[k]
                        else:
                            saved_current = None
                            break
                    if saved_current and keys[-1] in saved_current:
                        saved_value = saved_current[keys[-1]]
                
                if saved_value != value:
                    self.has_unsaved_changes = True
                    self.logger.debug(f"设置项已更新: {key}={value}, 有未保存更改")
                else:
                    self.logger.debug(f"设置项已更新: {key}={value}, 但与保存的值相同")
            return True
        else:
            # 向后兼容，支持旧的直接键设置
            # 尝试在brush或app分组中设置
            if key in ["pen_width", "pen_color"]:
                return self.set(f"brush.{key}", value)
            elif key in ["show_exit_dialog", "default_close_action"]:
                return self.set(f"app.{key}", value)
            else:
                # 直接设置顶级键
                if key in self.settings:
                    if self.settings[key] != value:
                        self.settings[key] = value
                        if (
                            not self.saved_settings
                            or key not in self.saved_settings
                            or self.saved_settings[key] != value
                        ):
                            self.has_unsaved_changes = True
                            self.logger.debug(f"设置项已更新: {key}={value}, 有未保存更改")
                    return True
                return False

    def reset_to_default(self):
        """重置为默认设置"""
        self.logger.info("重置为默认设置")
        try:
            default_settings = self._load_default_settings()
            if self.settings != default_settings:
                self.settings = default_settings
                self.has_unsaved_changes = True

            # 保存设置并更新saved_settings
            success = self.save()
            if success:
                self.saved_settings = self.settings.copy()
                self.has_unsaved_changes = False

                # 确保开机自启动设置为关闭状态
                if self.is_autostart_enabled():
                    self.set_autostart(False)
                    self.logger.info("重置为默认设置时已关闭开机自启动")

            return success
        except Exception as e:
            self.logger.error(f"重置为默认设置失败: {e}")
            return False

    def has_changes(self):
        """检查是否有未保存的更改"""
        # 首先根据标志快速判断
        if not self.has_unsaved_changes:
            return False

        # 如果标志为True，进一步比较当前设置与已保存的设置
        if not self.saved_settings:
            # 如果没有已保存的设置记录，则认为有未保存的更改
            return True

        # 逐一比较设置项
        for key, value in self.settings.items():
            if key not in self.saved_settings or self.saved_settings[key] != value:
                return True

        # 检查是否有已保存的设置项在当前设置中不存在
        for key in self.saved_settings:
            if key not in self.settings:
                return True

        # 实际上没有差异，重置标志
        self.has_unsaved_changes = False
        return False

    # 以下为新增的开机自启动相关方法

    def get_app_path(self):
        """
        获取应用程序可执行文件的路径
        返回值：应用程序可执行文件的完整路径，如果遇到错误则返回None
        """
        try:
            import os
            import sys

            # 检查应用程序是否已冻结（使用PyInstaller打包）
            if getattr(sys, "frozen", False):
                # 处理不同操作系统的打包路径
                if sys.platform == "win32":
                    app_path = sys.executable
                    # 检查路径是否包含空格，如果包含则加引号
                    if " " in app_path:
                        app_path = f'"{app_path}"'
                    return app_path
                elif sys.platform == "darwin":
                    # macOS上，需要处理 .app/Contents/MacOS/ 结构
                    bundle_dir = os.path.dirname(sys.executable)
                    if ".app/Contents/MacOS" in bundle_dir:
                        # 如果是通过pyinstaller打包的macOS应用
                        app_path = os.path.dirname(
                            bundle_dir.split(".app/Contents/MacOS")[0] + ".app"
                        )
                        if " " in app_path:
                            app_path = f'"{app_path}"'
                        return app_path
                    else:
                        # 如果是其他类型的打包
                        app_path = sys.executable
                        if " " in app_path:
                            app_path = f'"{app_path}"'
                        return app_path
                else:
                    # Linux或其他系统
                    app_path = sys.executable
                    if " " in app_path:
                        app_path = f'"{app_path}"'
                    return app_path
            else:
                # 未冻结（开发模式）
                if sys.platform == "win32":
                    # Windows下获取主脚本路径
                    main_script = os.path.abspath(sys.argv[0])
                    if " " in main_script:
                        main_script = f'"{main_script}"'
                    return main_script
                elif sys.platform == "darwin":
                    # macOS下获取主脚本路径
                    main_script = os.path.abspath(sys.argv[0])
                    if " " in main_script:
                        main_script = f'"{main_script}"'
                    return main_script
                else:
                    # Linux或其他系统获取主脚本路径
                    main_script = os.path.abspath(sys.argv[0])
                    if " " in main_script:
                        main_script = f'"{main_script}"'
                    return main_script
        except Exception as e:
            # 记录错误并返回合理的默认值
            logging.error(f"获取应用路径时出错: {e}")

            # 尝试返回一个合理的默认值
            try:
                # 尝试使用当前工作目录作为备选
                default_path = os.path.abspath(os.getcwd())
                if " " in default_path and sys.platform == "win32":
                    default_path = f'"{default_path}"'
                return default_path
            except:
                # 如果上述方法都失败，返回None
                return None

    def _get_autostart_dir(self):
        """获取自启动目录路径"""
        if sys.platform.startswith("darwin"):
            # macOS: ~/Library/LaunchAgents
            autostart_dir = os.path.join(
                os.path.expanduser("~"), "Library", "LaunchAgents"
            )
        elif not sys.platform.startswith("win"):
            # Linux: ~/.config/autostart
            autostart_dir = os.path.join(
                os.path.expanduser("~"), ".config", "autostart"
            )
        else:
            # Windows没有专用目录，返回None
            return None

        # 确保目录存在
        os.makedirs(autostart_dir, exist_ok=True)
        return autostart_dir

    def _get_autostart_file_path(self):
        """获取自启动文件路径"""
        autostart_dir = self._get_autostart_dir()
        if not autostart_dir:
            return None

        if sys.platform.startswith("darwin"):
            # macOS: plist文件
            return os.path.join(autostart_dir, f"com.{AUTHOR}.{APP_NAME}.plist")
        else:
            # Linux: desktop文件
            return os.path.join(autostart_dir, f"{APP_NAME.lower()}.desktop")

    def _create_macos_plist(self, app_path):
        """创建macOS的plist文件用于自启动"""
        # 处理app_path，确保它是一个有效的命令
        if " " in app_path and not (
            app_path.startswith('"') and app_path.endswith('"')
        ):
            # 如果路径包含空格但没有被引号包围，则添加引号（安全措施）
            app_path = f'"{app_path}"'

        # 在macOS上，一些命令需要完整路径
        if app_path.startswith("/usr/bin/python") or app_path.startswith(
            "/usr/bin/python3"
        ):
            # 确保python是完整路径
            pass
        elif "python" in app_path.lower() and not app_path.startswith("/"):
            # 尝试使用完整路径
            app_path = app_path.replace("python", "/usr/bin/python")

        # 对于macOS，使用shell包装命令以确保环境变量正确设置
        command = f"/bin/bash -c {app_path}"

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{AUTHOR}.{APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>{os.path.dirname(app_path.strip('"'))}</string>
    <key>StandardOutPath</key>
    <string>/tmp/{APP_NAME.lower()}_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/{APP_NAME.lower()}_stderr.log</string>
</dict>
</plist>
"""
        return plist_content

    def _create_linux_desktop(self, app_path):
        """创建Linux的desktop文件用于自启动"""
        # 查找应用程序图标路径
        import sys

        icon_path = ""
        try:
            # 尝试找到应用图标
            possible_icon_paths = [
                # 如果应用被安装
                f"/usr/share/icons/hicolor/scalable/apps/{APP_NAME.lower()}.svg",
                f"/usr/share/icons/hicolor/128x128/apps/{APP_NAME.lower()}.png",
                # 如果使用的是开发脚本
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(sys.modules["__main__"].__file__),
                        "assets",
                        "images",
                        "icon.svg",
                    )
                ),
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(sys.modules["__main__"].__file__),
                        "assets",
                        "images",
                        "icon.png",
                    )
                ),
            ]

            for path in possible_icon_paths:
                if os.path.exists(path):
                    icon_path = path
                    break

            if not icon_path:
                self.logger.warning(f"未找到应用图标，将使用默认图标名称: {APP_NAME.lower()}")
                icon_path = APP_NAME.lower()

        except Exception as e:
            self.logger.warning(f"查找图标路径时出错: {e}")
            icon_path = APP_NAME.lower()  # 使用默认图标名

        # 确保命令可以在任何目录下执行
        if " " in app_path and not (
            app_path.startswith('"') and app_path.endswith('"')
        ):
            app_path = f'"{app_path}"'

        # 使用bash -c确保环境变量正确加载
        command = f"bash -c {app_path}"

        desktop_content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Exec={command}
Terminal=false
Icon={icon_path}
Comment={APP_NAME} 自动启动
Categories=Utility;
X-GNOME-Autostart-enabled=true
StartupNotify=false
Hidden=false
"""
        return desktop_content

    def is_autostart_enabled(self):
        """检查应用程序是否设置为开机自启动"""
        try:
            # Windows系统
            if sys.platform.startswith("win"):
                if "winreg" not in sys.modules:
                    self.logger.warning("Windows注册表模块未导入，开机自启动检查失败")
                    return False

                app_path = self.get_app_path()
                if not app_path:
                    self.logger.warning("无法获取应用程序路径")
                    return False

                # 打开注册表项
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_READ,
                )

                try:
                    # 尝试读取注册表值
                    value, _ = winreg.QueryValueEx(key, APP_NAME)
                    exists = True
                except FileNotFoundError:
                    # 注册表项不存在
                    exists = False

                winreg.CloseKey(key)
                self.logger.debug(f"Windows自启动状态检查: {exists}")
                return exists

            # macOS系统
            if sys.platform.startswith("darwin"):
                autostart_file = self._get_autostart_file_path()
                exists = autostart_file and os.path.exists(autostart_file)
                self.logger.debug(f"macOS自启动状态检查: {exists}")
                return exists

            # Linux系统
            autostart_file = self._get_autostart_file_path()
            exists = autostart_file and os.path.exists(autostart_file)
            self.logger.debug(f"Linux自启动状态检查: {exists}")
            return exists

        except Exception as e:
            self.logger.error(f"检查开机自启动状态时出错: {e}")
            return False

        except Exception as e:
            self.logger.error(f"检查开机自启动状态时出错: {e}")
            return False

    def set_autostart(self, enable):
        """设置开机自启动状态

        Args:
            enable (bool): True表示启用开机自启动，False表示禁用

        Returns:
            bool: 操作是否成功
        """
        try:
            app_path = self.get_app_path()
            if not app_path:
                self.logger.error("无法获取应用程序路径，无法设置自启动")
                return False

            # 检查当前状态，如果状态相同则不做改变
            current_state = self.is_autostart_enabled()
            if current_state == enable:
                self.logger.debug(f"自启动状态已经是{'启用' if enable else '禁用'}状态，无需更改")
                return True

            # Windows系统
            if sys.platform.startswith("win"):
                if "winreg" not in sys.modules:
                    self.logger.warning("Windows注册表模块未导入，开机自启动设置失败")
                    return False

                # 打开注册表项
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE,
                )

                if enable:
                    # 添加自启动项
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{app_path}"')
                    self.logger.info(f"Windows: 已添加开机自启动: {app_path}")
                else:
                    # 移除自启动项
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                        self.logger.info("Windows: 已移除开机自启动")
                    except FileNotFoundError:
                        # 注册表项不存在，无需处理
                        self.logger.debug("Windows: 移除自启动项时未找到注册表项，可能已经不存在")

                winreg.CloseKey(key)
                return True

            # macOS系统
            elif sys.platform.startswith("darwin"):
                autostart_file = self._get_autostart_file_path()

                if enable:
                    # 创建plist文件
                    plist_content = self._create_macos_plist(app_path)
                    with open(autostart_file, "w") as f:
                        f.write(plist_content)
                    self.logger.info(f"macOS: 已添加开机自启动: {app_path}")
                    # 设置文件权限
                    os.chmod(autostart_file, 0o644)
                else:
                    # 删除plist文件
                    if os.path.exists(autostart_file):
                        os.remove(autostart_file)
                        self.logger.info("macOS: 已移除开机自启动")

                return True

            # Linux系统
            else:
                autostart_file = self._get_autostart_file_path()

                if enable:
                    # 创建desktop文件
                    desktop_content = self._create_linux_desktop(app_path)
                    with open(autostart_file, "w") as f:
                        f.write(desktop_content)
                    self.logger.info(f"Linux: 已添加开机自启动: {app_path}")
                    # 设置文件权限
                    os.chmod(autostart_file, 0o755)
                else:
                    # 删除desktop文件
                    if os.path.exists(autostart_file):
                        os.remove(autostart_file)
                        self.logger.info("Linux: 已移除开机自启动")

                return True

        except Exception as e:
            self.logger.error(f"设置开机自启动时出错: {e}")
            return False


# 创建全局设置实例
settings_manager = Settings()


def get_settings():
    """获取设置管理器实例"""
    return settings_manager
