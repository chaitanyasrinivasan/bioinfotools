import pandas as pd 
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
#from sklearn.model_selection import train_test_split
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import sys

np.random.seed(2750)


'''
Chaitanya Srinivasan
csriniv1

This is an active learning approach to maximize yield on the cell free system
'''

#loads the data
def load(path):
  print("loading data...")
  df = pd.read_csv("DataPool.csv")
  cols = df.columns.tolist()
  data  = df.to_numpy()
  return cols, data[:-3]

# returns and sklearn model object
def GPR(Xtrain, ytrain):
  kernel = DotProduct() + WhiteKernel()
  gpr = GaussianProcessRegressor(kernel=kernel, random_state=0).fit(Xtrain, ytrain)
  return gpr

def main():
  # read data
  cols, data = load("DataPool.csv")
  X, y = data[:,:10], data[:,11]
  BUDGET = 510
  BATCH_SIZE = 102
  INITIAL_BATCH = BATCH_SIZE
  # random initial experiments
  idxs = np.random.choice(len(X), INITIAL_BATCH)
  Xtrain, ytrain = (X[idxs], 
                      y[idxs])
  history = idxs
  yields = [np.median(ytrain)]
  distributions = [ytrain]
  r2s = list()
  testr2s = list()
  # 5 rounds of experiments
  for i in tqdm(range((BUDGET-INITIAL_BATCH) // BATCH_SIZE)):
    # train regressor
    gpr = GPR(Xtrain, ytrain)
    testr2s.append(gpr.score(np.array([X[i] for i in range(len(X)) if i not in history]),
                             np.array([y[i] for i in range(len(y)) if i not in history])))
    r2s.append(gpr.score(Xtrain, ytrain))
    # optimize yield from pool, choose top BATCHSIZE best results
    pool = []
    for j in range(len(X)):
      if j not in history:
        pool.append(X[j])
    pool_hats= gpr.predict(np.array(pool))
    best_idxs = pool_hats.argsort()[-BATCH_SIZE:][::-1]
    # "perform experiment", update history, training set, yields
    history += best_idxs
    Xtrain = np.concatenate((Xtrain, X[best_idxs]))
    ytrain = np.concatenate((ytrain, y[best_idxs]))
    distributions.append(y[best_idxs])
    yields.append(np.median(y[best_idxs]))
  # update model with complete budgeted training set
  Xtest = np.array([X[i] for i in range(len(X)) if i not in history])
  ytest = np.array([y[i] for i in range(len(y)) if i not in history])
  gpr = GPR(Xtrain, ytrain)
  r2s.append(gpr.score(Xtrain, ytrain))
  print("Yields", yields)
  print("Train R2s", r2s)
  print("Test R2s", testr2s)
  fig = plt.figure() 
  plt.boxplot(distributions)
  plt.xlabel("Rounds")
  plt.ylabel("Yield")
  plt.show()
    

if __name__ == "__main__":
  main()
