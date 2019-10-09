FROM python:3.7

EXPOSE 5000

ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

CMD sh -c "source .env"

CMD python -m flask run -h 0.0.0.0