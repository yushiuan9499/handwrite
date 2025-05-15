import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QGraphicsView, QGraphicsScene
)
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt
from picker import HandwritingPicker  # Assuming picker.py is in the same directory

class HandwritingGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Handwriting Simulator (PyQt)")
        self.picker = HandwritingPicker(asset_dir="asset")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("輸入文字："))
        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(50)
        input_layout.addWidget(self.text_input)
        layout.addLayout(input_layout)

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
        layout.addLayout(col_row_layout)

        # Preview button
        self.preview_btn = QPushButton("預覽")
        self.preview_btn.clicked.connect(self.preview)
        layout.addWidget(self.preview_btn)

        # SVG display
        self.svg_view = QGraphicsView()
        self.svg_scene = QGraphicsScene()
        self.svg_view.setScene(self.svg_scene)
        self.svg_view.setFixedSize(220, 220)
        layout.addWidget(self.svg_view)

        self.setLayout(layout)

    def preview(self):
        char = self.text_input.toPlainText().strip()[:1]
        if not char:
            QMessageBox.information(self, "提示", "請先輸入一個字元")
            return
        svg_path = self.picker.pick_svg_for_char(char)
        self.svg_scene.clear()
        if svg_path:
            svg_item = QGraphicsSvgItem(svg_path)
            svg_item.setScale(2.0)
            self.svg_scene.addItem(svg_item)
            svg_item.setPos(10, 10)
        else:
            fallback_char = self.picker.get_fallback_char(char)
            text_item = self.svg_scene.addText(fallback_char)
            if text_item is not None:
                text_item.setPos(80, 80)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HandwritingGUI()
    gui.show()
    sys.exit(app.exec_())
