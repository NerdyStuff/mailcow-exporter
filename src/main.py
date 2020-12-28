import os
import sys
import requests
import json
from prometheus_client import Gauge, Summary, Counter, start_http_server
import time

"""
This is a simple server to process metrics from mailcow's API.
The collected data is provided in prometheus readable data format.

For running the code you have to set the API_KEY environment variable (API key from Mailcow)
Also you have to set the BASE_URL environment variable in format <protocol>://<DOMAIN>/api/v1/get/
E.g. https://mail.example.com/api/v1/get/

Author: Marcel Mertens
"""

# Handle Environment variables
API_KEY = os.getenv('API_KEY') # API Key
if API_KEY == None:
    sys.exit("Error: API key not set!")

PORT = 9999
envPort = os.getenv('PORT') # PORT
if envPort != None:
    PORT = int(envPort)

SCRAPE_INTERVAL = 1800
envScrapeInterval = os.getenv('SCRAPE_INTERVAL') # SCRAPE_INTERVAL
if envScrapeInterval != None:
    SCRAPE_INTERVAL = int(envScrapeInterval)

BASE_URL = os.getenv('BASE_URL') # BASE_URL
if BASE_URL == None:
    sys.exit("Error: BASE_URL not set!")


# Call API and return data as dict
def getInfo(reqUrl):
    url = BASE_URL + reqUrl
    payload = {}
    headers = {'X-API-Key': API_KEY}
    
    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)

# Calculate bytes from given strings
def calcBytes(input):
    if 'KB' in input or 'kb' in input:
        return int(float(input[:-2]) * 1000)
    elif 'MB' in input or 'mb' in input:
        return int(float(input[:-2]) * 1000000)
    elif 'GB' in input or 'gb' in input:
        return int(float(input[:-2]) * 1000000000)
    elif 'TB' in input or 'tb' in input:
        return int(float(input[:-2]) * 1000000000000)
    elif 'B' in input or 'b' in input:
        return int(input[:-1])
    if 'K' in input or 'k' in input:
        return int(float(input[:-1]) * 1000)
    elif 'M' in input or 'm' in input:
        return int(float(input[:-1]) * 1000000)
    elif 'G' in input or 'g' in input:
        return int(float(input[:-1]) * 1000000000)
    elif 'T' in input or 't' in input:
        return int(float(input[:-1]) * 1000000000000)
    else:
        return -1

# Make number from string
def stateToNumber(state):
    if (state.lower()) == 'running':
        return 1
    else:
        return 0

# Set state of containers
def getContainerStatus(infos):
    for container in infos:
        if 'rspamd' in container:
            containerRspamdUp.set(stateToNumber(infos[container]['state']))
        elif 'netfilter' in container:
            containerNetfilterUp.set(stateToNumber(infos[container]['state']))
        elif 'postfix' in container:
            containerPostfixUp.set(stateToNumber(infos[container]['state']))
        elif 'dovecot' in container:
            containerDovecotUp.set(stateToNumber(infos[container]['state']))
        elif 'mysql' in container:
            containerMysqlUp.set(stateToNumber(infos[container]['state']))
        elif 'acme' in container:
            containerAcmeUp.set(stateToNumber(infos[container]['state']))
        elif 'nginx' in container:
            containerNginxUp.set(stateToNumber(infos[container]['state']))
        elif 'php' in container:
            containerPhpFpmUp.set(stateToNumber(infos[container]['state']))
        elif 'solr' in container:
            containerSolrUp.set(stateToNumber(infos[container]['state']))
        elif 'api' in container:
            containerApiUp.set(stateToNumber(infos[container]['state']))
        elif 'olefy' in container:
            containerOlefyUp.set(stateToNumber(infos[container]['state']))
        elif 'clamd' in container:
            containerClamdUp.set(stateToNumber(infos[container]['state']))
        elif 'redis' in container:
            containerRedisUp.set(stateToNumber(infos[container]['state']))
        elif 'watchdog' in container:
            containerWatchdogUp.set(stateToNumber(infos[container]['state']))
        elif 'sogo' in container:
            containerSogoUp.set(stateToNumber(infos[container]['state']))
        elif 'memcached' in container:
            containerMemcachedUp.set(stateToNumber(infos[container]['state']))
        elif 'unbound' in container:
            containerUnboundUp.set(stateToNumber(infos[container]['state']))

# Count number of mails from all mailboxes
def getTotalNumberOfMails(infos):
    numberMails = 0
    for mailbox in infos:
        if 'messages' in mailbox:
            numberMails += int(mailbox['messages'])
    return numberMails

