FROM python:3.6

RUN apt-get update && apt-get install -y

WORKDIR /usr/src/app

#Only temporarily use this, test final with the remote
RUN git clone https://github.com/john-grando/hw2.git /usr/src/app/hw2
WORKDIR /usr/src/app/hw2
#temporary, commit to master on submission
RUN git checkout working
COPY requirements.txt ./
#Required credential file, if it's missing then continue and just let the program spit out the error
COPY HiddenFiles/credentials.txt ./HiddenFiles/credentials.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python /usr/src/app/hw2/pull_data.py
RUN python /usr/src/app/hw2/train_model.py
RUN python /usr/src/app/hw2/score_model.py
RUN git add .
RUN git commit -m "auto commit on `date +'%Y-%m-%d %H:%M:%S'`"
RUN git push origin working
