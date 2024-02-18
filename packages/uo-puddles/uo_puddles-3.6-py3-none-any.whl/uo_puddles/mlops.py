#for cis 423 class use

pypi_version = '1.67'
import sklearn
sklearn.set_config(transform_output="pandas")  #says pass pandas tables through pipeline instead of numpy matrices

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

#chapter 7
import subprocess
import sys
subprocess.call([sys.executable, '-m', 'pip', 'install', 'category_encoders'])
import category_encoders as ce

import joblib

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

  
#This class maps values in a column, numeric or categorical.
#Importantly, it does not change NaNs, leaving that for the imputer step.
class CustomMappingTransformer(BaseEstimator, TransformerMixin):

  def __init__(self, mapping_column, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.'
    self.mapping_dict = mapping_dict
    self.mapping_column = mapping_column  #column to focus on

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.mapping_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column "{self.mapping_column}"'  #column legit?

    #Set up for producing warnings. First have to rework nan values to allow set operations to work.
    #In particular, the conversion of a column to a Series, e.g., X[self.mapping_column], transforms nan values in strange ways that screw up set differencing.
    #Strategy is to convert empty values to a string then the string back to np.nan
    placeholder = "NaN"
    column_values = X[self.mapping_column].fillna(placeholder).tolist()  #convert all nan values to the string "NaN" in new list
    column_values = [np.nan if v == placeholder else v for v in column_values]  #now convert back to np.nan
    keys_values = self.mapping_dict.keys()

    column_set = set(column_values)  #without the conversion above, the set will fail to have np.nan values where they should be.
    keys_set = set(keys_values)      #this will have np.nan values where they should be so no conversion necessary.

    #now check to see if all keys are contained in column.
    keys_not_found = keys_set - column_set
    if keys_not_found:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these mapping keys do not appear in the column: {keys_not_found}\n")

    #now check to see if some keys are absent
    keys_absent = column_set -  keys_set
    if keys_absent:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these values in the column do not contain corresponding mapping keys: {keys_absent}\n")

    #do actual mapping
    X_ = X.copy()
    X_[self.mapping_column].replace(self.mapping_dict, inplace=True)
    return X_

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result
    

class CustomOHETransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, dummy_na=False, drop_first=False):  #False because worried about mismatched columns after splitting. Easier to add missing column.
    self.target_column = target_column
    self.dummy_na = dummy_na
    self.drop_first = drop_first
 
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column {self.target_column}'
    X_ = X.copy()
    X_ = pd.get_dummies(X_, columns=[self.target_column],
                        dummy_na=self.dummy_na,
                        drop_first = self.drop_first)
    return X_

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result
  
#This class will rename one or more columns.
class CustomRenamingTransformer(BaseEstimator, TransformerMixin):
  #your __init__ method below

  def __init__(self, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.' 
    self.mapping_dict = mapping_dict

  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  #write the transform method without asserts. Again, maybe copy and paste from MappingTransformer and fix up.   
  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'RenamingTransformer.transform expected Dataframe but got {type(X)} instead.'
    #your assert code below

    column_set = set(X.columns)
    not_found = set(self.mapping_dict.keys()) - column_set
    assert not not_found, f"Columns {not_found}, are not in the data table"

    X_ = X.copy()
    return X_.rename(columns=self.mapping_dict)

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result

class CustomPearsonTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, threshold):
    self.threshold = threshold
    self.correlated_columns = None

  #define methods below

  def fit(self, X, y = None):
    df_corr = X.corr(method='pearson')
    masked_df = df_corr.abs() > self.threshold
    upper_mask = np.triu(masked_df, k=1)
    self.correlated_columns = [c for i,c in enumerate(df_corr.columns) if upper_mask[:,i].any()]
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.correlated_columns, list), f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'

    X_ = X.drop(columns=self.correlated_columns)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X, y)
    result = self.transform(X)
    return result

class CustomDythonTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, threshold):
    self.threshold = threshold
    self.drop_columns = None

  #define methods below

  def fit(self, X, y = None):
    assoc_matrix = nominal.associations(X, nominal_columns='auto', compute_only=True)
    corr_matrix = assoc_matrix['corr'].abs().round(2)
    masked_df = corr_matrix > self.threshold
    upper_mask = np.triu(masked_df, k=1)
    self.drop_columns = [c for i,c in enumerate(X.columns) if upper_mask[:,i].any()]
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.drop_columns, list), f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'

    X_ = X.drop(columns=self.drop_columns)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X, y)
    result = self.transform(X)
    return result
  
#chapter 4 asks for 2 new transformers

class CustomSigma3Transformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column):
    self.target_column = target_column
    self.high_wall = None
    self.low_wall = None

  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
    mean = X[self.target_column].mean()
    sigma = X[self.target_column].std()
    self.high_wall = float(mean + 3.0*sigma)
    self.low_wall = mean - 3.0*sigma
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.high_wall, float), f'{self.__class__.__name__}.transform appears no fit was called prior.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'

    X_ = X.copy()
    X_[self.target_column] = X_[self.target_column].clip(lower=self.low_wall, upper=self.high_wall)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
    result = self.transform(X)
    return result

class CustomTukeyTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, fence='outer'):
    assert fence in ['inner', 'outer']
    self.target_column = target_column
    self.fence = fence
    self.inner_low = None
    self.outer_low = None
    self.inner_high = None
    self.outer_high = None

  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
    q1 = X[self.target_column].quantile(0.25)
    q3 = X[self.target_column].quantile(0.75)
    iqr = q3-q1
    self.inner_low = q1-1.5*iqr
    self.outer_low = q1-3.0*iqr
    self.inner_high = q3+1.5*iqr
    self.outer_high = q3+3.0*iqr
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.inner_low, float), f'{self.__class__.__name__}.transform appears no fit was called prior.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'

    X_ = X.copy()
    if self.fence=='inner':
      X_[self.target_column] = X_[self.target_column].clip(lower=self.inner_low, upper=self.inner_high)
    elif self.fence=='outer':
      X_[self.target_column] = X_[self.target_column].clip(lower=self.outer_low, upper=self.outer_high)
    else:
      assert False, f"fence has unrecognized value {self.fence}"
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
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

class CustomRobustTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, column):
    #fill in rest below
    self.target_column = column
    self.iqr = None
    self.med = None

  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
    self.iqr = float(X[self.target_column].quantile(.75) - X[self.target_column].quantile(.25))
    self.med = X[self.target_column].median()
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.iqr, float), f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'

    X_ = X.copy()
    X_[self.target_column] -= self.med
    X_[self.target_column] /= self.iqr
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

titanic_variance_based_split = 107
customer_variance_based_split = 113

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
    ('map_gender', CustomMappingTransformer('Gender', {'Male': 0, 'Female': 1})),
    ('map_class', CustomMappingTransformer('Class', {'Crew': 0, 'C3': 1, 'C2': 2, 'C1': 3})),
    ('target_joined', ce.TargetEncoder(cols=['Joined'],
                           handle_missing='return_nan', #will use imputer later to fill in
                           handle_unknown='return_nan'  #will use imputer later to fill in
    )),
    ('tukey_age', CustomTukeyTransformer(target_column='Age', fence='outer')),
    ('tukey_fare', CustomTukeyTransformer(target_column='Fare', fence='outer')),
    ('scale_age', CustomRobustTransformer('Age')),  #from chapter 5
    ('scale_fare', CustomRobustTransformer('Fare')),  #from chapter 5
    ('imputer', KNNImputer(n_neighbors=5, weights="uniform", add_indicator=False))  #from chapter 6
    ], verbose=True)

