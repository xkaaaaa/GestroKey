import getpass
import json
import logging
import os
import sys

from core.logger import get_logger
from version import APP_NAME, AUTHOR

if sys.platform.startswith("win"):
    import winreg

_settings_instance = None


class Settings:
    def __init__(self):
        self.logger = get_logger("Settings")
        self.settings = self._load_default_settings()
        self.settings_file = self._get_settings_file_path()
        self.saved_settings = None

        self.load()

    def _load_default_settings(self):
        try:
            default_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_settings.json")

            if os.path.exists(default_settings_path):
                with open(default_settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                return settings
            else:
                raise FileNotFoundError(f"默认设置文件不存在: {default_settings_path}")
        except Exception as e:
            self.logger.error(f"加载默认设置失败: {e}")
            raise

    def _get_settings_file_path(self):
        if sys.platform.startswith("win"):
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(user_dir, f".{AUTHOR}", APP_NAME.lower(), "config")
        elif sys.platform.startswith("darwin"):
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(user_dir, "Library", "Application Support", f"{AUTHOR}", APP_NAME, "config")
        else:
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
            config_dir = os.path.join(xdg_config_home, f"{AUTHOR}", APP_NAME, "config")

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "settings.json")

    def load(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                for key, value in loaded_settings.items():
                    if key in self.settings:
                        self.settings[key] = value

                self.saved_settings = self.settings.copy()
            else:
                self.save()
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            raise

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            self.saved_settings = self.settings.copy()
            return True
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False

    def get(self, key, default=None):
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
            return self.settings.get(key, default)

    def set(self, key, value):
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
            return True
        else:
            old_value = self.settings.get(key)
            if old_value != value:
                self.settings[key] = value
            return True

    def reset_to_default(self):
        try:
            default_settings = self._load_default_settings()
            if self.settings != default_settings:
                self.settings = default_settings

            success = self.save()
            if success:
                self.saved_settings = self.settings.copy()

                if self.is_autostart_enabled():
                    self.set_autostart(False)

            return success
        except Exception as e:
            self.logger.error(f"重置为默认设置失败: {e}")
            return False

    def has_changes(self):
        self.logger.debug(f"设置库检查变更开始: 当前设置数量={len(self.settings) if self.settings else 0}, 已保存设置数量={len(self.saved_settings) if self.saved_settings else 0}")
        
        if not self.saved_settings:
            result = True if self.settings else False
            self.logger.debug(f"设置库检查变更: 没有已保存设置记录, 结果={result}")
            return result

        for key, value in self.settings.items():
            saved_value = self.saved_settings.get(key, '不存在')
            if key not in self.saved_settings or self.saved_settings[key] != value:
                self.logger.debug(f"设置库检查变更: 发现差异 - 键={key}")
                self.logger.debug(f"  当前值: {value} (类型: {type(value)})")
                self.logger.debug(f"  已保存值: {saved_value} (类型: {type(saved_value)})")
                return True

        for key in self.saved_settings:
            if key not in self.settings:
                self.logger.debug(f"设置库检查变更: 已保存的键在当前设置中不存在 - 键={key}")
                return True

        self.logger.debug("设置库检查变更: 没有发现差异")
        return False

    def get_app_path(self):
        def _quote_if_needed(path):
            return f'"{path}"' if " " in path else path
        
        try:
            if getattr(sys, "frozen", False):
                if sys.platform == "darwin":
                    bundle_dir = os.path.dirname(sys.executable)
                    if ".app/Contents/MacOS" in bundle_dir:
                        app_path = os.path.dirname(
                            bundle_dir.split(".app/Contents/MacOS")[0] + ".app"
                        )
                        return _quote_if_needed(app_path)
                
                return _quote_if_needed(sys.executable)
            else:
                main_script = os.path.abspath(sys.argv[0])
                return _quote_if_needed(main_script)
        except Exception as e:
            logging.error(f"获取应用路径时出错: {e}")

            try:
                default_path = os.path.abspath(os.getcwd())
                return _quote_if_needed(default_path) if sys.platform == "win32" else default_path
            except:
                return None

    def get_app_path_with_silent(self):
        app_path = self.get_app_path()
        if not app_path:
            return None
        
        if app_path.endswith('"'):
            return app_path[:-1] + ' --silent"'
        else:
            return app_path + ' --silent'

    def _get_autostart_dir(self):
        if sys.platform.startswith("darwin"):
            autostart_dir = os.path.join(
                os.path.expanduser("~"), "Library", "LaunchAgents"
            )
        elif not sys.platform.startswith("win"):
            autostart_dir = os.path.join(
                os.path.expanduser("~"), ".config", "autostart"
            )
        else:
            return None

        os.makedirs(autostart_dir, exist_ok=True)
        return autostart_dir

    def _get_autostart_file_path(self):
        autostart_dir = self._get_autostart_dir()
        if not autostart_dir:
            return None

        if sys.platform.startswith("darwin"):
            return os.path.join(autostart_dir, f"com.{AUTHOR}.{APP_NAME}.plist")
        else:
            return os.path.join(autostart_dir, f"{APP_NAME.lower()}.desktop")

    def _normalize_app_path(self, app_path):
        if " " in app_path and not (app_path.startswith('"') and app_path.endswith('"')):
            return f'"{app_path}"'
        return app_path

    def _get_icon_path(self):
        try:
            possible_icon_paths = [
                f"/usr/share/icons/hicolor/scalable/apps/{APP_NAME.lower()}.svg",
                f"/usr/share/icons/hicolor/128x128/apps/{APP_NAME.lower()}.png",
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(sys.modules["__main__"].__file__),
                        "assets",
                        "images",
                        "app",
                        "icon.svg",
                    )
                ),
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(sys.modules["__main__"].__file__),
                        "assets",
                        "images",
                        "app",
                        "icon.png",
                    )
                ),
            ]

            for path in possible_icon_paths:
                if os.path.exists(path):
                    return path

            self.logger.warning(f"未找到应用图标，将使用默认图标名称: {APP_NAME.lower()}")
            return APP_NAME.lower()

        except Exception as e:
            self.logger.warning(f"查找图标路径时出错: {e}")
            return APP_NAME.lower()

    def _create_macos_plist(self, app_path):
        app_path = self._normalize_app_path(app_path)
        
        if "python" in app_path.lower() and not app_path.startswith("/usr/bin/python"):
            if not app_path.startswith("/"):
                app_path = app_path.replace("python", "/usr/bin/python")

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
        icon_path = self._get_icon_path()
        app_path = self._normalize_app_path(app_path)
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
        try:
            if sys.platform.startswith("win"):
                if "winreg" not in sys.modules:
                    self.logger.warning("Windows注册表模块未导入，开机自启动检查失败")
                    return False

                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_READ,
                )

                try:
                    value, _ = winreg.QueryValueEx(key, APP_NAME)
                    exists = True
                except FileNotFoundError:
                    exists = False

                winreg.CloseKey(key)
                return exists

            autostart_file = self._get_autostart_file_path()
            return autostart_file and os.path.exists(autostart_file)

        except Exception as e:
            self.logger.error(f"检查开机自启动状态时出错: {e}")
            return False

    def set_autostart(self, enable):
        try:
            app_path = self.get_app_path_with_silent()
            if not app_path:
                self.logger.error("无法获取应用程序路径，无法设置自启动")
                return False

            current_state = self.is_autostart_enabled()
            if current_state == enable:
                return True

            if sys.platform.startswith("win"):
                return self._set_windows_autostart(enable, app_path)
            elif sys.platform.startswith("darwin"):
                return self._set_macos_autostart(enable, app_path)
            else:
                return self._set_linux_autostart(enable, app_path)

        except Exception as e:
            self.logger.error(f"设置开机自启动时出错: {e}")
            return False

    def _set_windows_autostart(self, enable, app_path):
        if "winreg" not in sys.modules:
            self.logger.warning("Windows注册表模块未导入，开机自启动设置失败")
            return False

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
            self.logger.info(f"Windows: 已添加开机自启动: {app_path}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                self.logger.info("Windows: 已移除开机自启动")
            except FileNotFoundError:
                pass

        winreg.CloseKey(key)
        return True

    def _set_macos_autostart(self, enable, app_path):
        autostart_file = self._get_autostart_file_path()

        if enable:
            plist_content = self._create_macos_plist(app_path)
            with open(autostart_file, "w") as f:
                f.write(plist_content)
            self.logger.info(f"macOS: 已添加开机自启动: {app_path}")
            os.chmod(autostart_file, 0o644)
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)
                self.logger.info("macOS: 已移除开机自启动")

        return True

    def _set_linux_autostart(self, enable, app_path):
        autostart_file = self._get_autostart_file_path()

        if enable:
            desktop_content = self._create_linux_desktop(app_path)
            with open(autostart_file, "w") as f:
                f.write(desktop_content)
            self.logger.info(f"Linux: 已添加开机自启动: {app_path}")
            os.chmod(autostart_file, 0o755)
        else:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)
                self.logger.info("Linux: 已移除开机自启动")

        return True


settings_manager = Settings()


def get_settings():
    return settings_manager