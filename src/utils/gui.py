import sys
import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QSpinBox, QDoubleSpinBox, QPushButton, QScrollArea, QSlider,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QGraphicsView, QGraphicsScene, QDialog,
)
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtCore import Qt, pyqtSignal 
from PyQt5 import QtGui, QtCore
from utils.picker import HandwritingPicker  # Assuming picker.py is in the same directory
from utils.compress import compress_svg  # Assuming compress.py is in the same directory
class ClickableSvgItem(QGraphicsSvgItem):
    clicked = pyqtSignal(str, int)

    def __init__(self, svg_path, char, index):
        super().__init__(svg_path)
        self.char = char
        self.index = index
        self.custom_renderer = None
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)

    def mousePressEvent(self, event:PyQt5.QtWidgets.QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.char, self.index)
        super().mousePressEvent(event)

class HandwritingGUI(QWidget):
    MAIN_LAYOUT_RATIO = (1, 2)  # (settings_layout, svg_view)
    SVG_VIEW_SIZE = (800, 1600)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Handwriting Simulator (PyQt)")
        self.picker = HandwritingPicker()
        self.background_item = None
        self.background_path = None
        self.char_items = []  # 新增：記錄每個字的 QGraphicsItem
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
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(21.33)  # Default size
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

        # Compress SVG button
        self.compress_svg_btn = QPushButton("壓縮 SVG")
        self.compress_svg_btn.clicked.connect(lambda: compress_svg())
        settings_layout.addWidget(self.compress_svg_btn)
        settings_layout.addStretch(1)

        # Right: SVG display
        self.svg_view = QGraphicsView()
        self.svg_scene = QGraphicsScene()
        self.svg_view.setScene(self.svg_scene)
        self.svg_view.setFixedSize(*self.SVG_VIEW_SIZE)
        self.svg_view.setResizeAnchor(QGraphicsView.NoAnchor)
        self.svg_view.setTransformationAnchor(QGraphicsView.NoAnchor)
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

        cell_size = self.size_spin.value()
        column_limit = self.column_spin.value()
        self.svg_scene.clear()
        self.char_items = []
        self.background_item = None

        # 重新加回背景（如果有）
        if self.background_path:
            self.set_background(self.background_path)

        margin = 0
        max_row = 30
        max_column = 30

        current_column = 0
        row = 0
        col = -1
        col_shift = 0

        # 從左上角橫式填寫
        for char in text:
            if char == '\n':
                row += 1
                col = -1
                continue

            col += 1
            # 計算這個column可以放多少字
            max_word = max_column // column_limit + (current_column < max_column % column_limit)
            if col >= max_word:
                col = 0
                row += 1
            if row >= max_row:
                col_shift += max_word
                current_column += 1
                row = 0
            if current_column >= column_limit:
                QMessageBox.warning(self, "警告", "字數過多，請調整字數")
                break

            x = col_shift + margin + col * cell_size
            y = margin + row * cell_size

            svg_path = self.picker.pick_svg_for_char(char)
            if svg_path:
                svg_item = ClickableSvgItem(svg_path, char, len(self.char_items))
                import random
                from PyQt5.QtGui import QTransform

                # 隨機縮放 (0.95~1.05)
                scale_factor = cell_size / 21.33 * random.uniform(0.95, 1.05)

                # 根據xy座標進行非等比縮放
                # 例如: x方向 0.95~1.05, y方向 0.95~1.05
                sx = scale_factor * (1 + 0.03 * ((x % 5) - 2))  # -0.06~+0.06
                sy = scale_factor * (1 + 0.03 * ((y % 5) - 2))

                # 隨機平移 (-2~2 px)
                offset_x = (cell_size - svg_item.boundingRect().width() * sx) / 2 + random.uniform(-2, 2)
                offset_y = (cell_size - svg_item.boundingRect().height() * sy) / 2 + random.uniform(-2, 2)

                # 建立仿射變換矩陣
                transform = QTransform()
                transform.scale(sx, sy)
                svg_item.setTransform(transform)

                svg_item.setPos(x + offset_x, y + offset_y)
                svg_item.clicked.connect(self.open_font_picker_dialog)
                self.svg_scene.addItem(svg_item)
                self.char_items.append(svg_item)
        # 設定 scene rect，確保左上角為 (0,0)
        if self.background_item:
            rect = self.background_item.boundingRect()
            self.svg_scene.setSceneRect(rect)
        else:
            self.svg_scene.setSceneRect(0, 0, self.SVG_VIEW_SIZE[0], self.SVG_VIEW_SIZE[1])
    def open_font_picker_dialog(self, char, index):
        dialog = FontPickerDialog(self.picker, char, parent=self)
        if dialog.exec_():
            selected_svg = dialog.get_selected_svg()
            if selected_svg:
                # 更新該字的字體
                item = self.char_items[index]
                if isinstance(item, ClickableSvgItem):
                    # 建立新的 QSvgRenderer 並保存，避免被垃圾回收
                    from PyQt5.QtSvg import QSvgRenderer
                    if hasattr(item, 'custom_renderer') and item.custom_renderer:
                        del item.custom_renderer
                    item.custom_renderer = QSvgRenderer(selected_svg)
                    item.setSharedRenderer(item.custom_renderer)
    def export_to_pdf(self):
        """將 SVG scene 匯出成 PDF 檔案"""
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存 PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return
        from PyQt5.QtPrintSupport import QPrinter
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        # 根據背景大小設定紙張大小
        if self.background_item:
            rect = self.background_item.boundingRect()
            printer.setPaperSize(QtCore.QSizeF(rect.width(), rect.height()), QPrinter.Point)
            printer.setFullPage(True)
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

