FROM python:alpine3.20

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir  -r requirements.txt

COPY . .
EXPOSE 8080

ENV FLASK_APP run.py
ENV FLASK_ENV production

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
