#DATA 622 Homework 2 - pull_data.py
#John Grando
# -*- coding: utf-8 -*-

import requests, os, sys, logging, logging.config, tempfile, boto3
import pandas as pd
from botocore.client import ClientError

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

def get_or_instantiate_bucket(s3, bucket):
    """
    Check if s3 bucket exists.  If not, then create it.
    """
    try:
        s3.meta.client.head_bucket(Bucket=bucket)
        logger.info('%s bucket exists', bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket)
        logger.info('%s bucket created', bucket)
    return

def upload_csv_file_s3(s3_r, bucket, key, file):
    """
    Check if train/test csv file exists.  If not, then get files and upload to s3 bucket
    """
    try:
        print(str(file.name), "-----")
        s3_r.upload_file(str(file.name), bucket, key)
    except ClientError:
        logger.info("%s file could not be uploaded", key)
        sys.exit(1)
    return

def get_kaggle_data(s3_r, url, payload, file_name, bucket=None):
    """
    Get CSV files from kaggle and upload to s3
    """
    temp = tempfile.NamedTemporaryFile()
    try:
        payload = get_credentials()
        #I had mulitple issues with the standard method of importing files 
        #and this was the only answer that worked for me
        #https://stackoverflow.com/questions/50863516/issue-in-extracting-titanic-training-data-from-kaggle-using-jupyter-notebook
        try:
            with requests.Session() as c:
                response = c.get(loginURL).text
                AFToken = response[response.index('antiForgeryToken')+19:response.index('isAnonymous: ')-12]
                payload['__RequestVerificationToken']=AFToken
                c.post(loginURL + "?isModal=true&returnUrl=/", data=payload)
                response = c.get(url)
            for chunk in response.iter_content(chunk_size = 512 * 1024):
                if chunk: 
                    temp.write(chunk)    
            #reset tempfile
            temp.seek(0)
        except:
            logger.error("There was an error downloading the file")
            sys.exit(1)
        t_df = pd.read_csv(temp)
        if t_df.empty == True:
            logger.error("The CSV file appears to be empty")
            sys.exit(1)
        upload_csv_file_s3(s3_r, bucket, file_name, temp)
    except:
        logger.error("There was an error testing the csv file")
        sys.exit(1)

    return

def main():
    """
    Get training and test files from the titanic dataset at kaggle.com
    """
    #instantiate aws
    if len(sys.argv)>1:
        print("a")
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
        logger.info("files already uploaded to s3, nothing is overwritten")
    except:
        #Test if bucket exists
        get_or_instantiate_bucket(s3, bucket)
        logger.info("download training file")
        get_kaggle_data(s3_r, train_url, get_credentials(), 'train_data.csv', bucket)
        logger.info("download test file")
        get_kaggle_data(s3_r, test_url, get_credentials(), 'test_data.csv', bucket)
    return

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('hw2Logger')
    main()
    