# Collect data from API
def collectData():
    containerInfos = getInfo("status/containers")
    getContainerStatus(containerInfos)

    # Vmail
    vmailInfos = getInfo("status/vmail")
    if 'used_percent' in vmailInfos: 
        vmStoragePercent.set(vmailInfos['used_percent'][:-1])
    if 'total' in vmailInfos:
        vmStorageTotal.set(calcBytes(vmailInfos['total']))
    if 'used' in vmailInfos:
        vmStorageUsed.set(calcBytes(vmailInfos['used']))

    # Solr
    solrInfos = getInfo("status/solr")
    if 'solr_documents' in solrInfos:
        solrNumberDocuments.set(solrInfos['solr_documents'])
    if 'solr_size' in solrInfos:
        solrSize.set(calcBytes(solrInfos['solr_size']))


    # TODO Add more data
    # Mailboxes
    mailboxInfos = getInfo("mailbox/all")
    mbNumberMailboxes.set(len(mailboxInfos))
    mbNumberMails.set(getTotalNumberOfMails(mailboxInfos))

    # TODO Add more data
    # Aliases
    aliasInfos = getInfo("alias/all")
    alNumberAliases.set(len(aliasInfos))

    # TODO Add data
    # Mail queue
    queueInfos = getInfo("mailq/all")
    mqNumberMails.set(len(queueInfos))

    # TODO Add data
    # Quarantined mails
    quarantineInfos = getInfo("quarantine/all")
    qtNumberMails.set(len(quarantineInfos))

    # TODO Add data
    # Sync Jobs
    syncJobInfos = getInfo("syncjobs/all/no_log")
    sjNumberJobs.set(len(syncJobInfos))

    # TODO Add data
    domainsInfos = getInfo("domain/all")
    dmNumberDomains.set(len(domainsInfos))

    # TODO Add data
    forwardingHostsInfos = getInfo("fwdhost/all")
    fwdNumberForwardingHosts.set(len(forwardingHostsInfos))


# Generate metric names and descriptions
vmStoragePercent = Gauge('mailcow_vmail_used_storage_percent', 'Shows the used storage from vmail in percent')
vmStorageTotal = Gauge('mailcow_vmail_available_storage_bytes', 'Shows the available storage for vmail in bytes')
vmStorageUsed = Gauge('mailcow_vmail_used_storage_bytes', 'Shows the used storage for vmail in bytes')
solrNumberDocuments = Gauge('mailcow_solr_documents_total', 'Total number of solr documents')
solrSize = Gauge('mailcow_solr_size_bytes', 'Size of solr in bytes')
mbNumberMailboxes = Gauge('mailcow_mailboxes_total', 'Total number of mailboxes')
mbNumberMails = Gauge('mailcow_mailboxes_messages_total', 'Total number of messages')
alNumberAliases = Gauge('mailcow_aliases_total', 'Total number of aliases')
mqNumberMails = Gauge('mailcow_mailqueue_mails_total', 'Total number of mails in mail queue')
qtNumberMails = Gauge('mailcow_quarantine_mails_total', 'Total number of mails in quarantine')
sjNumberJobs = Gauge('mailcow_sync_jobs_total', 'Total number of sync jobs')
dmNumberDomains = Gauge('mailcow_domains_total', 'Total number of domains')
fwdNumberForwardingHosts = Gauge('mailcow_forwarding_hosts_total', 'Total number of forwarding hosts')
# Containers up
containerRspamdUp = Gauge('mailcow_container_rspamd_up', 'Shows if rspamd container is up')
containerNetfilterUp = Gauge('mailcow_container_netfilter_up', 'Shows if netfilter container is up')
containerPostfixUp = Gauge('mailcow_container_postfix_up', 'Shows if postfix container is up')
containerDovecotUp = Gauge('mailcow_container_dovecot_up', 'Shows if dovecot container is up')
containerMysqlUp = Gauge('mailcow_container_mysql_up', 'Shows if mysql container is up')
containerAcmeUp = Gauge('mailcow_container_acme_up', 'Shows if acme container is up')
containerNginxUp = Gauge('mailcow_container_nginx_up', 'Shows if nginx container is up')
containerPhpFpmUp = Gauge('mailcow_container_php_fpm_up', 'Shows if php fpm container is up')
containerSolrUp = Gauge('mailcow_container_solr_up', 'Shows if solr container is up')
containerApiUp = Gauge('mailcow_container_api_up', 'Shows if api container is up')
containerOlefyUp = Gauge('mailcow_container_olefy_up', 'Shows if olefy container is up')
containerClamdUp = Gauge('mailcow_container_clamd_up', 'Shows if clamd container is up')
containerRedisUp = Gauge('mailcow_container_redis_up', 'Shows if redis container is up')
containerWatchdogUp = Gauge('mailcow_container_watchdog_up', 'Shows if watchdog container is up')
containerSogoUp = Gauge('mailcow_container_sogo_up', 'Shows if sogo container is up')
containerMemcachedUp = Gauge('mailcow_container_memcached_up', 'Shows if memcached container is up')
containerUnboundUp = Gauge('mailcow_container_unbound_up', 'Shows if unbound container is up')

# MAIN PART
print("Starting Mailcow Exporter")
start_http_server(PORT)
print("Mailcow Exporter started\nServer listening on port", PORT)

while True:
    collectData()
    time.sleep(SCRAPE_INTERVAL)
