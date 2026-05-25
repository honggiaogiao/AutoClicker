"""
截图 AutoClicker 窗口并裁剪。
完全使用标准库 + PIL，无须额外依赖。
"""
from PIL import ImageGrab
import subprocess
import time
import sys
import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. 启动连点器（后台）
proc = subprocess.Popen(
    [sys.executable, "src/main.py"],
    cwd=project_dir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("AutoClicker 已启动")

# 2. 等待窗口出现
time.sleep(3)

# 3. 全屏截图
full = ImageGrab.grab()
w, h = full.size
print(f"全屏尺寸: {w}x{h}")

# 4. 窗口默认居中，尺寸约 350x260
cx, cy = w // 2, h // 2
left = cx - 200
top = cy - 160
right = cx + 200
bottom = cy + 160

cropped = full.crop((left, top, right, bottom))
output = os.path.join(project_dir, "docs", "screenshot.png")
cropped.save(output)
print(f"截图已保存: {output}")
print(f"尺寸: {cropped.size[0]}x{cropped.size[1]}")

# 5. 关闭连点器
proc.terminate()
proc.wait(timeout=3)
print("已关闭")
