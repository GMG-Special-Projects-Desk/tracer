import requests
import sys
import logging
import json

logger = logging.getLogger(__name__)


class Slacker:
    def __init__(self,
                 webhook,
                 db):
        self.webhook = webhook
        self.db = db

    def get_latest_counts(self, days=1):
        try:
            counts = self.db.get_cases_count_from(days=days)
            if counts:
                lines = ["{}: {} cases".format(c[1].capitalize(),
                                                                  c[0])
                         for c in counts]

                text = "\n".join(lines)
                text += '\n _Use `/tracer` for more info._'
                self.send(text)
            else:
                logger.info('No new cases found')

        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            logger.error("Error: {} Line No: {}".format(e, exc_tb.tb_lineno))

    def send(self, text):
        payload = {'text': text}
        r = requests.post(self.webhook,  data=json.dumps(payload))
        if r.status_code == requests.codes.ok:
            logger.info("posted to slack".format(text))
        else:
            logger.error("Response Body: {}".format(r.text))
