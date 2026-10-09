import os
import re

def fix_native():
    print("=== 开始修正原生主题与开屏背景 ===")
    
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

    # 2. 生成标准启动图定义（直接绑定实际存在的 boot_logo）
    drawable_dir = "app/src/main/res/drawable"
    os.makedirs(drawable_dir, exist_ok=True)
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
    for name in ["splash.xml", "splash_screen.xml", "logo.xml", "boot_splash.xml"]:
        with open(os.path.join(drawable_dir, name), "w", encoding="utf-8") as f:
            f.write(splash_xml)

    # 3. 扫描 values 目录中的 styles.xml 与 themes.xml，将 windowBackground 指向 boot_logo
    values_dir = "app/src/main/res/values"
    if os.path.exists(values_dir):
        for f_name in os.listdir(values_dir):
            if f_name.endswith(".xml"):
                f_path = os.path.join(values_dir, f_name)
                try:
                    with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                    c_new = re.sub(r'@drawable/(splash|logo|custom_boot_logo)', '@drawable/boot_logo', c)
                    if c_new != c:
                        with open(f_path, "w", encoding="utf-8") as f:
                            f.write(c_new)
                        print(f"已更新原生主题文件: {f_name}")
                except Exception:
                    pass

    # 4. 安全更新 activity_boot.xml，保留所有控件与 ID，并指向 boot_logo
    boot_xml_path = "app/src/main/res/layout/activity_boot.xml"
    if os.path.exists(boot_xml_path):
        with open(boot_xml_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r'android:src="@drawable/[^"]+"', 'android:src="@drawable/boot_logo"', content)
        with open(boot_xml_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("activity_boot.xml 引用更新完成")

def fix_web():
    print("=== 开始处理 Web 框架层 ===")
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
