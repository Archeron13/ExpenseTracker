FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /ExpenseTracker

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /ExpenseTracker

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
