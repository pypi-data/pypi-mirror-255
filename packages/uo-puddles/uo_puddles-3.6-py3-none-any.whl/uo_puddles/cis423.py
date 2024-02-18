#for cis 423 class use

pypi_version = '1.67'

from sklearn.base import BaseEstimator, TransformerMixin

from sklearn.pipeline import Pipeline
import pandas as pd
pd.set_option('mode.chained_assignment', None)  #https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer  #chapter 6

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

from sklearn.neighbors import KNeighborsClassifier

#Check if a function is referencing global variables - bad
import builtins
import types
#use: @up_no_globals(globals())  #globals is function that returns *current* globals as dict
#DANGER DANGER: this fails on forward refs. Assumes helper functions all defined before main function. If not will get spurious error.
def up_no_globals(gfn:dict):

  def wrap(f):
    new_globals = {'__builtins__': builtins} 
    # removing keys from globals() storing global values in old_globals
    for key, val in gfn.items():
      if  callable(val):
          new_globals[key] = val
    new_f = types.FunctionType(f.__code__, globals=new_globals, argdefs=f.__defaults__)
    new_f.__annotations__ = f.__annotations__ # for some reason annotations aren't copied over
    return new_f

  return wrap

#drop by removing or keeping
class DropColumnsTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, column_list, action='drop'):
    assert action in ['keep', 'drop'], f'DropColumnsTransformer action {action} not in ["keep", "drop"]'
    assert isinstance(column_list, list), f'DropColumnsTransformer expected list but saw {type(column_list)}'
    self.column_list = column_list
    self.action = action

  #fill in rest below
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    remaining_set = set(self.column_list) - set(X.columns)

    X_ = X.copy()
    if self.action=='drop':
      if remaining_set:
        print(f"\nWarning: {self.__class__.__name__} does not contain these columns to drop: {remaining_set}.")
      X_ = X_.drop(columns=self.column_list, errors='ignore')
    else:
      assert not remaining_set, f'{self.__class__.__name__}.transform unknown columns to keep: {remaining_set}'
      X_ = X_[self.column_list]
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
  
#This class maps values in a column, numeric or categorical.
#Importantly, it does not change NaNs, leaving that for the imputer step.
class MappingTransformer(BaseEstimator, TransformerMixin):
  
  def __init__(self, mapping_column, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.'
    self.mapping_dict = mapping_dict
    self.mapping_column = mapping_column  #column to focus on

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.mapping_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column "{self.mapping_column}"'  #column legit?
    
    #now check to see if all keys are contained in column
    column_set = set(X[self.mapping_column])
    keys_not_found = set(self.mapping_dict.keys()) - column_set
    if keys_not_found:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these mapping keys do not appear in the column: {keys_not_found}\n")

    #now check to see if some keys are absent
    keys_absent = column_set -  set(self.mapping_dict.keys())
    if keys_absent:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these values in the column do not contain corresponing mapping keys: {keys_absent}\n")

    X_ = X.copy()
    X_[self.mapping_column].replace(self.mapping_dict, inplace=True)
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
    

class OHETransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, dummy_na=False, drop_first=False):  #False because worried about mismatched columns after splitting. Easier to add missing column.
    self.target_column = target_column
    self.dummy_na = dummy_na
    self.drop_first = drop_first
 
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column {self.target_column}'
    X_ = X.copy()
    X_ = pd.get_dummies(X_, columns=[self.target_column],
                        dummy_na=self.dummy_na,
                        drop_first = self.drop_first)
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
  
