FROM python:3.6

RUN apt-get update && apt-get install -y

WORKDIR /usr/src/app
RUN git clone https://github.com/john-grando/data622-hw3-files.git /usr/src/app/hw2
WORKDIR /usr/src/app/hw2
#Temporary step for local testing, commented out for final submission.
#COPY requirements.txt ./
#Required credential file that can optionally be copied in, if it's missing then continue and just let the program spit out the error
#COPY HiddenFiles/credentials.txt ./HiddenFiles/credentials.txt
RUN pip install --no-cache-dir -r requirements.txt
#RUN python /usr/src/app/hw2/pull_data.py
#RUN python /usr/src/app/hw2/train_model.py
#RUN python /usr/src/app/hw2/score_model.py
