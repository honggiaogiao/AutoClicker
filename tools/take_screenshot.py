"""
截图工具：先启动连点器，等待后截图，然后关闭程序。
"""
import subprocess
import time
from PIL import ImageGrab
import os
import signal
import sys

# 启动连点器
proc = subprocess.Popen(
    [sys.executable, "src/main.py"],
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

print("连点器已启动，等待 3 秒...")
time.sleep(3)

# 截图
screenshot = ImageGrab.grab()
output_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "screenshot.png"
)
screenshot.save(output_path)
print(f"截图已保存: {output_path} ({os.path.getsize(output_path)} bytes)")

# 关闭连点器
proc.terminate()
proc.wait(timeout=5)
print("连点器已关闭")
