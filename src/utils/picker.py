import os
import random
import xml.etree.ElementTree as ET

class HandwritingPicker:
    def __init__(self, asset_dir="asset"):
        self.asset_dir = asset_dir

    def pick_svg_for_char(self, char):
        folder = os.path.join(self.asset_dir, char)
        if not os.path.isdir(folder):
            return None
        svg_files = [f for f in os.listdir(folder) if f.endswith(".svg")]
        if not svg_files:
            return None
        svg_file = random.choice(svg_files)
        return os.path.join(folder, svg_file)

    def is_chinese(self, char):
        return '\u4e00' <= char <= '\u9fff'

    def get_fallback_char(self, char):
        if self.is_chinese(char):
            return "　"  # 全形空白
        else:
            return " "  # 半形空白

    def parse_svg_path(self, svg_path):
        # Minimal SVG path extraction (for demo)
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag.endswith('path'):
                    return elem.attrib.get('d', '')
        except Exception:
            return None
        return None
