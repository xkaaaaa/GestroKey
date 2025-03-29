@echo off
echo ����׼�����GestroKeyӦ��...

REM �л����������ļ�����Ŀ¼
cd /d "%~dp0"

REM �������Ŀ¼
if exist build rmdir /s /q build
mkdir build

REM ʹ��Nuitka���Ӧ��
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
    --file-description="������ƿ���Ӧ��" ^
    --copyright="GPLv3" ^
    --file-version="1.0.0" ^
    --product-version="1.0.0" ^
    src\main.py

if %ERRORLEVEL% NEQ 0 (
    echo ������̳����������������Ϣ��
    pause
    exit /b 1
)

REM ���������ļ���buildĿ¼�����û��޸ģ�
copy src\gestures.json build\
copy src\settings.json build\

echo �����ɣ���ִ���ļ�λ��buildĿ¼��
echo ע��: gestures.json��settings.json�Ѹ��Ƶ�buildĿ¼���û�����ֱ���޸���Щ�ļ�
pause