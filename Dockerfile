FROM python:slim

WORKDIR /usr/src/app

RUN useradd -m bot
USER bot

RUN pip install --upgrade pip && \
pip install "ts3>=2.0.0b2" --upgrade &&\
pip install urllib3

COPY . .

CMD [ "python", "./__init__.py" ]

