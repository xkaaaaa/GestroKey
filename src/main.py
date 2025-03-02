import customtkinter as ctk
from tkinter import messagebox
from app.ink_painter import InkPainter

# 设置外观模式和颜色主题
ctk.set_appearance_mode("System")  # 可选值: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # 可选值: "blue", "green", "dark-blue"

class MainApp:
    def __init__(self):
        # 创建主窗口
        self.window = ctk.CTk()
        self.window.title("隐绘助手")
        self.window.geometry("300x200")  # 设置窗口尺寸
        self.window.attributes("-topmost", True)  # 保持在顶层
        
        # 状态控制
        self.painter = None
        self.painting = False

        # 添加标签
        self.label = ctk.CTkLabel(
            self.window,
            text="点击按钮开始或停止绘画",
            font=("Arial", 12),
            text_color="#FFFFFF"  # 文字颜色
        )
        self.label.pack(pady=20)

        # 添加“开始/停止”按钮
        self.toggle_button = ctk.CTkButton(
            self.window,
            text="开始绘画",
            command=self.toggle_painting,
            width=120,
            height=40,
            corner_radius=10,  # 圆角半径
            fg_color="#1F6AA5",  # 按钮背景颜色
            hover_color="#144870"  # 鼠标悬停时的颜色
        )
        self.toggle_button.pack(pady=10)

        # 添加“退出”按钮
        self.exit_button = ctk.CTkButton(
            self.window,
            text="退出",
            command=self.on_close,
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#D32F2F",  # 按钮背景颜色
            hover_color="#9A0000"  # 鼠标悬停时的颜色
        )
        self.exit_button.pack(pady=10)

        # 启动 Tkinter 事件循环
        self.window.after(100, self.check_painter_status)

    def check_painter_status(self):
        """定时检查绘画器状态"""
        if self.painting and (not self.painter or not self.painter.running):
            self.stop_painting()
        self.window.after(500, self.check_painter_status)

    def toggle_painting(self):
        """切换绘画状态"""
        try:
            if not self.painting:
                self.start_painting()
            else:
                self.stop_painting()
        except Exception as e:
            messagebox.showerror("错误", f"切换状态时发生错误：{str(e)}")
            self.stop_painting()

    def start_painting(self):
        """启动绘画功能"""
        self.painter = InkPainter()
        self.painting = True
        self.toggle_button.configure(text="停止绘画")  # 更新按钮文本
        self.label.configure(text="绘画已启动")

    def stop_painting(self):
        """停止绘画功能"""
        if self.painter:
            try:
                self.painter.shutdown()
            except Exception as e:
                messagebox.showerror("错误", f"关闭绘画时发生错误：{str(e)}")
            finally:
                self.painter = None
                
        self.painting = False
        self.toggle_button.configure(text="开始绘画")  # 更新按钮文本
        self.label.configure(text="绘画已停止")

    def on_close(self):
        """退出程序"""
        if self.painting:
            if not messagebox.askokcancel("确认", "绘画功能仍在运行，确定要退出吗？"):
                return
                
        self.stop_painting()
        self.window.quit()
        self.window.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.window.mainloop()  # 启动 Tkinter 主循环