#DATA 622 Homework 2 - pull_data.py
#John Grando
# -*- coding: utf-8 -*-

import os, sys, logging, logging.config
import pandas as pd

def data_clean(file_loc):
    df = pd.DataFrame()
    input_df = pd.read_csv(file_loc)
    print(input_df.isnull().any())
    try:
        #Drop columns which either cannot or should not be used for training
        df = input_df.drop(['PassengerId', 'Survived', 'Name'], axis = 1)
    except:
        logger.error("A referenced column name in the training data does not exist")
        sys.exit(1)
    print(df.head(10))
    return df

def main():
    """
    Get process data and train data with a random forest model
    """
    if os.path.isfile(os.path.join(os.getcwd(), "train_data.csv")) and os.path.isfile(os.path.join(os.getcwd(), "test_data.csv")):
        logger.info("load training file")
        logger.info("clean data")
        train_clean_df = data_clean(os.path.join(os.getcwd(), "train_data.csv"))
        
        print(train_clean_df.dtypes)
    else:
        print("The training and/or testing data files are missing")
        sys.exit()
    return

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('hw2Logger')
    main()