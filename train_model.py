#DATA 622 Homework 2 - train_model.py
#John Grando
# -*- coding: utf-8 -*-

import os, sys, logging, logging.config, pickle
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report

#make logger a global variable
logger = logging.getLogger('hw2Logger')

def data_clean(file_loc, train_data = None):
    """
    clean csv file and process it into a dataframe.  Return X and y objects.
    """
    #set y to null for when non-training data is used
    y = None
    try:
        #Read in csv file
        X = pd.read_csv(file_loc)
    except:
        logger.error("%s could not be read", file_loc)
    logger.info("%s read", file_loc)
    try:
        if train_data:
            #Get response values for testing
            y = X.pop('Survived').values
    except:
        logger.error("Response Category is not available")
    try:
        #Drop columns which either cannot or should not be used for training.
        X = X.drop(['PassengerId', 'Name', 'Ticket'], axis = 1)
    except:
        logger.error("A referenced column name in the training data does not exist")
        logger.error("Available columns %s", X.columns.values)
        sys.exit(1)
    logging.info("Extraneous columns removed")
    try:
        #format categorical columns using numeric indicators
        X['Pclass'] = X['Pclass'].astype(object)
    except:
        logger.error("Column type conversion on the training data failed")
        sys.exit(1)
    return X, y
        
def data_preprocess(X):
    """
    Format cleaned data such that it is ready for input into machine learning algorithm
    """
    if not isinstance(X, pd.DataFrame):
        logger.error("Preprocessing input is not a dataframe")
        sys.exit(1)
    try:
        #Perform data transformation
        #This is all read in as one step because one pipe is used.
        col_kinds = [dt.kind for dt in X.dtypes]
        all_columns = [i for i in X.columns.values]
        is_num = [i != 'O' for i in col_kinds]
        num_cols = [i for (i,j) in zip(all_columns, is_num) if j == True]
        cat_cols = [i for i in all_columns if i not in num_cols]
        cat_impute_step = ('cis', 
                           SimpleImputer(strategy='constant', 
                                         fill_value='MISSING'))
        cat_ohe_step = ('cos', OneHotEncoder(sparse=False,
                                            handle_unknown='ignore'))
        num_impute_step = ('nis', 
                           SimpleImputer(strategy='median'))
        cat_steps = [cat_impute_step, cat_ohe_step]
        num_steps = [num_impute_step]
        cat_pipe = Pipeline(cat_steps)
        num_pipe = Pipeline(num_steps)
        #cat_cols = ['Pclass', 'Sex', 'Cabin', 'Embarked']
        logger.debug("Categorical transformation performed for %s", cat_cols)
        logger.debug("Numeric transformation performed for %s", num_cols)
        transformers = [('cat', cat_pipe, cat_cols), 
                        ('num', num_pipe, num_cols)]
        ct = ColumnTransformer(transformers=transformers)
    except:
        logger.error("Transformation of training data failed")
        sys.exit(1)
    logging.info("Training data transformation complete")
    return ct

def create_randomforest(X, y, grid_search=None):
    """
    Create random forest model and save to file
    """
    try:
        # preprocess data    
        ct = data_preprocess(X)
    except:
        logger.error("Data could not be preprocessed")
        sys.exit(1)
    try:
        #Split data
        X_train, X_test, y_train, y_test = train_test_split(X, 
                                                        y,
                                                        test_size=0.3)
    except:
        logger.error("Data could not be split")
        sys.exit(1)
    try:
        #Run data through pipeline and create model
        rf_pipe = Pipeline([('transform', ct),
                            ('rfc', RandomForestClassifier(n_estimators=100,
                                                          max_depth=12,
                                                          random_state = 345))])
        if grid_search:
            try:
                param_grid = {'rfc__n_estimators' : [10, 50, 100, 250, 500, 750, 1000],
                              'rfc__max_depth' : [2, 4, 6, 8, 10, 12, 14, 16, 20]}
                grid = GridSearchCV(rf_pipe, 
                                    param_grid=param_grid,
                                    cv=10)
                grid.fit(X_train, y_train)
                logger.info("Best cross-validation accuracy: {:.2f}".format(grid.best_score_))
                logger.info("Test set score: {:.2f}".format(grid.score(X_test, y_test)))
                logger.info("Best parameters: {}".format(grid.best_params_))
                plt.matshow(grid.cv_results_['mean_test_score'].reshape(len(param_grid['rfc__max_depth']), -1),
                            vmin=min(grid.cv_results_['mean_test_score']), cmap="viridis")
                plt.xlabel("rfc__n_estimators")
                plt.ylabel("rfc__max_depth")
                plt.xticks(range(len(param_grid['rfc__n_estimators'])), 
                           param_grid['rfc__n_estimators'])
                plt.yticks(range(len(param_grid['rfc__max_depth'])),
                           param_grid['rfc__max_depth'])
                plt.colorbar()
                plt.savefig('grid_search_cv.png', bbox_inches='tight')
            except:
                logger.error("Grid search failed, program proceeding")
        rf_pipe.fit(X_train, y_train)
        #get scores
        train_score = rf_pipe.score(X_train, y_train)
        test_score = rf_pipe.score(X_test, y_test)   
    except:
        logger.error("Model could not be created")
        sys.exit(1)
    try:
        #Save model to file
        with open("RandomForestModel.pkl", 'wb') as f:
            pickle.dump(rf_pipe, f)
    except:
        logger.error("Model could not be saved to file but program will continue")
    return train_score, test_score, classification_report(y_train, rf_pipe.predict(X_train))

def main():
    """
    Get data and train a random forest model
    """
    file_loc = os.path.join(os.getcwd(), "train_data.csv")
    if os.path.isfile(file_loc):
        logger.info("load training file and clean")
        X_clean, y = data_clean(file_loc, train_data=True)
        logger.info("Create RandomForest model")
        train_score, test_score, _ = create_randomforest(X_clean, y, grid_search=False)
        logger.info("Model training score: %s", round(train_score, 3))
        logger.info("Model test score: %s ", round(test_score, 3))
    else:
        logger.error("The training data file is missing")
        sys.exit()
    return

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('hw2Logger')
    main()
