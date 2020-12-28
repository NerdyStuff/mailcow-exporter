# Mailcow-Exporter
Prometheus exporter for mailcow containers

This is a simple prometheus exporter for [mailcow dockerized](https://github.com/mailcow/mailcow-dockerized) written in python.
The code uses the Prometheus_Client library for python. See [this](https://github.com/prometheus/client_python) for more details.

## Getting started
To use the exporter you have to enable the mailcow API and generate an API-key.
After generating the key you have to set the environment variables for the API-URL and the API-key:

`export API_KEY="<YOUR-API-KEY>"`<br>
`export BASE_URL="<https://mail.example.com/api/v1/get/>"`

Install the needed python libraries using pip:
```
pip install prometheus_client
pip install requests
```

or use pip3:
```
pip3 install prometheus_client
pip3 install requests
```

## Environment Variables
```
API_KEY="<YOUR-API-KEY>"
BASE_URL="<https://YOUR.DOMAIN.com/api/v1/get/>"
PORT=1234
SCRAPE_INTERVAL=10
```
Use the `PORT` environment variable to change the default port `9999` to an other port.
The `SCRAPE_INTERVAL` variable is used to set the time between the data collections from API. The default interval is 1800 seconds.

Note: The `SCARPE_INTERVAL` uses seconds as input! 

## Docker
Use the `Dockerfile` to create a docker container.
Therefore clone the repository and change the environment variables in the Dockerfile

