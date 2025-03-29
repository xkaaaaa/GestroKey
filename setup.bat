@echo off
echo 正在准备打包GestroKey应用...

REM 切换到批处理文件所在目录
cd /d "%~dp0"

REM 创建输出目录
if exist build rmdir /s /q build
mkdir build

REM 使用Nuitka打包应用
python -m nuitka ^
    --standalone ^
    --windows-console-mode=disable ^
    --follow-imports ^
    --include-package=PyQt5 ^
    --include-package=numpy ^
    --include-package=pyautogui ^
    --include-package=psutil ^
    --include-package=PIL ^
    --include-module=win32api ^
    --include-module=win32con ^
    --include-module=pyperclip ^
    --include-module=keyboard ^
    --enable-plugin=pyqt5 ^
    --enable-plugin=pylint-warnings ^
    --mingw64 ^
    --remove-output ^
    --output-dir=build ^
    --include-data-dir=src\ui\assets=ui\assets ^
    --windows-icon-from-ico=src\ui\assets\icons\logo.ico ^
    --company-name="GestroKey" ^
    --product-name="GestroKey" ^
    --file-description="鼠标手势控制应用" ^
    --copyright="GPLv3" ^
    --file-version="1.0.0" ^
    --product-version="1.0.0" ^
    src\main.py

if %ERRORLEVEL% NEQ 0 (
    echo 打包过程出错，请检查以上输出信息。
    pause
    exit /b 1
)

REM 复制配置文件到build目录（供用户修改）
copy src\gestures.json build\
copy src\settings.json build\

echo 打包完成！可执行文件位于build目录中
echo 注意: gestures.json和settings.json已复制到build目录，用户可以直接修改这些文件
pause