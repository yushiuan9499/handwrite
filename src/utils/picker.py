import os
import random
import xml.etree.ElementTree as ET

class HandwritingPicker:
    def __init__(self, asset_dir="data/font"):
        self.asset_dir = asset_dir

    def pick_svg_for_char(self, char) -> str|None:
        folder = os.path.join(self.asset_dir, char)
        if not os.path.isdir(folder):
            return None
        svg_files = [f for f in os.listdir(folder) if f.endswith(".svg")]
        if not svg_files:
            return None
        svg_file = random.choice(svg_files)
        return os.path.join(folder, svg_file)

    def is_chinese(self, char) -> bool:
        return '\u4e00' <= char <= '\u9fff'

    def get_fallback_char(self, char) -> str:
        if self.is_chinese(char):
            return "　"  # 全形空白
        else:
            return " "  # 半形空白

    def get_all_svgs_for_char(self, char):
        folder = os.path.join(self.asset_dir, char)
        if not os.path.isdir(folder):
            return []
        svg_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".svg")]
        return svg_files
