"""
AutoClicker - 核心连点引擎

负责键盘/鼠标键的模拟点击，运行在独立线程中。
支持开始、停止、动态修改目标和间隔。
"""

import threading
import time
import keyboard
import mouse


# 鼠标键的别名映射，统一为 mouse.click() 接受的格式
MOUSE_BUTTON_MAP = {
    "左键": "left",
    "右键": "right",
    "中键": "middle",
    "侧键X1": "x1",
    "侧键X2": "x2",
}


class Clicker:
    """连点器核心类，管理连点线程的生命周期。"""

    def __init__(self):
        self._target_key = "a"          # 当前要连点的键
        self._is_mouse = False          # True=鼠标键, False=键盘键
        self._interval_ms = 100         # 间隔（毫秒）
        self._stop_event = threading.Event()
        self._thread = None
        self._lock = threading.Lock()   # 保护配置读取的线程安全

    # ─── 配置接口 ────────────────────────────────────

    def set_keyboard_target(self, key_name: str):
        """设置连点目标为一个键盘键。"""
        with self._lock:
            self._target_key = key_name
            self._is_mouse = False

    def set_mouse_target(self, button_label: str):
        """设置连点目标为一个鼠标键。

        Args:
            button_label: "左键", "右键", "中键", "侧键X1", "侧键X2"
        """
        mapped = MOUSE_BUTTON_MAP.get(button_label)
        if mapped is None:
            raise ValueError(f"不支持的鼠标键: {button_label}")
        with self._lock:
            self._target_key = mapped
            self._is_mouse = True

    def set_interval(self, ms: int):
        """设置连点间隔（毫秒），最小 10ms。"""
        if ms < 10:
            ms = 10
        with self._lock:
            self._interval_ms = ms

    def get_target_display(self) -> str:
        """获取连点目标的显示名称（用于界面展示）。"""
        with self._lock:
            return self._target_key

    def get_interval(self) -> int:
        """获取当前间隔（毫秒）。"""
        with self._lock:
            return self._interval_ms

    # ─── 运行控制 ────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        """启动连点（如果已经在运行则忽略）。"""
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """请求停止连点，等待线程退出。"""
        if not self.is_running:
            return
        self._stop_event.set()
        self._thread.join(timeout=2.0)
        self._thread = None

    # ─── 内部循环 ────────────────────────────────────

    def _run(self):
        """连点主循环，运行在后台线程中。"""
        while not self._stop_event.is_set():
            with self._lock:
                target = self._target_key
                is_mouse = self._is_mouse
                interval_s = self._interval_ms / 1000.0

            # 执行一次点击
            try:
                if is_mouse:
                    mouse.click(button=target)
                else:
                    keyboard.press_and_release(target)
            except Exception:
                # 模拟失败时静默跳过，不崩溃
                pass

            # 等待间隔时间（分段等待以便及时响应停止信号）
            self._sleep_with_early_stop(interval_s)

    def _sleep_with_early_stop(self, seconds: float):
        """分段休眠，在休眠期间也能快速响应停止信号。"""
        # 每 50ms 检查一次停止信号
        chunk = 0.05
        remaining = seconds
        while remaining > 0 and not self._stop_event.is_set():
            sleep_time = min(chunk, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time
