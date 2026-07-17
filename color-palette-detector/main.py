import sys
import cv2
import numpy as np
from sklearn.cluster import KMeans
import webcolors
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QSizePolicy, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap, QImage

css3_names = webcolors.names("css3")

def closest_color(requested_color):
    min_dist = float('inf')
    closest_name = None
    for name in css3_names:
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        dist = (r_c - requested_color[0])**2 + (g_c - requested_color[1])**2 + (b_c - requested_color[2])**2
        if dist < min_dist: 
            min_dist = dist
            closest_name = name
    return closest_name


def get_color_name(rgb):
    try:
        return webcolors.rgb_to_name(tuple(rgb), spec="css3")
    except ValueError:
        return closest_color(rgb)


class ColorPalleteApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dominant Color Palette")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("background-color: #080810;")

        central = QWidget()
        self.setCentralWidget(central)

        self.layout = QVBoxLayout(central)
        self.layout.setContentsMargins(28, 28, 28, 28)
        self.layout.setSpacing(16)

        #   HEADER
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: rgba(120, 80, 255, 0.10);
                border: 1px solid rgba(120, 80, 255, 0.22);
                border-radius: 14px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)

        title = QLabel(" Dominant Color Palette")
        title.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        title.setStyleSheet("color: #c4b5fd; background: transparent; border: none;")

        tagline = QLabel("Discover the colors around you")
        tagline.setFont(QFont("SF Pro Text", 10))
        tagline.setStyleSheet("color: rgba(160, 140, 255, 0.40); background: transparent; border: none;")
        tagline.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header_layout.addWidget(title)
        header_layout.addWidget(tagline)
        self.layout.addWidget(header)

        #   SLIDER
        slider_row = QHBoxLayout()

        slider_label = QLabel("dominant colors")
        slider_label.setFont(QFont("SF Pro Text", 10))
        slider_label.setStyleSheet("color: rgba(167, 139, 250, 0.45);")

        self.k_slider = QSlider(Qt.Horizontal)
        self.k_slider.setMinimum(3)
        self.k_slider.setMaximum(8)
        self.k_slider.setValue(5)
        self.k_slider.setTickInterval(1)
        self.k_slider.setTickPosition(QSlider.TicksBelow)
        self.k_slider.setFixedWidth(200)
        self.k_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background: rgba(120, 80, 255, 0.12);
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #7c3aed;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #a78bfa;
                border: 2px solid #7c3aed;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
        """)

        self.k_value_label = QLabel("5")
        self.k_value_label.setFont(QFont("SF Pro Display", 13, QFont.Bold))
        self.k_value_label.setStyleSheet("color: #ddd6fe;")
        self.k_value_label.setFixedWidth(20)

        self.k_slider.valueChanged.connect(self.on_slider_change)

        slider_row.addStretch()
        slider_row.addWidget(slider_label)
        slider_row.addSpacing(12)
        slider_row.addWidget(self.k_slider)
        slider_row.addSpacing(10)
        slider_row.addWidget(self.k_value_label)
        slider_row.addStretch()
        self.layout.addLayout(slider_row)

        #BUTTONS
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.webcam_btn = QPushButton("WEBCAM")
        self.upload_btn = QPushButton("upload picture")
        self.stop_btn = QPushButton("✕  Stop")

        btn_style = """
            QPushButton {
                background-color: rgba(120, 80, 255, 0.12);
                color: #a78bfa;
                border: 1px solid rgba(120, 80, 255, 0.25);
                border-radius: 10px;
                padding: 13px 28px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: rgba(120, 80, 255, 0.28);
                color: #ddd6fe;
                border: 1px solid rgba(180, 140, 255, 0.50);
            }
            QPushButton:pressed {
                background-color: rgba(120, 80, 255, 0.42);
                color: #ede9fe;
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.02);
                color: #2e2e4e;
                border: 1px solid rgba(255, 255, 255, 0.04);
            }
        """

        self.webcam_btn.setStyleSheet(btn_style)
        self.upload_btn.setStyleSheet(btn_style)
        self.stop_btn.setStyleSheet(btn_style)

        self.webcam_btn.clicked.connect(self.start_webcam)
        self.upload_btn.clicked.connect(self.upload_file)
        self.stop_btn.clicked.connect(self.stop_and_restart)
        self.stop_btn.setEnabled(False)

        btn_row.addWidget(self.webcam_btn)
        btn_row.addWidget(self.upload_btn)
        btn_row.addWidget(self.stop_btn)
        self.layout.addLayout(btn_row)

        #   VIDEO AREA
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(860, 420)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: rgba(120, 80, 255, 0.05);
                border: 1px solid rgba(120, 80, 255, 0.10);
                border-radius: 14px;
                color: rgba(130, 100, 255, 0.35);
                font-size: 13px;
            }
        """)
        self.video_label.setFont(QFont("SF Pro Text", 13))
        self.video_label.setText("*  drop an image or open your camera  *")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.video_label, stretch=7)

        #   PALETTE BAR
        self.palette_label = QLabel()
        self.palette_label.setMinimumHeight(64)
        self.palette_label.setStyleSheet("""
            QLabel {
                background-color: rgba(120, 80, 255, 0.05);
                border: 1px solid rgba(120, 80, 255, 0.10);
                border-radius: 14px;
                color: rgba(130, 100, 255, 0.30);
                font-size: 11px;
            }
        """)
        self.palette_label.setText("*  your color story will appear here  *")
        self.palette_label.setAlignment(Qt.AlignCenter)
        self.palette_label.setFont(QFont("SF Pro Text", 10))
        self.layout.addWidget(self.palette_label, stretch=1)

        self.color_info = []

        self.cap = None
        self.frame_count = 0
        self.k = 5
        self.process_every_n = 15

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def on_slider_change(self, value):
        self.k = value
        self.k_value_label.setText(str(value))

    def start_webcam(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.video_label.setText("could not open webcam")
            return
        self.frame_count = 0
        self.timer.start(30)
        self.stop_btn.setEnabled(True)
        self.webcam_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        frame = cv2.imread(file_path)
        if frame is None:
            self.video_label.setText("Could not load image.")
            return
        self.run_kmeans(frame)
        self.display_frame(frame)
        self.stop_btn.setEnabled(True)
        self.webcam_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)

    def update_frame(self):
        if self.cap is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            return
        self.frame_count += 1
        if self.frame_count % self.process_every_n == 0:
            self.run_kmeans(frame)
        self.display_frame(frame)

    def update_palette(self):
        if not self.color_info:
            return
        total_width = self.palette_label.width()
        height = self.palette_label.height()
        canvas = QPixmap(total_width, height)
        canvas.fill(Qt.transparent)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        x = 0
        for i, (r, g, b, pct, name) in enumerate(self.color_info):
            w = int(pct * total_width) if i < len(self.color_info) - 1 else total_width - x
            if w <= 0:
                continue
            painter.fillRect(x, 0, w, height, QColor(r, g, b))
            brightness = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = QColor(0, 0, 0, 200) if brightness > 140 else QColor(255, 255, 255, 220)
            painter.setPen(text_color)
            painter.setFont(QFont("SF Pro Text", 8, QFont.Bold))
            label = f"{name}\n#{r:02x}{g:02x}{b:02x}\n{pct * 100:.1f}%"
            painter.drawText(x + 6, 0, w - 6, height, Qt.AlignVCenter | Qt.AlignLeft, label)
            x += w
        painter.end()
        self.palette_label.setPixmap(canvas)

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        event.accept()

    def run_kmeans(self, frame):
        small = cv2.resize(frame, (150, 150))
        pixels = small.reshape((-1, 3))
        kmeans = KMeans(n_clusters=self.k, n_init=3, random_state=42)
        kmeans.fit(pixels)
        colors_bgr = kmeans.cluster_centers_.astype(int)
        counts = np.bincount(kmeans.labels_)
        percentages = counts / counts.sum()
        sorted_idx = np.argsort(percentages)[::-1]
        colors_bgr = colors_bgr[sorted_idx]
        percentages = percentages[sorted_idx]
        self.color_info = []
        for bgr, pct in zip(colors_bgr, percentages):
            r, g, b = int(bgr[2]), int(bgr[1]), int(bgr[0])
            name = get_color_name((r, g, b))
            self.color_info.append((r, g, b, pct, name))
        self.update_palette()

    def display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(
            pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def stop_and_restart(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.frame_count = 0
        self.color_info = []
        self.video_label.clear()
        self.video_label.setText("*  drop an image or open your camera  *")
        self.palette_label.clear()
        self.palette_label.setText("*  your color story will appear here  *")
        self.stop_btn.setEnabled(False)
        self.webcam_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorPalleteApp()
    window.show()
    sys.exit(app.exec_())