#This class will rename one or more columns.
class RenamingTransformer(BaseEstimator, TransformerMixin):
  #your __init__ method below

  def __init__(self, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.' 
    self.mapping_dict = mapping_dict

  #write the transform method without asserts. Again, maybe copy and paste from MappingTransformer and fix up.   
  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'RenamingTransformer.transform expected Dataframe but got {type(X)} instead.'
    #your assert code below

    column_set = set(X.columns)
    not_found = set(self.mapping_dict.keys()) - column_set
    assert not not_found, f"Columns {not_found}, are not in the data table"

    X_ = X.copy()
    return X_.rename(columns=self.mapping_dict)
  
#chapter 4 asks for 2 new transformers

class Sigma3Transformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column):  
    self.target_column = target_column
    
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    mean = X_[self.target_column].mean()
    sigma = X_[self.target_column].std()
    high_wall = mean + 3*sigma
    low_wall = mean - 3*sigma
    #print(f'{self.__class__.__name__} mean, sigma, low_wall, high_wall: {round(mean, 2)}, {round(sigma, 2)}, {round(low_wall, 2)}, {round(high_wall, 2)}')
    X_[self.target_column] = X_[self.target_column].clip(lower=low_wall, upper=high_wall)
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

class TukeyTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, fence='outer'):
    assert fence in ['inner', 'outer']
    self.target_column = target_column
    self.fence = fence
    
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    if len(set(X[self.target_column]))<20:
      print(f'{self.__class__.__name__} warning: {self.target_column} has less than 20 unique values. Consider it as categorical?')
      
    X_ = X.copy()
    q1 = X_[self.target_column].quantile(0.25)
    q3 = X_[self.target_column].quantile(0.75)
    iqr = q3-q1
    inner_low = q1-1.5*iqr
    outer_low = q1-3*iqr
    inner_high = q3+1.5*iqr
    outer_high = q3+3*iqr
    #print(f'{self.__class__.__name__} inner_low, inner_high, outer_low, outer_high: {round(inner_low, 2)}, {round(outer_low, 2)}, {round(inner_high, 2)}, {round(outer_high, 2)}')
    if self.fence=='inner':
      X_[self.target_column] = X_[self.target_column].clip(lower=inner_low, upper=inner_high)
    elif self.fence=='outer':
      X_[self.target_column] = X_[self.target_column].clip(lower=outer_low, upper=outer_high)
    else:
      assert False, f"fence has unrecognized value {self.fence}"
      
    if len(set(X_[self.target_column]))<5:
      print(f'{self.__class__.__name__} warning: {self.target_column} has less than 5 unique values after clipping.')
      
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

#chapter 5 asks for 1 new transformer

class MinMaxTransformer(BaseEstimator, TransformerMixin):
  def __init__(self):
    pass
    
  #fill in rest below
  def fit(self, X, y = None):
    print(f'Warning: {self.__class__.__name__}.fit does nothing.')
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    new_df = pd.DataFrame(scaler.fit_transform(X_), columns=X_.columns)
    return new_df

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
  
MinMaxTransformerWrapped = MinMaxTransformer  #for fall 22 bug

class MinMaxTransformerScratch(BaseEstimator, TransformerMixin):
  def __init__(self):
    self.column_stats = dict()

  #fill in rest below
  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'MinMaxTransformer.fit expected Dataframe but got {type(X)} instead.'
    if y: print(f'Warning: {self.__class__.__name__}.fit did not expect a value for y but got {type(y)} instead.')
    self.column_stats = {c:(X[c].min(),X[c].max()) for c in X.columns.to_list()}
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.column_stats, f'{self.__class__.__name__}.transform expected fit method to be called prior.'
    X_ = X.copy()
    fit_columns = set(self.column_stats.keys())
    transform_columns = set(X_.columns.to_list())
    not_fit = transform_columns - fit_columns
    not_transformed = fit_columns - transform_columns
    if not_fit: print(f'Warning: {self.__class__.__name__}.transform has more columns than fit: {not_fit}.')
    if not_transformed: print(f'Warning: {self.__class__.__name__}.transform has fewer columns than fit: {not_transformed}.')

    for c in fit_columns:
      if c not in transform_columns: continue
      cmin,cmax = self.column_stats[c]
      denom = cmax-cmin
      if not denom:
        print(f'Warning: column {c} has same min and max. No change made.')
      else:
        new_col = [(v-cmin)/denom for v in X_[c].to_list()]  #note NaNs remain NaNs - nice
        X_[c] = new_col
    
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
    result = self.transform(X)
    return result

