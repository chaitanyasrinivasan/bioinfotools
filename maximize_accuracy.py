import pandas as pd 
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(2750)

'''
Chaitanya Srinivasan
csriniv1

This is an active learning approach to maximize model accuracy on the cell free system
'''

# loads the dataset
def load(path):
  print("loading data...")
  df = pd.read_csv("DataPool.csv")
  cols = df.columns.tolist()
  data  = df.to_numpy()
  return cols, data[:-3]

# fits and scores the model
def GPR(Xtrain, ytrain, Xtest, ytest):
  kernel = DotProduct() + WhiteKernel()
  gpr = GaussianProcessRegressor(kernel=kernel, random_state=2750).fit(Xtrain, ytrain)
  return (gpr.score(Xtrain, ytrain), gpr.score(Xtest, ytest))

def main():
  # read data
  cols, data = load("DataPool.csv")
  X, y = data[:,:10], data[:,11]
  BUDGET = 510
  TEST_SIZE = len(X)-BUDGET
  INITIAL_BATCH = 20
  BATCH_SIZE = 1
  # create train and test set 
  idxs = np.random.choice(len(X), INITIAL_BATCH)
  Xtrain, ytrain = (X[idxs], 
                      y[idxs])
  X, y = np.delete(X, idxs, 0), np.delete(y, idxs, 0)
  idxs = np.random.choice(len(X), TEST_SIZE)
  Xtest, ytest = (X[idxs], 
                      y[idxs])
  X, y = np.delete(X, idxs, 0), np.delete(y, idxs, 0)
  print(len(Xtest))
  sys.exit(0)

  print("fitting data...")
  Rtrains, Rtests = list(), list()
  history = list()

  for i in tqdm(range((BUDGET-INITIAL_BATCH) // BATCH_SIZE)):
    # random sample
    query_idx = np.random.randint(len(X))
    Xtrain = np.concatenate((Xtrain, X[query_idx].reshape(1, 10)))
    ytrain = np.concatenate((ytrain, np.array([y[query_idx]])))
    # score model
    Rtrain, Rtest = GPR(Xtrain, ytrain, Xtest, ytest)
    Rtrains.append(Rtrain)
    Rtests.append(Rtest)
    # update pool
    X = np.delete(X, query_idx, 0)
    y = np.delete(y, query_idx, 0)
  # plot results
  print(Rtrains)
  print(Rtests)
  fig = plt.figure()
  plt.xlabel("Query Round")
  plt.ylabel("R^2")
  plt.plot(range(BUDGET-INITIAL_BATCH // BATCH_SIZE), Rtrains, label="R^2 train")
  plt.plot(range(BUDGET-INITIAL_BATCH // BATCH_SIZE), Rtests, label="R^2 test")
  plt.legend()
  plt.show()
  


if __name__ == "__main__":
  main()
