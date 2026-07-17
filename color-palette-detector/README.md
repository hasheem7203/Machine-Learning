# 🎨 Color Palette Detector using K-Means Clustering

A desktop application built with Python that extracts dominant colors from images and live webcam input using the K-Means clustering algorithm. The application provides an interactive GUI for generating color palettes and displays the percentage distribution of each detected color.

## Features

- Extract dominant colors from uploaded images
- Capture colors from live webcam input
- Adjustable number of dominant colors (K value)
- Interactive graphical user interface built with PyQt5
- Displays color names and percentage distribution
- Uses OpenCV for image processing
- Uses K-Means clustering for color extraction

## Technologies Used

- Python
- OpenCV
- NumPy
- scikit-learn
- PyQt5
- webcolors

## Project Structure

```
color-palette-detector/
│
├── main.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/color-palette-detector.git
```

2. Navigate to the project directory

```bash
cd color-palette-detector
```

3. Install the required packages

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
python main.py
```

## How It Works

1. Upload an image or capture a frame using the webcam.
2. The image is processed using OpenCV.
3. K-Means clustering groups similar colors together.
4. The dominant colors are extracted.
5. Each color is displayed along with its percentage and closest color name.

## Future Improvements

- Export generated color palettes
- Support additional color spaces (HSV/LAB)
- Save palette history
- Improve color naming accuracy
- Dark mode interface

## License

This project is for educational and learning purposes.
