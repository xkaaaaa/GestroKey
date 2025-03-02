"""
日志记录器
调用说明：
log(文件名, 日志信息, level='info')
"""

import os
from datetime import datetime

def log(filename, *args, level='info'):
    
    # 直接构造Roaming目录路径
    user_profile = os.getenv('USERPROFILE')
    if not user_profile:
        print("无法获取用户目录")
        return
    
    appdata_dir = os.path.join(user_profile, 'AppData', 'Roaming')
    if not os.path.exists(appdata_dir):
        print("Roaming目录不存在")
        return

    log_dir = os.path.join(appdata_dir, 'GestroKey', 'Logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"{filename}_{datetime.now().strftime('%Y%m%d')}.txt")
    
    for arg in args:
        message = str(arg)
        try:
            print(filename + ':' + message)
            timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]')
            log_entry = f"{timestamp} [{level.upper()}] {message}\n"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"日志记录失败: {str(e)}")

if __name__ == '__main__':
    log('test', 'Hello, World!')