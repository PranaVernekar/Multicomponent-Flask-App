FROM python:3.10
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5001
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "application:app"]
