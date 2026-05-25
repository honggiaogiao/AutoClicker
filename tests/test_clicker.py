"""
快速验证 Clicker 核心逻辑：
- 启动/停止状态切换
- 配置修改
- 间隔校验
"""

from clicker import Clicker
import time

c = Clicker()

# 1. 默认状态
print(f"[1] 初始状态: running={c.is_running}, target={c.get_target_display()}, interval={c.get_interval()}ms")
assert not c.is_running, "初始应为停止状态"
assert c.get_interval() == 100

# 2. 改变目标
c.set_keyboard_target("space")
print(f"[2] 设为空格键: target={c.get_target_display()}")
assert c.get_target_display() == "space"

c.set_mouse_target("右键")
print(f"[3] 设为鼠标右键: target={c.get_target_display()}")
assert c.get_target_display() == "right"

c.set_keyboard_target("a")
c.set_interval(200)
print(f"[4] 设为键盘A, 200ms: target={c.get_target_display()}, interval={c.get_interval()}ms")

# 3. 启动与停止
print("[5] 启动连点...", end=" ")
c.start()
assert c.is_running
print("OK, 运行中")
time.sleep(1)

print("[6] 停止连点...", end=" ")
c.stop()
assert not c.is_running
print("OK, 已停止")

# 4. 二次启动
print("[7] 再次启动/停止...", end=" ")
c.start()
time.sleep(0.5)
c.stop()
assert not c.is_running
print("OK")

# 5. 间隔下限
c.set_interval(5)
assert c.get_interval() == 10, f"最小间隔应为10ms, 实际={c.get_interval()}"
print(f"[8] 间隔下限保护: {c.get_interval()}ms (最小10ms)")

print("\n✅ 所有核心逻辑测试通过！")