customer_transformer = Pipeline(steps=[
    ('map_os', CustomMappingTransformer('OS', {'Android': 0, 'iOS': 1})),
    ('target_isp', ce.TargetEncoder(cols=['ISP'],
                           handle_missing='return_nan', #will use imputer later to fill in
                           handle_unknown='return_nan'  #will use imputer later to fill in
    )),
    ('map_level', CustomMappingTransformer('Experience Level', {'low': 0, 'medium': 1, 'high':2})),
    ('map_gender', CustomMappingTransformer('Gender', {'Male': 0, 'Female': 1})),
    ('tukey_age', CustomTukeyTransformer('Age', 'inner')),  #from chapter 4
    ('tukey_time spent', CustomTukeyTransformer('Time Spent', 'inner')),  #from chapter 4
    ('scale_age', CustomRobustTransformer('Age')), #from 5
    ('scale_time spent', CustomRobustTransformer('Time Spent')), #from 5
    ('imputer', KNNImputer(n_neighbors=5, weights="uniform", add_indicator=False))  #from chapter 6
    ], verbose=True)


def dataset_setup(original_table, label_column_name:str, the_transformer, rs, ts=.2):
  #your code below
  feature_table = original_table.drop(columns=label_column_name)
  labels = original_table[label_column_name].to_list()
  X_train, X_test, y_train, y_test  = train_test_split(feature_table, labels, test_size=ts, shuffle=True,
                                                    random_state=rs, stratify=labels)
  X_train_transformed = the_transformer.fit_transform(X_train, y_train)
  X_test_transformed = the_transformer.transform(X_test)
  x_train_numpy = X_train_transformed.to_numpy()
  x_test_numpy = X_test_transformed.to_numpy()
  y_train_numpy = np.array(y_train)
  y_test_numpy = np.array(y_test)
  return x_train_numpy, x_test_numpy, y_train_numpy,  y_test_numpy

def titanic_setup(titanic_table, transformer=titanic_transformer, rs=titanic_variance_based_split, ts=.2):
  return dataset_setup(titanic_table, 'Survived', transformer, rs=rs, ts=ts)

def customer_setup(customer_table, transformer=customer_transformer, rs=customer_variance_based_split, ts=.2):
  return dataset_setup(customer_table, 'Rating', transformer, rs=rs, ts=ts)

def threshold_results(thresh_list, actuals, predicted):
  result_df = pd.DataFrame(columns=['threshold', 'precision', 'recall', 'f1', 'accuracy', 'auc'])
  for t in thresh_list:
    yhat = [1 if v >=t else 0 for v in predicted]
    #note: where TP=0, the Precision and Recall both become 0. And I am saying return 0 in that case.
    precision = precision_score(actuals, yhat, zero_division=0)
    recall = recall_score(actuals, yhat, zero_division=0)
    f1 = f1_score(actuals, yhat)
    accuracy = accuracy_score(actuals, yhat)
    auc = roc_auc_score(actuals, yhat)
    result_df.loc[len(result_df)] = {'threshold':t, 'precision':precision, 'recall':recall, 'f1':f1, 'accuracy':accuracy, 'auc': auc}

  result_df = result_df.round(2)

  #Next bit fancies up table for printing. See https://betterdatascience.com/style-pandas-dataframes/
  #Note that fancy_df is not really a dataframe. More like a printable object.
  headers = {
    "selector": "th:not(.index_name)",
    "props": "background-color: #800000; color: white; text-align: center"
  }
  properties = {"border": "1px solid black", "width": "65px", "text-align": "center"}
  result_df = result_df.round(2)
  fancy_df = result_df.style.highlight_max(color = 'pink', axis = 0).set_properties(**properties).set_table_styles([headers]).format(precision=2)
  return (result_df, fancy_df)

def halving_search(model, grid, x_train, y_train, factor=2, min_resources="exhaust", scoring='roc_auc'):
  #your code below
  halving_cv = HalvingGridSearchCV(
    model, grid,  #our model and the parameter combos we want to try
    scoring=scoring,  #could alternatively choose f1, accuracy or others
    n_jobs=-1,
    min_resources=min_resources,
    factor=factor,  #a typical place to start so triple samples and take top 3rd of combos on each iteration
    cv=5, random_state=1234,
    refit=True  #remembers the best combo and gives us back that model already trained and ready for testing
)

  grid_result = halving_cv.fit(x_train, y_train)
  return grid_result
