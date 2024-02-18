FROM python:3.10-slim-bullseye
RUN apt-get update && \
    apt-get upgrade -y
WORKDIR /usr/src
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]