FROM python:3.9-alpine

WORKDIR /app
COPY . .

# flask default port
EXPOSE 5000

RUN pip install -r requirements.txt
# --port=5000
CMD [ "flask", "run", "--host=0.0.0.0" ]