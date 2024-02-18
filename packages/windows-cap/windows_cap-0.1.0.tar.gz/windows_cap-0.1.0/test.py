import cv2
import numpy as np
from windows_cap import WindowCapture
from time import time

wincap = WindowCapture("雀魂麻將", "UnityWndClass")

wincap.start_capture()

start = time()
cnt = 0

while True:
    cnt += 1
    if time() - start > 1:
        print(f'FPS: {cnt}')
        start = time()
        cnt = 0
    data = wincap.next()
    w, h = wincap.client_size
    img = np.frombuffer(data, dtype=np.uint8)
    img = np.reshape(img, (h, w, 4))
    img = cv2.resize(img, (w // 4, h // 4))
    cv2.imshow("Computer Vision", img)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break