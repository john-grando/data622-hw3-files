#DATA 622 Homework 2 - pull_data.py
#John Grando
# -*- coding: utf-8 -*-

import logging, logging.config, os, sys, pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

#append local directory to path so that modules can be loaded
sys.path.append(os.path.join(os.getcwd()))
#get functions from local modules to clean and pre-process data
import train_model

#make logger a global variable
logger = logging.getLogger('hw2Logger')
    
def read_model(file_loc):
   """
   Load model from pickle file
   """
   model = None
   try:
       #try to load the pickle file
       with open(file_loc, 'rb') as f: 
           model = pickle.load(f)
   except:
       logger.error("Model loading failed for %s", file_loc)
       logger.info("Model loaded for %s", file_loc)
   return model

def score_set_transform(X):
    """
    Process Pipeline into transformed array
    """
    X_transformed = None
    try:
        #try to process test data
        ct = train_model.data_preprocess(X)
        X_transformed = Pipeline([('transform', ct)])
    except:
        logger.error("Test data could not be transformed")
    return X_transformed.fit_transform(X)

def get_predictions(file_loc, model_file_loc):
    """
    Make predictions using a saved model and test data
    """
    predictions = None
    model = None
    if os.path.isfile(file_loc):
        try:
            #load data and make predictions
            logger.info("Load test file and clean data")
            X_clean, y = train_model.data_clean(file_loc)
            logger.info("Load model")
            model = read_model(model_file_loc)
            logger.info("Test model")
            predictions = model.predict(X_clean)
            logger.info("Predictions completed")
        except:
            logger.error("Unable to make predictions based on the inputs")
            sys.exit(1)
    else:
        logger.error("The testing data file is missing")
        sys.exit(1)
    try:
        #Save predictions to csv file
        pd.DataFrame(predictions).to_csv("Predictions.csv", index=False)
    except:
        logger.error("Unable to write predictions, program continuing")
    return predictions, model

def get_reports(file_loc, model):
    """
    Generate reports for a model based on input file
    """
    if os.path.isfile(file_loc):
        try:
            logger.info("load training file and clean")
            X_clean, y = train_model.data_clean(file_loc, train_data=True)
            cf_report = classification_report(y, model.predict(X_clean))
            logger.info("Classification report for test data \n %s", cf_report)
        except:
            logger.error("classification report could not be generated")
        with open("ClassificationReport.txt", 'w') as f:
            f.write(cf_report)
    else:
        logger.error("Input file does not exist")
    return

def main():
    """
     Get scoring data and test with a pre-made random forest model.  Print ouputs.
    """
    file_loc = os.path.join(os.getcwd(), "test_data.csv")
    model_file_loc = os.path.join(os.getcwd(),"RandomForestModel.pkl")
    #get predictions using the test data set
    _, model = get_predictions(file_loc, model_file_loc)
    #get training data and print classification report
    file_loc = os.path.join(os.getcwd(), "train_data.csv")
    get_reports(file_loc, model)
    return

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('hw2Logger')
    main()