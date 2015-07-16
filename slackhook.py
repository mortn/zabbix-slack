#!/usr/bin/env python

from sys import argv
import json
import requests
import logging as log

slack_hook_url = 'https://hooks.slack.com/services/your-slack-webhook-url-goes-here'
zabbix_host = 'https://zabbix.example.com'

# change log.DEBUG to log.INFO when in production = easier then removing the log.debug lines
log.basicConfig(level=log.DEBUG, filename='/var/log/zabbix-server/slackhook.log', 
    format='%(asctime)s %(levelname)s %(message)s')

class slackhook:
    def __init__(self):
        try:
            self.channel = argv[1] # @user or #channel
            self.status = argv[2] # OK or PROBLEM
            evtdata = argv[3] # JSON data
            self.data = json.loads(evtdata)
            self.send()
            exit(0)
        except Exception as e:
            log.error(e)
            log.error(argv[1:])
            exit(1)

    def send(self):
        d = self.data
        log.debug(d)
        color = 'good' if self.status == 'OK' else 'danger' 
        trigger = d['trigger']
        if not ' on ' in trigger: trigger = '{} on {}'.format(trigger,d['hostname'])
        # Strip out things we don't need to see with every alert
        trigger = trigger.replace('.example.com','')
        url = '{}/tr_events.php?triggerid={}&eventid={}'.format(zabbix_host, d['trigger_id'], d['event_id'])
        message = '{}\n{}'.format(trigger, url)
        #fields = [{ 'title': 'Actions', 'value': 'Value', 'short': False }]
        attachment = [{
            'color': color,
            'title': trigger,
            'title_link': url,
            'fallback': trigger,
        }]
        emoji=':smile:' # :frowning: :ghost:
        payload = {'channel': self.channel, 'username': 'Zabbix'}
        #payload['icon_emoji'] = emoji
        payload['attachments'] = attachment
        data = json.dumps(payload)
        log.info(data)
        r = requests.post(slack_hook_url, data=data, timeout=5)
        log.debug(r.text)
        log.debug(r.headers)

if __name__ == '__main__':
    try:
        exit(slackhook())
    except Exception as e:
        log.error(e)

