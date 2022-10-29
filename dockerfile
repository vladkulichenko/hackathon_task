FROM python:3.10-alpine

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "main_script.py"]