class FontPickerDialog(QDialog):
    def __init__(self, picker, char, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"選擇字體 - {char}")
        self.picker = picker
        self.char = char
        self.selected_svg = None
        self.current_page = 0
        self.font_svgs = self.picker.get_all_svgs_for_char(char)
        self.font_count = len(self.font_svgs)
        self.fonts_per_page = 10

        main_layout = QVBoxLayout(self)
        self.preview_layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.preview_widget = QWidget()
        self.preview_widget.setLayout(self.preview_layout)
        self.scroll.setWidget(self.preview_widget)
        main_layout.addWidget(self.scroll)

        self.page_slider = QSlider(Qt.Orientation.Vertical)
        self.page_slider.setMinimum(0)
        self.page_slider.setMaximum(max(0, (self.font_count - 1) // self.fonts_per_page))
        self.page_slider.valueChanged.connect(self.update_preview)
        main_layout.addWidget(self.page_slider)

        button_box = QHBoxLayout()
        self.ok_btn = QPushButton("確定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(self.ok_btn)
        button_box.addWidget(self.cancel_btn)
        main_layout.addLayout(button_box)

        self.selected_index = None
        self.update_preview()

    def update_preview(self):
        # 清除舊的預覽
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        start = self.page_slider.value() * self.fonts_per_page
        end = min(start + self.fonts_per_page, self.font_count)
        for idx in range(start, end):
            svg_path = self.font_svgs[idx]
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setMinimumHeight(60)
            # 顯示 SVG 預覽
            icon = QtGui.QIcon(svg_path)
            btn.setIcon(icon)
            btn.setIconSize(QtCore.QSize(48, 48))
            btn.clicked.connect(lambda checked, i=idx: self.select_font(i))
            self.preview_layout.addWidget(btn)
            if self.selected_index == idx:
                btn.setChecked(True)

    def select_font(self, idx):
        self.selected_index = idx
        self.selected_svg = self.font_svgs[idx]
        self.update_preview()

    def get_selected_svg(self):
        return self.selected_svg
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HandwritingGUI()
    gui.show()
    sys.exit(app.exec_())
