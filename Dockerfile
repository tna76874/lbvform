FROM python:3.9

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update

COPY requirements.txt /app/requirements.txt
RUN pip install pipreqs && pip install -r requirements.txt && chmod -R +x /app

COPY app.py /app/app.py
COPY lbvform /app/lbvform
COPY templates /app/templates
COPY static /app/static
COPY example /app/example
RUN chmod -R +x /app

EXPOSE 5000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["sh", "-c", "/app/entrypoint.sh"]