FROM python:slim-buster@sha256:e192c9d82785f103fcb27a62067784795fb0c3cb84ba2588577893cd7f6b7308

WORKDIR /usr/src/stibbons

RUN pip install --no-cache-dir pipenv

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv install

COPY . .

ENV STIBBONS_DB_PATH=/usr/src/stibbons/stibbons.db
ENTRYPOINT ["pipenv", "run", "./start-api.py"]