##added in chapter 6

class KNNTransformer(BaseEstimator, TransformerMixin):
  def __init__(self,n_neighbors=5, weights="uniform"):
    #your code
    self.n_neighbors = n_neighbors
    self.weights=weights 

  def fit(self, X, y = None):
    print(f'Warning: KNNTransformer.fit does nothing.')
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'KNNTransformer.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    from sklearn.impute import KNNImputer
    imputer = KNNImputer(n_neighbors=self.n_neighbors, weights=self.weights, add_indicator=False)  #if True will screw up column match
    columns = X_.columns
    matrix = imputer.fit_transform(X_)
    result_df = pd.DataFrame(matrix,columns=columns)
    return result_df

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

class IterativeTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, estimator, max_iter=10, random_state=1234):
    self.estimator = estimator
    self.max_iter=max_iter 
    self.random_state=random_state

  #your code
  def fit(self, X, y = None):
    print(f'Warning: {self.__class__.__name__}.fit does nothing.')
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    imputer = IterativeImputer(estimator=self.estimator, max_iter=self.max_iter, random_state=self.random_state)
    columns = X_.columns
    matrix = imputer.fit_transform(X_)
    result_df = pd.DataFrame(matrix,columns=columns)
    return result_df

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

#chapter 7 add

from sklearn.metrics import f1_score#, balanced_accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegressionCV
from sklearn.neighbors import KNeighborsClassifier


def find_random_state(domain_df, labels, n=200):

  def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

  Var = []  #collect test_error/train_error where error based on F1 score
  for i in range(1, n):
      train_X, test_X, train_y, test_y = train_test_split(domain_df, labels, test_size=0.2, shuffle=True,
                                                      random_state=i, stratify=labels)
      model = KNeighborsClassifier(n_neighbors=5)  #start over every time
      model.fit(train_X, train_y)
      train_pred = model.predict(train_X)
      test_pred = model.predict(test_X)
      train_error = f1_score(train_y, train_pred)
      test_error = f1_score(test_y, test_pred)
      variance = test_error/train_error
      Var.append(variance)
      
  rs_value = np.average(Var)

  nearest = find_nearest(Var, rs_value)
  return Var.index(nearest)

import matplotlib.pyplot as plt

def heat_map(zipped, label_list=(0,1)):
  zlist = list(zipped)
  case_list = []
  for i in range(len(label_list)):
    inner_list = []
    for j in range(len(label_list)):
      inner_list.append(zlist.count((label_list[i], label_list[j])))
    case_list.append(inner_list)


  fig, ax = plt.subplots(figsize=(5, 5))
  ax.imshow(case_list)
  ax.grid(False)
  title = ''
  for i,c in enumerate(label_list):
    title += f'{i}={c} '
  ax.set_title(title)
  ax.set_xlabel('Predicted outputs', fontsize=16, color='black')
  ax.set_ylabel('Actual outputs', fontsize=16, color='black')
  ax.xaxis.set(ticks=range(len(label_list)))
  ax.yaxis.set(ticks=range(len(label_list)))
  
  for i in range(len(label_list)):
      for j in range(len(label_list)):
          ax.text(j, i, case_list[i][j], ha='center', va='center', color='white', fontsize=32)
  plt.show()
  return None

#ch9

titanic_transformer = Pipeline(steps=[
    ('drop', DropColumnsTransformer(['Age', 'Gender', 'Class', 'Joined', 'Married',  'Fare'], 'keep')),
    ('gender', MappingTransformer('Gender', {'Male': 0, 'Female': 1})),
    ('class', MappingTransformer('Class', {'Crew': 0, 'C3': 1, 'C2': 2, 'C1': 3})),
    ('ohe', OHETransformer(target_column='Joined')),
    ('age', TukeyTransformer(target_column='Age', fence='outer')), #from chapter 4
    ('fare', TukeyTransformer(target_column='Fare', fence='outer')), #from chapter 4
    ('minmax', MinMaxTransformer()),  #from chapter 5
    ('imputer', KNNTransformer())  #from chapter 6
    ], verbose=True)

