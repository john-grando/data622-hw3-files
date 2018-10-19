#DATA 622 Homework 2 - score_model.py
#John Grando
# -*- coding: utf-8 -*-

import logging, logging.config, os, sys, pickle, boto3, tempfile
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

#append local directory to path so that modules can be loaded
sys.path.append(os.path.join(os.getcwd()))
#get functions from local modules to clean and pre-process data
import train_model

#make logger a global variable
logger = logging.getLogger('hw2Logger')

#instantiate aws
s3 = boto3.resource('s3')
s3_r = boto3.client('s3')

    
def read_model(s3_r, bucket, key):
   """
   Load model from pickle file
   """
   model = None
   try:
       #try to load the pickle file
       obj = s3_r.get_object(Bucket=bucket, Key=key)
       model = pickle.loads(obj['Body'].read())
   except Exception:
       logger.exception("Model loading failed for %s", key)
       sys.exit(1)
   logger.info("Model loaded for %s", key)
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

def get_predictions(s3_r, bucket, file, model_file):
    """
    Make predictions using a saved model and test data
    """
    predictions = None
    model = None
    try:
        #load data and make predictions
        logger.info("Load test file and clean data")
        X_clean, y = train_model.data_clean(s3_r, bucket, file, train_data=False)
        logger.info("Load model")
        model = read_model(s3_r, bucket, model_file)
        logger.info("Test model")
        predictions = model.predict(X_clean)
        logger.info("Predictions completed")
    except:
        logger.error("Unable to make predictions based on the inputs")
        sys.exit(1)
    try:
        #Save predictions to csv file
        obj = s3_r.get_object(Bucket=bucket, Key=file)
        input_df = pd.read_csv(obj['Body'])
        with tempfile.NamedTemporaryFile() as temp:
            pd.DataFrame(pd.concat([input_df['PassengerId'], pd.DataFrame(predictions)], axis=1, ignore_index=True)).rename(index=str, columns={0:'PassengerId', 1:'Survived'}).to_csv(temp.name, index=False)
            temp.flush()
            s3_r.upload_file(temp.name, bucket, 'Predictions.csv')
            
    except Exception:
        logger.exception("Unable to write predictions, program continuing")
    return predictions, model

def get_reports(s3_r, bucket, key, model):
    """
    Generate reports for a model based on input file
    """
    cf_report = None
    try:
        logger.info("load training file and clean")
        X_clean, y = train_model.data_clean(s3_r, bucket, key, train_data=True)
        cf_report = classification_report(y, model.predict(X_clean))
        logger.info("Classification report for test data \n %s", cf_report)
        with tempfile.NamedTemporaryFile(mode='w') as temp:
            temp.write(cf_report)
            temp.flush()
            s3_r.upload_file(temp.name, bucket, 'ClassificationReport.txt')
    except Exception:
        logger.exception("classification report could not be generated")
    return

def main():
    """
     Get scoring data and test with a pre-made random forest model.  Print ouputs.
    """
    if len(sys.argv)>1:
        if sys.argv[1] == 'remote':
            s3 = boto3.resource('s3',
                                aws_access_key_id=os.environ['aws_access_key_id'],
                                aws_secret_access_key=os.environ['aws_secret_access_key'],
                                aws_session_token=os.environ['aws_session_token']
                                )
            s3_r = boto3.client('s3',
                                aws_access_key_id=os.environ['aws_access_key_id'],
                                aws_secret_access_key=os.environ['aws_secret_access_key'],
                                aws_session_token=os.environ['aws_session_token']
                                )
        else:
            logger.exception("Invalid argument")
            sys.exit(1)
    else:
        s3 = boto3.resource('s3')
        s3_r = boto3.client('s3')
    bucket='data622-hw3'
    try:
        s3.Object(bucket, 'train_data.csv').load()
        s3.Object(bucket, 'test_data.csv').load()
    except:
        logger.exception("files are missing from s3 instance, please rerun pull_data.py")
        sys.exit(1)
    #get predictions using the test data set
    _, model = get_predictions(s3_r, bucket, 'test_data.csv', 'RandomForestModel.pkl')
    #get training data and print classification report
    get_reports(s3_r, bucket, 'train_data.csv', model)
    return

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('hw2Logger')
    main()