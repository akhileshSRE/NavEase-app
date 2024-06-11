FROM python:alpine3.20

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]
