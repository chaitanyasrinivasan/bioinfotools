import glob, cv2, sys
import numpy as np
from tqdm import tqdm
import skimage
from skimage.feature import greycoprops, greycomatrix
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def load_data(files):
  return np.array([cv2.imread(file, 0) for file in tqdm(files)])

def subsample(img, iter, kernel_size=(75, 75), stride=75):
  if (kernel_size[0] % 2 != 1 or kernel_size[1] % 2 != 1):
    print("kernel size must be odd")
    sys.exit(1)
  samples = list()
  out_length = ((len(img) - kernel_size[0])//stride) + 1
  out_width = ((len(img[0]) - kernel_size[1])//stride) + 1
  if iter == 0:
    print("sample size: " + str(kernel_size[0]) + "x" + str(kernel_size[1]))
    print("number of samples: " + str(out_length) + "*" +str(out_width) + "=" + str(out_length*out_width))
  feature_matrix = list()
  for i in tqdm(range(out_length)):
    for j in range(out_width):
      # extract sample
      sample = img[stride*i:(stride*i)+kernel_size[0], stride*j:(stride*j)+kernel_size[1]]
      # calculate GLCM
      glcm_image = skimage.feature.greycomatrix(sample, [10], [np.pi/4, np.pi/2, 3*np.pi/4, np.pi], levels=256)
      features = np.zeros(6, dtype=np.float32)
      for k in range(4):
        # vertical, horizontal, diagonal directions
        features[0] += skimage.feature.greycoprops(glcm_image, 'ASM')[0][k]/4
        features[1] += skimage.feature.greycoprops(glcm_image, 'contrast')[0][k]/4
        features[2] += skimage.feature.greycoprops(glcm_image, 'dissimilarity')[0][k]/4
        features[3] += skimage.feature.greycoprops(glcm_image, 'homogeneity')[0][k]/4
        features[4] += skimage.feature.greycoprops(glcm_image, 'energy')[0][k]/4
        features[5] += skimage.feature.greycoprops(glcm_image, 'correlation')[0][k]/4
      feature_matrix.append(features)
  return np.sum(np.array(feature_matrix), axis=0)
  
def PCA_fit(samples, labels):
  pca = PCA(n_components=4)
  projected = pca.fit_transform(samples)
  fig = plt.figure()
  plt.scatter(projected[:, 1], projected[:, 3],
            c=labels, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Spectral', len(samples)))
  plt.suptitle("PCA of Haralick Texture Features")
  plt.xlabel('component 1')
  plt.ylabel('component 2')
  plt.colorbar()
  plt.show()

def tSNE_fit(samples, labels):
    tsne = TSNE(n_components=2, perplexity=10, init='random')
    projected = tsne.fit_transform(samples)
    plt.scatter(projected[:, 0], projected[:, 1],
            c=labels, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Spectral', len(samples)))
    plt.suptitle("tSNE of Haralick Texture Features")
    plt.xlabel('component 1')
    plt.ylabel('component 2')
    plt.colorbar()
    plt.show()

if __name__ == "__main__":
  load_state = False

  if load_state:
    print("loading data...")
    labels = np.load("labels.npy", allow_pickle=True)
    samples = np.load("samples.npy", allow_pickle=True)
    print("performing dimensionality reduction...")
    PCA_fit(samples, labels)


  else:
    imgs = glob.glob("TargetActivation.V4_03-31-21_04;05;40/*f05d1.PNG")
    labels = np.array([int(img.split("/")[1].split("_")[2][1:3]) for img in imgs])
    np.save("labels.npy", labels, allow_pickle=True)
    print("loading images...")
    imgs = load_data(imgs)
    print("subsampling...")
    samples = list()
    for i in tqdm(range(len(imgs))):
      samples.append(subsample(imgs[i], i))
    samples = np.array(samples)
    np.save("samples.npy", samples, allow_pickle=True)
    print("performing PCA...")
    PCA_fit(samples, labels)
    
