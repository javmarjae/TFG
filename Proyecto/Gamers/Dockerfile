FROM python:3.9

WORKDIR /app/Gamers

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app/Gamers/

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000