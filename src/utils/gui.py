import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QGraphicsView, QGraphicsScene
)
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt
from utils.picker import HandwritingPicker  # Assuming picker.py is in the same directory
from PyQt5 import QtGui

class HandwritingGUI(QWidget):
    MAIN_LAYOUT_RATIO = (1, 2)  # (settings_layout, svg_view)
    SVG_VIEW_SIZE = (800, 1600)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Handwriting Simulator (PyQt)")
        self.picker = HandwritingPicker()
        self.background_item = None
        self.background_path = None
        self.init_ui()

    def init_ui(self) -> None:
        """初始化 UI"""
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
        size_row_layout = QHBoxLayout()
        size_row_layout.addWidget(QLabel("字體大小(font size)："))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(10)
        size_row_layout.addWidget(self.size_spin)
        size_row_layout.addWidget(QLabel("列數 (column)："))
        self.column_spin = QSpinBox()
        self.column_spin.setRange(1, 4)
        self.column_spin.setValue(1)
        size_row_layout.addWidget(self.column_spin)
        settings_layout.addLayout(size_row_layout)

        # Set Background button
        self.set_bg_btn = QPushButton("設定背景")
        self.set_bg_btn.clicked.connect(self.set_background_dialog)
        settings_layout.addWidget(self.set_bg_btn)

        # Preview button
        self.preview_btn = QPushButton("預覽")
        self.preview_btn.clicked.connect(self.preview)
        settings_layout.addWidget(self.preview_btn)

        # Export to PDF button
        self.export_pdf_btn = QPushButton("匯出為 PDF")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        settings_layout.addWidget(self.export_pdf_btn)
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

    def preview(self) -> None:
        """預覽按鈕的點擊事件"""
        text = self.text_input.toPlainText()
        if not text:
            QMessageBox.information(self, "提示", "請先輸入文字")
            return
        # 假設字是正方形的
        cell_size = self.size_spin.value()
        column = self.column_spin.value()
        self.svg_scene.clear()
        # 重新加回背景（如果有）
        if self.background_path:
            self.background_item = None
            self.set_background(self.background_path)

        margin = 0
        max_row = 30
        max_column = 30

        # 計算位置用變數
        now_column = 0
        row = 0
        col = 0
        col_shift = 0


        # 從左上角橫式填寫
        for char in text:
            # 換行
            if char == '\n':
                row += 1
                col = 0
                continue
            col += 1
            # 計算這個column可以放多少字
            max_word = max_column//column + (now_column < max_column%column)
            if col >= max_word:
                # 換行
                col = 0
                row += 1
            if row >= max_row:
                col_shift += max_word
                now_column += 1
                row = 0
            if now_column >= column:
                # 顯示警告，詢問是否拋棄後面的內容
                QMessageBox.warning(self, "警告", "字數過多，請調整字數")
                break
            # 計算位置
            x = col_shift + margin + col * cell_size 
            y = margin + row * cell_size 
            # 嘗試從 SVG 中取得對應的字形
            svg_path = self.picker.pick_svg_for_char(char)
            if svg_path:
                # 如果有對應的 SVG，則顯示它
                svg_item = QGraphicsSvgItem(svg_path)
                svg_item.setScale(cell_size / 15)
                svg_item.setPos(x, y)
                self.svg_scene.addItem(svg_item)
            else:
                # 如果沒有對應的 SVG，則顯示 fallback 字形
                fallback_char = self.picker.get_fallback_char(char)
                text_item = self.svg_scene.addText(fallback_char)
                text_item.setPos(x + cell_size // 4, y + cell_size // 4)
        # 設定 sceneRect 讓內容靠左上
    def export_to_pdf(self):
        """將 SVG scene 匯出成 PDF 檔案"""
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存 PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return
        from PyQt5.QtPrintSupport import QPrinter
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)
        painter = None
        try:
            painter = QtGui.QPainter(printer)
            self.svg_scene.render(painter)
        finally:
            if painter:
                painter.end()
    def set_background_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇背景圖片", "", "SVG Files (*.svg)")
        if file_path:
            self.set_background(file_path)

    def set_background(self, svg_path):
        # 移除舊的背景
        if self.background_item and self.background_item.scene() is not None:
            self.svg_scene.removeItem(self.background_item)
            self.background_item = None
        # 加入新的背景
        bg_item = QGraphicsSvgItem(svg_path)
        bg_item.setZValue(-100)  # 確保在最底層
        bg_item.setPos(0, 0)
        self.svg_scene.addItem(bg_item)
        self.background_item = bg_item
        self.background_path = svg_path

        # 取得背景 SVG 的大小並調整 svg_view
        rect = bg_item.boundingRect()
        self.svg_scene.setSceneRect(rect)
        self.svg_view.setFixedSize(int(rect.width()), int(rect.height()))
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HandwritingGUI()
    gui.show()
    sys.exit(app.exec_())
