FROM python:3
WORKDIR .
COPY ./src .
ENV BASE_URL=https://mail.example.com/api/v1/get/
ENV API_KEY=YOUR-API-KEY-HERE
ENV PORT=9999
ENV SCRAPE_INTERVAL=5

RUN pip3 install prometheus_client
RUN pip3 install twisted
RUN pip3 install requests

CMD ["main.py"]
ENTRYPOINT ["python3"]
