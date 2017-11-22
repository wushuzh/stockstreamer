FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

ADD ./wait-for-it.sh /usr/src/app
ADD ./project/data_fetcher.py /usr/src/app
ADD ./project/stockstreamer.py /usr/src/app

CMD python data_fetcher.py
