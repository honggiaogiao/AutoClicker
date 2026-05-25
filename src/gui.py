"""
AutoClicker - GUI 界面

简洁直观的淡蓝色主题窗口。
支持键盘键捕获、鼠标键选择、间隔设置、开始/停止控制。
键盘捕获使用 keyboard 库全局钩子，不受输入法影响。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import keyboard
import ctypes
from clicker import Clicker


# ─── 配色方案 ─────────────────────────────────────

COLORS = {
    "bg_window":   "#EAF2FA",
    "bg_frame":    "#D4E8F7",
    "fg_text":     "#2C3E50",
    "fg_muted":    "#7F8C8D",
    "btn_start":   "#27AE60",
    "btn_start_hover": "#2ECC71",
    "btn_stop":    "#E74C3C",
    "btn_stop_hover": "#EC7063",
    "btn_capture": "#5DADE2",
    "entry_bg":    "#FFFFFF",
}


def is_admin():
    """检查当前程序是否以管理员权限运行。"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class AutoClickerGUI:
    """连点器主界面。"""

    def __init__(self):
        self.clicker = Clicker()

        # 窗口
        self.root = tk.Tk()
        self.root.title("AutoClicker")
        self.root.geometry("350x260")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg_window"])
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 变量
        self._mode_var = tk.StringVar(value="keyboard")
        self._mouse_var = tk.StringVar(value="左键")
        self._interval_var = tk.StringVar(value="100")
        self._captured_key = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="空闲")
        self._topmost_var = tk.BooleanVar(value=False)

        # 捕获状态
        self._is_capturing = False
        self._capture_hook_id = None

        # 管理员权限提示（仅启动时提醒一次）
        self._admin_warned = False

        # 构建界面
        self._build_widgets()

    # ─── 界面搭建 ────────────────────────────────────

    def _build_widgets(self):
        root = self.root

        # ── 连点键选择 ────────────────────────────
        frame_key = tk.LabelFrame(
            root, text=" 选择连点键 ", font=("Microsoft YaHei", 10),
            bg=COLORS["bg_window"], fg=COLORS["fg_text"],
            padx=10, pady=8
        )
        frame_key.pack(fill="x", padx=15, pady=(12, 0))

        # 第一行：模式切换 + 选择控件
        row1 = tk.Frame(frame_key, bg=COLORS["bg_window"])
        row1.pack(fill="x")

        tk.Radiobutton(
            row1, text="键盘", variable=self._mode_var,
            value="keyboard", command=self._on_mode_switch,
            bg=COLORS["bg_window"], fg=COLORS["fg_text"],
            selectcolor=COLORS["bg_frame"], font=("Microsoft YaHei", 9)
        ).pack(side="left", padx=(0, 5))

        tk.Radiobutton(
            row1, text="鼠标", variable=self._mode_var,
            value="mouse", command=self._on_mode_switch,
            bg=COLORS["bg_window"], fg=COLORS["fg_text"],
            selectcolor=COLORS["bg_frame"], font=("Microsoft YaHei", 9)
        ).pack(side="left", padx=(0, 10))

        # 捕获按键按钮
        self._btn_capture = tk.Button(
            row1, text="点击捕获按键", width=16,
            bg=COLORS["btn_capture"], fg="white",
            font=("Microsoft YaHei", 9), relief="flat",
            activebackground="#4A9BD9", cursor="hand2",
            command=self._on_capture_key
        )
        self._btn_capture.pack(side="left")

        # 鼠标下拉框
        self._combo_mouse = ttk.Combobox(
            row1, textvariable=self._mouse_var,
            values=["左键", "右键", "中键", "侧键X1", "侧键X2"],
            state="readonly", width=12, font=("Microsoft YaHei", 9)
        )

        # 第二行：显示当前选中的键
        row2 = tk.Frame(frame_key, bg=COLORS["bg_window"])
        row2.pack(fill="x", pady=(4, 0))

        tk.Label(
            row2, text="当前键:",
            font=("Microsoft YaHei", 9), fg=COLORS["fg_text"],
            bg=COLORS["bg_window"]
        ).pack(side="left", padx=(0, 4))

        self._label_key_display = tk.Label(
            row2, text="（未选择）", width=18,
            font=("Microsoft YaHei", 10, "bold"), fg=COLORS["fg_text"],
            bg="#FFFFFF", relief="solid", bd=1
        )
        self._label_key_display.pack(side="left")

        # ── 时间间隔 ──────────────────────────────
        frame_interval = tk.LabelFrame(
            root, text=" 时间间隔 ", font=("Microsoft YaHei", 10),
            bg=COLORS["bg_window"], fg=COLORS["fg_text"],
            padx=10, pady=8
        )
        frame_interval.pack(fill="x", padx=15, pady=(8, 0))

        self._entry_interval = tk.Entry(
            frame_interval, textvariable=self._interval_var,
            width=10, font=("Microsoft YaHei", 10),
            bg=COLORS["entry_bg"], fg=COLORS["fg_text"],
            relief="solid", bd=1, justify="center"
        )
        self._entry_interval.pack(side="left", padx=(0, 5))

        # 输入校验：只允许数字
        vcmd = (root.register(self._validate_number), "%P")
        self._entry_interval.config(validate="key", validatecommand=vcmd)

        tk.Label(
            frame_interval, text="毫秒 (ms)   最小 10ms",
            font=("Microsoft YaHei", 9), fg=COLORS["fg_muted"],
            bg=COLORS["bg_window"]
        ).pack(side="left")

        # ── 控制按钮 ──────────────────────────────
        frame_btn = tk.Frame(root, bg=COLORS["bg_window"])
        frame_btn.pack(fill="x", padx=15, pady=(10, 0))

        self._btn_start = tk.Button(
            frame_btn, text="开始", width=10,
            bg=COLORS["btn_start"], fg="white",
            font=("Microsoft YaHei", 10, "bold"), relief="flat",
            activebackground=COLORS["btn_start_hover"], cursor="hand2",
            command=self._on_start
        )
        self._btn_start.pack(side="left", padx=(0, 10))

        self._btn_stop = tk.Button(
            frame_btn, text="停止", width=10,
            bg=COLORS["btn_stop"], fg="white",
            font=("Microsoft YaHei", 10, "bold"), relief="flat",
            activebackground=COLORS["btn_stop_hover"], cursor="hand2",
            state="disabled",
            command=self._on_stop
        )
        self._btn_stop.pack(side="left")

        # 窗口置顶复选框
        tk.Checkbutton(
            frame_btn, text="窗口置顶", variable=self._topmost_var,
            command=self._on_topmost_toggle,
            bg=COLORS["bg_window"], fg=COLORS["fg_text"],
            selectcolor=COLORS["bg_frame"], font=("Microsoft YaHei", 9)
        ).pack(side="right", padx=(10, 0))

        # ── 状态栏 ────────────────────────────────
        self._label_status = tk.Label(
            root, textvariable=self._status_var,
            font=("Microsoft YaHei", 9), fg=COLORS["fg_muted"],
            bg=COLORS["bg_window"], anchor="w"
        )
        self._label_status.pack(fill="x", padx=18, pady=(6, 0))

        # 管理员权限提示栏
        if not is_admin():
            tk.Label(
                root,
                text="提示：如果捕获按键无效，请右键以管理员身份运行",
                font=("Microsoft YaHei", 8), fg="#E74C3C",
                bg=COLORS["bg_window"], anchor="w"
            ).pack(fill="x", padx=18)

        # 默认显示键盘模式
        self._on_mode_switch()

    # ─── 模式切换 ────────────────────────────────────

    def _on_mode_switch(self):
        """键盘/鼠标模式切换。"""
        if self._mode_var.get() == "keyboard":
            self._btn_capture.pack(side="left")
            self._combo_mouse.pack_forget()
        else:
            self._btn_capture.pack_forget()
            self._combo_mouse.pack(side="left")

    # ─── 键盘捕获（使用 keyboard 库全局钩子） ──────────

    def _on_capture_key(self):
        """进入捕获模式，注册全局键盘钩子。"""
        self._is_capturing = True
        self._btn_capture.config(text="按下任意键...", state="disabled")
        self._captured_key.set("")
        self._label_key_display.config(text="等待按键...", fg=COLORS["fg_muted"])
        self._status_var.set("请按下键盘上的任意键...")

        # 注册 keyboard 全局钩子（绕过输入法/焦点限制）
        self._capture_hook_id = keyboard.on_press(self._on_keyboard_captured)

    def _on_keyboard_captured(self, event):
        """keyboard 全局钩子回调（在 keyboard 线程中执行）。"""
        key_name = event.name

        # 忽略修饰键单独按下
        modifiers = {"shift", "ctrl", "alt", "windows", "cmd",
                     "left shift", "right shift", "left ctrl", "right ctrl",
                     "left alt", "right alt", "left windows", "right windows"}
        if key_name and key_name.lower() in modifiers:
            return  # 继续监听

        # 取消钩子（只捕获一次）
        if self._capture_hook_id is not None:
            keyboard.unhook(self._capture_hook_id)
            self._capture_hook_id = None

        # 在主线程中更新 UI
        self.root.after(0, self._on_key_captured, key_name)

        # 返回 False 表示取消此回调注册（双重保险）
        return False

    def _on_key_captured(self, key_name: str):
        """捕获到键后回到主线程更新界面。"""
        if not self._is_capturing:
            return  # 已被其他操作取消

        self._is_capturing = False
        display_name = key_name.upper() if len(key_name) == 1 else key_name
        self._captured_key.set(key_name)
        self._btn_capture.config(text="重新捕获", state="normal")
        self._label_key_display.config(text=display_name, fg=COLORS["fg_text"])
        self._status_var.set(f"已捕获键盘键: {display_name}")
        self.clicker.set_keyboard_target(key_name)

    # ─── 开始/停止 ────────────────────────────────────

    def _on_start(self):
        # 校验间隔
        interval_text = self._interval_var.get().strip()
        if not interval_text:
            messagebox.showwarning("提示", "请输入时间间隔")
            return

        try:
            interval = int(interval_text)
        except ValueError:
            messagebox.showwarning("提示", "时间间隔必须为整数")
            return

        if interval < 10:
            messagebox.showwarning("提示", "时间间隔不能小于 10 毫秒")
            return

        # 校验键是否已选择
        if self._mode_var.get() == "keyboard":
            if not self._captured_key.get():
                messagebox.showwarning("提示", "请先捕获一个键盘键")
                return
            self.clicker.set_keyboard_target(self._captured_key.get())
        else:
            self.clicker.set_mouse_target(self._mouse_var.get())

        self.clicker.set_interval(interval)
        self.clicker.start()

        self._btn_start.config(state="disabled")
        self._btn_stop.config(state="normal")
        self._status_var.set("运行中...")
        self.root.title("AutoClicker (运行中...)")

    def _on_stop(self):
        self.clicker.stop()

        self._btn_start.config(state="normal")
        self._btn_stop.config(state="disabled")
        self._status_var.set("已停止")
        self.root.title("AutoClicker")

    # ─── 窗口置顶 ────────────────────────────────────

    def _on_topmost_toggle(self):
        """切换窗口置顶状态。"""
        self.root.attributes("-topmost", self._topmost_var.get())

    # ─── 窗口关闭 ────────────────────────────────────

    def _on_close(self):
        if self.clicker.is_running:
            self.clicker.stop()
        # 清理 keyboard 钩子
        if self._capture_hook_id is not None:
            keyboard.unhook(self._capture_hook_id)
        self.root.destroy()

    # ─── 输入校验 ────────────────────────────────────

    @staticmethod
    def _validate_number(value: str) -> bool:
        if value == "":
            return True
        return value.isdigit()

    # ─── 启动 ────────────────────────────────────────

    def run(self):
        self.root.mainloop()
