import tkinter as tk
from tkinter import messagebox
from app.ink_painter import InkPainter

class MainApp:
    def __init__(self):
        # 初始化主窗口
        self.window = tk.Tk()
        self.window.title("隐绘助手")
        self.window.geometry("300x200")
        self.window.resizable(False, False)
        
        # 状态控制
        self.painter = None
        self.painting = False
        
        # 初始化UI
        self.init_ui()
        
        # 窗口关闭处理
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_ui(self):
        """初始化用户界面"""
        # 状态标签
        self.status_label = tk.Label(
            self.window,
            text="状态：已停止",
            font=('微软雅黑', 12)
        )
        self.status_label.pack(pady=20)
        
        # 切换按钮
        self.toggle_btn = tk.Button(
            self.window,
            text="开始绘画",
            command=self.toggle_painting,
            bg="#4CAF50",
            fg="white",
            font=('微软雅黑', 14),
            width=15
        )
        self.toggle_btn.pack(pady=10)
        
        # 退出按钮
        exit_btn = tk.Button(
            self.window,
            text="退出程序",
            command=self.on_close,
            bg="#607D8B",
            fg="white",
            font=('微软雅黑', 12),
            width=10
        )
        exit_btn.pack(pady=5)

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
        self.status_label.config(text="状态：绘画中...", fg="green")
        self.toggle_btn.config(text="停止绘画", bg="#f44336")

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
        self.status_label.config(text="状态：已停止", fg="black")
        self.toggle_btn.config(text="开始绘画", bg="#4CAF50")

    def on_close(self):
        """窗口关闭时的清理操作"""
        if self.painting:
            if not messagebox.askokcancel("确认", "绘画功能仍在运行，确定要退出吗？"):
                return
                
        self.stop_painting()
        self.window.destroy()

    def run(self):
        """启动主循环"""
        self.window.mainloop()

if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except Exception as e:
        messagebox.showerror("致命错误", f"程序启动失败：{str(e)}")