customer_transformer = Pipeline(steps=[
    ('id', DropColumnsTransformer(column_list=['ID'])),
    ('os', OHETransformer(target_column='OS')),
    ('isp', OHETransformer(target_column='ISP')),
    ('level', MappingTransformer('Experience Level', {'low': 0, 'medium': 1, 'high':2})),
    ('gender', MappingTransformer('Gender', {'Male': 0, 'Female': 1})),
    ('time spent', TukeyTransformer('Time Spent', 'inner')),
    ('minmax', MinMaxTransformer()),
    ('imputer', KNNTransformer())  #from chapter 6
    ], verbose=True)


def dataset_setup(full_table, label_column_name, the_transformer, rs, ts=.2):
  feature_table = full_table.drop(columns=label_column_name)
  labels = full_table[label_column_name].to_list()
  X_train, X_test, y_train, y_test  = train_test_split(feature_table, labels, test_size=ts, shuffle=True,
                                                    random_state=rs, stratify=labels)
  X_train_transformed = the_transformer.fit_transform(X_train)
  X_test_transformed = the_transformer.fit_transform(X_test)
  x_trained_numpy = X_train_transformed.to_numpy()
  x_test_numpy = X_test_transformed.to_numpy()
  y_train_numpy = np.array(y_train)
  y_test_numpy = np.array(y_test)
  return x_trained_numpy, x_test_numpy, y_train_numpy,  y_test_numpy

def titanic_setup(titanic_table, transformer=titanic_transformer, rs=40, ts=.2):
  return dataset_setup(titanic_table, 'Survived', transformer, rs=rs, ts=ts)

def customer_setup(customer_table, transformer=customer_transformer, rs=76, ts=.2):
  return dataset_setup(customer_table, 'Rating', transformer, rs=rs, ts=ts)

def threshold_results(thresh_list, actuals, predicted):
  result_df = pd.DataFrame(columns=['threshold', 'precision', 'recall', 'f1', 'accuracy'])
  for t in thresh_list:
    yhat = [1 if v >=t else 0 for v in predicted]
    #note: where TP=0, the Precision and Recall both become 0
    precision = precision_score(actuals, yhat, zero_division=0)
    recall = recall_score(actuals, yhat, zero_division=0)
    f1 = f1_score(actuals, yhat)
    accuracy = accuracy_score(actuals, yhat)
    result_df.loc[len(result_df)] = {'threshold':t, 'precision':precision, 'recall':recall, 'f1':f1, 'accuracy':accuracy}

  result_df = result_df.round(2)

  #Next bit fancies up table for printing. See https://betterdatascience.com/style-pandas-dataframes/
  #Note that fancy_df is not really a dataframe. More like a printable object.
  headers = {
    "selector": "th:not(.index_name)",
    "props": "background-color: #800000; color: white; text-align: center"
  }
  properties = {"border": "1px solid black", "width": "65px", "text-align": "center"}

  fancy_df = result_df.style.format(precision=2).set_properties(**properties).set_table_styles([headers])
  return (result_df, fancy_df)

def halving_search(model, grid, x_train, y_train, factor=3, scoring='roc_auc'):
  #your code below
  halving_cv = HalvingGridSearchCV(
    model, grid,  #our model and the parameter combos we want to try
    scoring=scoring,  #could alternatively choose f1, accuracy or others
    n_jobs=-1,
    min_resources="exhaust",
    factor=factor,  #a typical place to start so triple samples and take top 3rd of combos on each iteration
    cv=5, random_state=1234,
    refit=True  #remembers the best combo and gives us back that model already trained and ready for testing
)

  grid_result = halving_cv.fit(x_train, y_train)
  return grid_result
