import os
import re

def fix_native():
    print("=== 开始处理 Android 原生层资源 ===")
    
    # 1. 修复自适应桌面图标，彻底解决 Android 小机器人问题
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

    # 2. 彻底重写原生启动图 splash.xml
    splash_xml = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/black" />
    <item>
        <bitmap
            android:gravity="center"
            android:src="@drawable/boot_logo" />
    </item>
</layer-list>
"""
    drawable_dir = "app/src/main/res/drawable"
    os.makedirs(drawable_dir, exist_ok=True)
    for name in ["splash.xml", "splash_screen.xml"]:
        with open(os.path.join(drawable_dir, name), "w", encoding="utf-8") as f:
            f.write(splash_xml)

    # 3. 彻底重写原生 activity_boot.xml
    boot_layout = """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#1e1e1e">
    <ImageView
        android:id="@+id/iv_logo"
        android:layout_width="140dp"
        android:layout_height="140dp"
        android:layout_gravity="center"
        android:src="@drawable/boot_logo"
        android:contentDescription="@null" />
</FrameLayout>
"""
    layout_dir = "app/src/main/res/layout"
    os.makedirs(layout_dir, exist_ok=True)
    with open(os.path.join(layout_dir, "activity_boot.xml"), "w", encoding="utf-8") as f:
        f.write(boot_layout)

    # 4. 清除原生工程中任何可能残留的折纸矢量路径
    res_dir = "app/src/main/res"
    for root, dirs, files in os.walk(res_dir):
        for file in files:
            if file.endswith(".xml") and ("logo" in file or "splash" in file):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                    if "<path" in c and ("M37.052" in c or "M306.909" in c):
                        c = re.sub(r'<path[^>]*/>', '', c)
                        c = re.sub(r'<path[^>]*>.*?</path>', '', c, flags=re.DOTALL)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(c)
                except Exception:
                    pass

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
