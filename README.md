## Usage

### Installation

1. Ensure you have a webcam connected.
2. Install the required dependencies:
```bash
pip install -r required/requirements.txt

```


3. Run the application:
```bash
python main.py

```



### Calibration

When you launch Hawkeye for the first time, it will enter **Calibration Mode**. You will see a video feed with the following controls:

1. **Set Top-Left:** Look at the top-left corner of your screen and press **A**.
2. **Set Bottom-Right:** Look at the bottom-right corner of your screen and press **S**.
3. **Toggle Settings (Optional):**
* Press **E** to toggle Sleep Detection (alert if eyes close for too long).
* Press **W** to toggle the Debug Window (visualize your gaze while tracking).


4. **Save & Start:** Press **D** to save your calibration and begin tracking.

*Note: Your calibration settings are automatically saved to `hawkeye_config.json`. The application will load these settings on next launch.*

### Global Hotkeys

The application runs in the background. You can control it from anywhere using these shortcuts:

* **Ctrl + Shift + H**: Pause or Resume tracking.
* **Ctrl + Shift + R**: Open the Recalibration and Settings window.

### Building from Source

To compile the application into a standalone executable (`.exe`):

1. Ensure you have the `required` folder containing `face_landmarker.task` and `requirements.txt`.
2. Run the build script:
* **Windows:** Double-click `build_hawkeye.bat`.


3. The output executable will be located in the `dist` folder.