import glob
import os
import sys
import numpy as np
import cv2
import skimage.feature
from sklearn import svm
from sklearn.metrics import accuracy_score


# Chaitanya Srinivasan


def feature_extract(image):
	glcm_image = skimage.feature.greycomatrix(image, [10], [np.pi/2, 3*np.pi/4, np.pi], levels=256)
	features = np.empty(18, dtype=float)
	for i in range(3):
		# vertical, horizontal, diagonal directions
		features[0+(6*i)] = skimage.feature.greycoprops(glcm_image, 'ASM')[0][i]
		features[1+(6*i)] = skimage.feature.greycoprops(glcm_image, 'contrast')[0][i]
		features[2+(6*i)] = skimage.feature.greycoprops(glcm_image, 'dissimilarity')[0][i]
		features[3+(6*i)] = skimage.feature.greycoprops(glcm_image, 'homogeneity')[0][i]
		features[4+(6*i)] = skimage.feature.greycoprops(glcm_image, 'energy')[0][i]
		features[5+(6*i)] = skimage.feature.greycoprops(glcm_image, 'correlation')[0][i]
	return features

def get_data(path):
	n = 0
	for label in glob.glob(os.path.join(path, '*')):
		for file in glob.glob(os.path.join(label, '*')):
			n += 1
	X = np.zeros(shape=(n, 18))
	Y = np.zeros(shape=(n))
	count = 0
	for y, label in enumerate(glob.glob(os.path.join(path, '*'))):
		for file in glob.glob(os.path.join(label, '*')):
			Y[count] = y
			image = cv2.imread(file, 0).astype(np.int)
			features = feature_extract(image)
			for j in range(len(features)):
				X[count][j] = features[j]
			count += 1
	return X, Y

def main():
	train_path = "Hela_hw2/train/"
	val_path = "Hela_hw2/validation/"
	test_path = "Hela_hw2/test/"
	if not (os.path.exists(train_path) and os.path.exists(val_path) and os.path.exists(test_path)):
		print("Hela_hw2/ needs to be placed in this directory")
		sys.exit(1)

	print("extracting features...")
	Xtrain, Ytrain = get_data(train_path)
	Xval, Yval = get_data(val_path)
	Xtest, Ytest = get_data(test_path)

	# fit SVM
	print("fitting SVM...")
	clf = svm.NuSVC(gamma='auto')
	clf.fit(Xtrain, Ytrain)

	print("testing...")

	# train set
	train_preds = clf.predict(Xtrain)
	train_score = accuracy_score(Ytrain, train_preds)
	print("Train accuracy : " + str(train_score))

	# validation set
	val_preds = clf.predict(Xval)
	val_score = accuracy_score(Yval, val_preds)
	print("Validation accuracy : " + str(val_score))

	# test set
	test_preds = clf.predict(Xtest)
	test_score = accuracy_score(Ytest, test_preds)
	print("Test accuracy : " + str(test_score))


if __name__ == "__main__":
	main()