import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Canvas
from picker import HandwritingPicker
import os

class HandwritingGUI(tk.Tk):
    MAX_WIDTH = 1000
    MAX_HEIGHT = 600
    def __init__(self):
        super().__init__()
        self.title("Handwriting Simulator")
        self.geometry(f"{HandwritingGUI.MAX_WIDTH}x{HandwritingGUI.MAX_HEIGHT}")

        self.svg_canvas = Canvas(self, width=HandwritingGUI.MAX_WIDTH//2, height=HandwritingGUI.MAX_HEIGHT)
        self.svg_canvas.grid(row=0, column=2, rowspan=3, padx=10, pady=10)
        self.picker = HandwritingPicker(asset_dir="asset")

        # Input text
        self.label_text = ttk.Label(self, text="輸入文字：")
        self.label_text.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_input = tk.Text(self, height=5, width=40)
        self.text_input.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Column setting
        self.label_col = ttk.Label(self, text="每行字數 (columns)：")
        self.label_col.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.col_var = tk.IntVar(value=10)
        self.spin_col = ttk.Spinbox(self, from_=1, to=100, textvariable=self.col_var, width=5)
        self.spin_col.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Row setting
        self.label_row = ttk.Label(self, text="行數 (rows)：")
        self.label_row.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.row_var = tk.IntVar(value=10)
        self.spin_row = ttk.Spinbox(self, from_=1, to=100, textvariable=self.row_var, width=5)
        self.spin_row.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Preview button (placeholder)
        self.preview_btn = ttk.Button(self, text="預覽", command=self.preview)
        self.preview_btn.grid(row=3, column=1, padx=10, pady=20, sticky="w")

    def preview(self):
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("提示", "請先輸入文字")
            return
        col = self.col_var.get()
        row = self.row_var.get()
        self.chars = list(text)[:col * row]
        self.char_svgs = [self.picker.pick_svg_for_char(c) for c in self.chars]
        self.selected_char_idx = None
        self.render_chars_grid()

    def render_chars_grid(self):
        self.svg_canvas.delete("all")
        col = self.col_var.get()
        cell_w, cell_h = 80, 80
        for idx, char in enumerate(self.chars):
            x = (idx % col) * cell_w + 50
            y = (idx // col) * cell_h + 50
            svg_path = self.char_svgs[idx]
            if svg_path:
                self.display_svg_on_canvas(svg_path, x, y)
            else:
                fallback_char = self.picker.get_fallback_char(char)
                self.svg_canvas.create_rectangle(x-35, y-35, x+35, y+35, outline="gray")
                self.svg_canvas.create_text(x, y, text=fallback_char, font=("Arial", 40))
        self.svg_canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        col = self.col_var.get()
        cell_w, cell_h = 80, 80
        x, y = event.x, event.y
        grid_x = (x - 50) // cell_w
        grid_y = (y - 50) // cell_h
        idx = grid_y * col + grid_x
        if 0 <= idx < len(self.chars):
            self.selected_char_idx = idx
            self.show_variant_selector(idx)

    def show_variant_selector(self, idx):
        char = self.chars[idx]
        folder = os.path.join(self.picker.asset_dir, char)
        if not os.path.isdir(folder):
            messagebox.showinfo("無字形", "此字沒有可選字形")
            return
        svg_files = [f for f in os.listdir(folder) if f.endswith(".svg")]
        if not svg_files:
            messagebox.showinfo("無字形", "此字沒有可選字形")
            return
        top = tk.Toplevel(self)
        top.title(f"選擇「{char}」的字形")
        for i, svg_file in enumerate(svg_files):
            btn = ttk.Button(top, text=svg_file, command=lambda f=svg_file: self.set_char_svg(idx, os.path.join(folder, f), top))
            btn.grid(row=0, column=i, padx=5, pady=5)

    def set_char_svg(self, idx, svg_path, window):
        self.char_svgs[idx] = svg_path
        window.destroy()
        self.render_chars_grid()

    def display_svg_on_canvas(self, svg_path, x, y):
        # Minimal SVG path rendering (only supports simple path for demo)
        d = self.picker.parse_svg_path(svg_path)
        # For demo: just draw a rectangle to represent the SVG
        self.svg_canvas.create_rectangle(x-35, y-35, x+35, y+35, outline="black")
        self.svg_canvas.create_text(x, y, text="SVG", font=("Arial", 20))

if __name__ == "__main__":
    app = HandwritingGUI()
    app.mainloop()
