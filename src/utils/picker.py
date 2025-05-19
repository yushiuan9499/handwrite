import os
import random
import xml.etree.ElementTree as ET

class HandwritingPicker:
    def __init__(self, asset_dir="data/font"):
        self.asset_dir = asset_dir
        self.used_svgs = {} # 紀錄最近使用的 SVG 檔案

    def pick_svg_for_char(self, char) -> str | None:
        folder = os.path.join(self.asset_dir, char)
        if not os.path.isdir(folder):
            return None

        # 確保不會重複使用
        used = self.used_svgs.setdefault(char, [])
        svg_files = [
            f for f in os.listdir(folder)
            if f.endswith(".svg") and f not in used
        ]
        if not svg_files:
            return None

        svg_file = random.choice(svg_files)
        used.append(svg_file)
        if len(used) > 10:
            # 如果使用的 SVG 檔案超過 10 個，則移除最舊的
            used.pop(0)
        return os.path.join(folder, svg_file)

    def is_chinese(self, char) -> bool:
        return '\u4e00' <= char <= '\u9fff'

    def get_all_svgs_for_char(self, char):
        folder = os.path.join(self.asset_dir, char)
        if not os.path.isdir(folder):
            return []
        svg_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".svg")]
        return svg_files
