import os
import re
import base64

def run():
    target_html = 'web_assets/appearance/boot/index.html'
    if not os.path.exists(target_html):
        print(f"未找到目标文件: {target_html}")
        return

    # 1. 尝试读取自定义 logo.png 并转为 Base64
    logo_data_uri = ""
    if os.path.exists('logo.png'):
        with open('logo.png', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
            logo_data_uri = f"data:image/png;base64,{b64}"

    with open(target_html, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 2. 彻底拔除绘制折纸光带的 JS 逻辑，防止原版动画执行
    content = re.sub(r'const streaksG = document\.querySelector\(.*?\);.*?\}\)\(\);', '})();', content, flags=re.DOTALL)

    # 3. 彻底清空 SVG 内部的折纸 path 和 streaks
    # 将整个 #bg 容器替换为居中的自定义 Logo
    if logo_data_uri:
        replacement_div = f'<div id="bg"><img src="{logo_data_uri}" style="width:140px;height:140px;object-fit:contain;margin:auto;" /></div>'
    else:
        replacement_div = '<div id="bg"></div>'

    content = re.sub(r'<div id="bg">.*?</div>', replacement_div, content, flags=re.DOTALL)

    # 4. 强行隐藏任何可能残留的折纸 SVG 样式
    style_inject = """
    <style>
        #bg svg, svg .logo, svg .streaks { display: none !important; opacity: 0 !important; }
        #bootAppearance { display: none !important; }
    </style>
    </head>
    """
    content = content.replace('</head>', style_inject)

    with open(target_html, 'w', encoding='utf-8') as f:
        f.write(content)

    print("已成功剔除折纸 SVG 并替换为新 Logo！")

if __name__ == '__main__':
    run()
