import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QGraphicsView, QGraphicsScene
)
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt
from picker import HandwritingPicker  # Assuming picker.py is in the same directory

class HandwritingGUI(QWidget):
    MAIN_LAYOUT_RATIO = (1, 2)  # (settings_layout, svg_view)
    SVG_VIEW_SIZE = (800, 1600)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Handwriting Simulator (PyQt)")
        self.picker = HandwritingPicker()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left: Settings
        settings_layout = QVBoxLayout()

        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("輸入文字："))
        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(100)
        input_layout.addWidget(self.text_input)
        settings_layout.addLayout(input_layout)

        # Column/Row
        col_row_layout = QHBoxLayout()
        col_row_layout.addWidget(QLabel("每行字數 (columns)："))
        self.col_spin = QSpinBox()
        self.col_spin.setRange(1, 100)
        self.col_spin.setValue(10)
        col_row_layout.addWidget(self.col_spin)
        col_row_layout.addWidget(QLabel("行數 (rows)："))
        self.row_spin = QSpinBox()
        self.row_spin.setRange(1, 100)
        self.row_spin.setValue(10)
        col_row_layout.addWidget(self.row_spin)
        settings_layout.addLayout(col_row_layout)

        # Preview button
        self.preview_btn = QPushButton("預覽")
        self.preview_btn.clicked.connect(self.preview)
        settings_layout.addWidget(self.preview_btn)
        settings_layout.addStretch(1)

        # Right: SVG display
        self.svg_view = QGraphicsView()
        self.svg_scene = QGraphicsScene()
        self.svg_view.setScene(self.svg_scene)
        self.svg_view.setFixedSize(*self.SVG_VIEW_SIZE)
        self.svg_view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Combine layouts
        main_layout.addLayout(settings_layout, self.MAIN_LAYOUT_RATIO[0])
        main_layout.addWidget(self.svg_view, self.MAIN_LAYOUT_RATIO[1])
        self.setLayout(main_layout)

    def preview(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "提示", "請先輸入文字")
            return
        columns = self.col_spin.value()
        rows = self.row_spin.value()
        self.svg_scene.clear()

        # 從左上角橫式填寫
        cell_size = 15 # 每個字的大小
        margin = 10
        max_chars = columns * rows 
        text = text[:max_chars] # 限制字數

        for idx, char in enumerate(text):
            # 計算位置
            row = idx // columns
            col = idx % columns
            x = margin + col * cell_size
            y = margin + row * cell_size 
            svg_path = self.picker.pick_svg_for_char(char)
            if svg_path:
                svg_item = QGraphicsSvgItem(svg_path)
                svg_item.setScale(cell_size / 15)
                svg_item.setPos(x, y)
                self.svg_scene.addItem(svg_item)
            else:
                fallback_char = self.picker.get_fallback_char(char)
                text_item = self.svg_scene.addText(fallback_char)
                text_item.setPos(x + cell_size // 4, y + cell_size // 4)
        # 設定 sceneRect 讓內容靠左上
        self.svg_scene.setSceneRect(0, 0, margin * 2 + columns * cell_size, margin * 2 + rows * cell_size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HandwritingGUI()
    gui.show()
    sys.exit(app.exec_())
