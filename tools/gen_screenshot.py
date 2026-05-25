"""
根据设计规范生成 AutoClicker GUI 效果图。
准确反映实际界面布局和配色。
"""
from PIL import Image, ImageDraw, ImageFont
import os

output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(output_dir, "docs", "screenshot.png")

# 尺寸 350x260，与实际窗口一致
W, H = 350, 260
COLORS = {
    "bg_window":   "#EAF2FA",
    "bg_frame":    "#D4E8F7",
    "fg_text":     "#2C3E50",
    "fg_muted":    "#7F8C8D",
    "btn_start":   "#27AE60",
    "btn_stop":    "#E74C3C",
    "btn_capture": "#5DADE2",
    "entry_bg":    "#FFFFFF",
    "border":      "#BDC3C7",
}

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

img = Image.new("RGB", (W, H), hex_to_rgb(COLORS["bg_window"]))
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("msyh.ttc", 14)
    font_small = ImageFont.truetype("msyh.ttc", 12)
except:
    font = ImageFont.load_default()
    font_small = font

# ── 标题栏 ──
draw.rectangle([(0, 0), (W-1, 28)], fill=hex_to_rgb("#B0D0E8"))
draw.text((12, 5), "AutoClicker", fill="white", font=font_small)

# ── "选择连点键" 区域 ──
fy1 = 36
draw.rectangle([(12, fy1), (W-12, fy1+72)], outline=hex_to_rgb(COLORS["border"]), fill=hex_to_rgb("#F0F6FB"))
draw.text((20, fy1+4), " 选择连点键 ", fill=hex_to_rgb(COLORS["fg_text"]), font=font_small)

# 单选按钮 - 键盘(选中) 鼠标
draw.text((24, fy1+28), "◉ 键盘", fill=hex_to_rgb(COLORS["fg_text"]), font=font_small)
draw.text((92, fy1+28), "○ 鼠标", fill=hex_to_rgb(COLORS["fg_muted"]), font=font_small)

# 捕获按键按钮
btn_x, btn_y = 170, fy1+26
btn_w, btn_h = 110, 24
draw.rounded_rectangle([(btn_x, btn_y), (btn_x+btn_w, btn_y+btn_h)], radius=4,
                       fill=hex_to_rgb(COLORS["btn_capture"]))
draw.text((btn_x+14, btn_y+4), "点击捕获按键", fill="white", font=font_small)

# 当前键标签
draw.text((24, fy1+52), "当前键:", fill=hex_to_rgb(COLORS["fg_text"]), font=font_small)
draw.rectangle([(80, fy1+50), (160, fy1+70)], fill="white", outline=hex_to_rgb(COLORS["border"]))
draw.text((86, fy1+52), "（未选择）", fill=hex_to_rgb(COLORS["fg_muted"]), font=font_small)

# ── "时间间隔" 区域 ──
fy2 = 116
draw.rectangle([(12, fy2), (W-12, fy2+56)], outline=hex_to_rgb(COLORS["border"]), fill=hex_to_rgb("#F0F6FB"))
draw.text((20, fy2+4), " 时间间隔 ", fill=hex_to_rgb(COLORS["fg_text"]), font=font_small)

# 输入框
draw.rectangle([(20, fy2+28), (100, fy2+50)], fill="white", outline=hex_to_rgb(COLORS["border"]))
draw.text((30, fy2+32), "100", fill=hex_to_rgb(COLORS["fg_text"]), font=font_small)
draw.text((108, fy2+32), "毫秒 (ms)   最小 10ms", fill=hex_to_rgb(COLORS["fg_muted"]), font=font_small)

# ── 控制按钮 ──
fy3 = 180
# 开始按钮
draw.rounded_rectangle([(20, fy3), (90, fy3+34)], radius=5, fill=hex_to_rgb(COLORS["btn_start"]))
draw.text((37, fy3+7), "开始", fill="white", font=font_small)

# 停止按钮（灰色不可用状态）
draw.rounded_rectangle([(100, fy3), (170, fy3+34)], radius=5, fill="#B0B0B0")
draw.text((117, fy3+7), "停止", fill="white", font=font_small)

# 窗口置顶
draw.rectangle([(260, fy3+4), (274, fy3+18)], fill="white", outline=hex_to_rgb(COLORS["border"]))
draw.text((280, fy3+4), "窗口置顶", fill=hex_to_rgb(COLORS["fg_text"]), font=font_small)

# ── 状态栏 ──
draw.text((20, 226), "状态: 空闲", fill=hex_to_rgb(COLORS["fg_muted"]), font=font_small)

# 管理员提示
draw.text((20, 244), "提示：如果捕获按键无效，请右键以管理员身份运行",
          fill="#E74C3C", font=font_small)

img.save(output_path)
print(f"GUI 效果图已生成: {output_path}")
print(f"尺寸: {W}x{H}")
