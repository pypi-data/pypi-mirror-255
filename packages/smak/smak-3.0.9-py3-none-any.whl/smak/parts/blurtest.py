import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('image1.png')
gaussian_blur = cv2.GaussianBlur(img,(5,5),0)
plt.imshow(gaussian_blur)
plt.show()