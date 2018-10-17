#DATA 622 Homework 2 - pull_data.py
#John Grando
# -*- coding: utf-8 -*-

import requests, os, sys, logging, logging.config
import pandas as pd

loginURL = 'https://www.kaggle.com/account/login'
train_url = "https://www.kaggle.com/c/titanic/download/train.csv"
test_url = "https://www.kaggle.com/c/titanic/download/test.csv"
#make logger a global variable
logger = logging.getLogger('hw2Logger')

def get_credentials():
    """
    Create a payload with proper credentials that are stored in a hidden file within the directory
    """
    credential_d = {}
    with open(os.path.join(os.getcwd(), "HiddenFiles", "credentials.txt")) as f:
        credentials = [x.strip().split(",") for x in f.readlines()]
        for username, password in credentials:
            credential_d['__RequestVerificationToken'] = ''
            credential_d['UserName'] = username
            credential_d['Password'] = password
            credential_d['rememberme'] = 'false'
            #process only one line
            break
    return credential_d

def get_kaggle_data(url, payload, file_name):
    """
    Get CSV files from kaggle and test
    """
    try:
        payload = get_credentials()
        #I had mulitple issues with the standard method of importing files 
        #and this was the only answer that worked for me
        #https://stackoverflow.com/questions/50863516/issue-in-extracting-titanic-training-data-from-kaggle-using-jupyter-notebook
        with requests.Session() as c:
            response = c.get(loginURL).text
            AFToken = response[response.index('antiForgeryToken')+19:response.index('isAnonymous: ')-12]
            payload['__RequestVerificationToken']=AFToken
            c.post(loginURL + "?isModal=true&returnUrl=/", data=payload)
            response = c.get(url)

        #By specifying 'with' instead of creating the file in one line (f = open()) we do not need to call close()
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size = 512 * 1024):
                if chunk: 
                    f.write(chunk)

        #test the file
        try:
            t_df = pd.read_csv(os.path.join(os.getcwd(),file_name))
            if t_df.empty == True:
                logger.error("The CSV file appears to be empty")
                sys.exit(1)
        except:
            logger.error("There was an error testing the csv file")
            sys.exit(1)
    except:
        logger.error("There was an error downloading the file")
        sys.exit(1)
    return

def main():
    """
    Get training and test files from the titanic dataset at kaggle.com
    """
    if os.path.isfile(os.path.join(os.getcwd(), 'train_data.csv')) and os.path.isfile(os.path.join(os.getcwd(), 'test_data.csv')):
        logger.info("files already downloaded, nothing downloaded")
    elif os.path.isfile(os.path.join(os.getcwd(), "HiddenFiles", "credentials.txt")):
        logger.info("download training file")
        get_kaggle_data(train_url, get_credentials(), 'train_data.csv')
        logger.info("download test file")
        get_kaggle_data(test_url, get_credentials(), 'test_data.csv')
    else:
        logger.error("The credentials.txt file is missing, please add a credentials.txt file in the HiddenFiles folder as UserName,Password")
        sys.exit()
    return

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('hw2Logger')
    main()
    