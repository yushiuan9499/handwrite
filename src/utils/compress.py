import os
import subprocess
import json
import time
import xml.etree.ElementTree as ET
from collections import Counter
with open('last_compress.json', 'r') as f:
    last_compress = json.load(f)
def check_svg_installed():
    """Check if svgo is installed."""
    try:
        subprocess.run(['svgo', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def compress_svg(dir: str = 'data/font'):
    """Compress SVG files in the given directory using svgo.
    @param dir: Directory to search for SVG files."""

    if not check_svg_installed():
        print("svgo is not installed. Please install it to use this function.")
        print("Run 'npm install -g svgo' to install svgo.")
        return

    # get current time
    current_time = time.time()
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith('.svg'):
                # Check if the file was modified after the last compression
                svg_file = os.path.join(root, file)
                if svg_file in last_compress:
                    last_modified_time = os.path.getmtime(svg_file)
                    if last_modified_time <= last_compress[svg_file]:
                        continue
                try:
                    subprocess.run(['svgo', svg_file, "-o", svg_file], check=True)
                    print(f"Compressed: {svg_file}")
                    last_compress[svg_file] = current_time  # Update the last compression time
                    compress_svg_style(svg_file)
                except subprocess.CalledProcessError as e:
                    print(f"Error compressing {svg_file}: {e}")

    # Save the last compression time to a file
    with open('last_compress.json', 'w') as f:
        json.dump(last_compress, f)
def compress_svg_style(file_path: str):
    """
    將SVG中重複的style屬性抽出為class，並寫入<style>區塊。
    只對出現次數多且長度較長的style進行壓縮。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        svg_text = f.read()
    tree = ET.ElementTree(ET.fromstring(svg_text))
    root = tree.getroot()

    # 統計所有path的style
    style_counter = Counter()
    paths = []
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]  # 去除namespace
        if tag == 'path' and 'style' in elem.attrib:
            style_counter[elem.attrib['style']] += 1
            paths.append(elem)

    # 決定哪些style值得壓縮
    style_to_class = {}
    class_defs = []
    class_idx = 0
    for style, count in style_counter.items():
        if len(style) * (count-1) > 40:
            class_name = f"s{class_idx}"
            style_to_class[style] = class_name
            class_defs.append(f".{class_name}{{{style}}}")
            class_idx += 1

    # 替換path的style為class
    for elem in paths:
        style = elem.attrib['style']
        if style in style_to_class:
            elem.attrib.pop('style')
            elem.set('class', style_to_class[style])

    # 插入<style>區塊（無namespace）
    if class_defs:
        style_elem = ET.Element("style")
        style_elem.text = "\n  " + "\n  ".join(class_defs) + "\n"
        # 插入到<svg>下第一個元素
        root.insert(0, style_elem)

    # 寫回檔案
    ET.indent(tree, space="  ", level=0)
    tree.write(file_path, encoding="utf-8", xml_declaration=False)

if __name__ == "__main__":
    # 壓縮SVG中的style
    compress_svg_style('3.svg')
