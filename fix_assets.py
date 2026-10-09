import os
import re

def fix_native():
    print("=== 开始安全处理 Android 原生层资源（严格保留控件 ID，杜绝闪退） ===")
    
    # 1. 修复自适应桌面图标
    anydpi_dir = "app/src/main/res/mipmap-anydpi-v26"
    os.makedirs(anydpi_dir, exist_ok=True)
    adaptive_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@android:color/white" />
    <foreground android:drawable="@drawable/icon" />
</adaptive-icon>
"""
    with open(os.path.join(anydpi_dir, "ic_launcher.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_xml)
    with open(os.path.join(anydpi_dir, "ic_launcher_round.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_xml)

    # 2. 将所有 splash / logo 矢量资源重定向为我们的位图 boot_logo
    drawable_dir = "app/src/main/res/drawable"
    os.makedirs(drawable_dir, exist_ok=True)
    
    bitmap_xml = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/black" />
    <item>
        <bitmap
            android:gravity="center"
            android:src="@drawable/boot_logo" />
    </item>
</layer-list>
"""
    # 覆盖原版引用的所有开屏矢量定义
    for name in ["splash.xml", "splash_screen.xml", "logo.xml"]:
        with open(os.path.join(drawable_dir, name), "w", encoding="utf-8") as f:
            f.write(bitmap_xml)

    # 3. 安全更新 activity_boot.xml（只替换 ImageView 的图片源，绝不删除任何 ProgressBar / TextView 等组件）
    boot_xml_path = "app/src/main/res/layout/activity_boot.xml"
    if os.path.exists(boot_xml_path):
        with open(boot_xml_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 将引用的 @drawable/logo 或旧图片强制换成 @drawable/boot_logo
        content = re.sub(r'android:src="@drawable/[^"]+"', 'android:src="@drawable/boot_logo"', content)
        with open(boot_xml_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("已安全更新 activity_boot.xml 图片引用，保留全部原有控件 ID！")

def fix_web():
    print("=== 开始处理 Web 前端层资产 ===")
    web_dir = "web_assets"
    if not os.path.exists(web_dir):
        return

    patterns = [
        r'd="M37\.052[^"]*"',
        r'd="M306\.909[^"]*"',
        r'd="M512[^"]*"',
        r'd="M717\.091[^"]*"',
        r'<path fill="#d23f31"[^>]*></path>',
        r'<path fill="#3b3e43"[^>]*></path>',
        r'<g class="streaks">.*?</g>',
        r'<g class="logo">.*?</g>'
    ]

    replacement_img = '<img src="logo.png" style="width:130px;height:130px;object-fit:contain;margin:auto;display:block;border-radius:20px;" />'

    for root, dirs, files in os.walk(web_dir):
        for file in files:
            if file.endswith((".html", ".htm", ".js")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                    orig = c
                    for p in patterns:
                        c = re.sub(p, "", c, flags=re.DOTALL)
                    if file == "index.html":
                        c = re.sub(r'<div id="bg">.*?</div>', f'<div id="bg">{replacement_img}</div>', c, flags=re.DOTALL)
                        c = re.sub(r'<svg[^>]*>.*?</svg>', replacement_img, c, flags=re.DOTALL)
                    if c != orig:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(c)
                except Exception:
                    pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        fix_web()
    else:
        fix_native()
