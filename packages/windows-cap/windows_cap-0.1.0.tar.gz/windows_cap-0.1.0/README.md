# Windows Capture

Utilize the Windows Graphics Capture API to capture the client area of a window.

Requires Windows 10 and Python 3.8 or later.

## Usage

```python
import cv2
import numpy as np
from windows_cap import WindowCapture

# Create a WindowCapture object with the window title and class name (optional)
wincap = WindowCapture("Untitled - Notepad", "CLASSNAME")

while True:
    data = wincap.next()
    w, h = wincap.client_size
    img = np.frombuffer(data, dtype=np.uint8)
    img = np.reshape(img, (h, w, 4))
    img = cv2.resize(img, (w // 4, h // 4))
    cv2.imshow("WGC", img)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break
```