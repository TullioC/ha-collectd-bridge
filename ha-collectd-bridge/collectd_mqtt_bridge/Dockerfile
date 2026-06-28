FROM python:3.12-alpine

RUN pip install paho-mqtt

COPY bridge.py bridge.py
COPY run.sh run.sh

RUN chmod a+x run.sh

CMD ["run.sh"]
