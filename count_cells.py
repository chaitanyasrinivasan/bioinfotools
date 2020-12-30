import cv2
import scipy.ndimage
import numpy as np
import glob


'''
Chaitanya Srinivasan

automated cell counter

'''

def count(file):
	im = cv2.imread(file).astype('uint8')
	cv2.imwrite(file[:-4]+"_8bit.png", im)
	image = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
	image = scipy.ndimage.gaussian_filter(image,0.5)
	thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 333, 2)
	kernel = np.ones((5,5), np.uint8)
	img_dilation = cv2.dilate(thresh, kernel, iterations=2)
	img_erode = cv2.erode(img_dilation,kernel, iterations=1)
	cv2.imwrite(file[:-3]+"seg.png", img_erode)
	ret, labels = cv2.connectedComponents(img_erode)
	print("There are " + str(ret) + " cells, "+file)


def main():
	for file in glob.glob("*.PNG"):
		count(file)

if __name__ == "__main__":
	main()