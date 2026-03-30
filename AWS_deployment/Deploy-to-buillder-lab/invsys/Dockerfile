FROM python:3.10
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "api:app"]
