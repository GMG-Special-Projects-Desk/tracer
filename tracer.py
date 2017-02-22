import requests
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
logger = logging.getLogger(__name__)


class Tracer(object):
    def __init__(self,
                 user,
                 password,
                 db,
                 num_days=1):
        self.session = requests.Session()
        self.login_url = 'https://pacer.login.uscourts.gov/csologin/login.jsf'
        self.search_url = 'https://pcl.uscourts.gov/dquery'
        self.num_days = num_days
        self.db = db

        if not user or not password:
            logger.error("Cant run Tracer with Pacer credentials.")
            return
        self.login_data = {
            'login': 'login',
            'login:loginName': user,
            'login:password': password,
            'login:clientCode': '',
            'login:fbtnLogin': '',
            'javax.faces.ViewState': 'stateless'
        }
        self.search_data = {
          'case_no': '',
          'mdl_id': '',
          'stitle': '',
          'date_filed_start': (datetime.now() - timedelta(days=num_days)).strftime('%m/%d/%Y'),
          'date_filed_end': datetime.now().strftime('%m/%d/%Y'),
          'date_term_start': '',
          'date_term_end': '',
          'date_dismiss_start': '',
          'date_dismiss_end': '',
          'date_discharge_start': '',
          'date_discharge_end': '',
          'party': '',
          'ssn4': '',
          'ssn': '',
          'show_title':'Yes',
          'court_type': 'all',
          'default_form': 'allb'
        }
        self.companies = ['facebook',
                          'trump',
                          'alphabet',
                          'google',
                          'palantir',
                          'washington post',
                          'wall street journal',
                          'new york times',
                          'glittering steel',
                          'steve bannon',
                          'breitbart news',
                          'American Vantage Media',
                          'jeffrey epstein',
                          'Affinity Media',
                          'Cambridge Analytica',
                          'SCL Group',
                          'Alexander Nix',
                          'Brittany Kaiser',
                          'cambridge analytica']

    def login(self):
        try:
            logger.info('Logging in to Pacer...')
            r = self.session.post(self.login_url,  data=self.login_data)
            if r.status_code == requests.codes.ok:
                logger.info("Successfully logged in")
            else:
                logger.error("Couldnt log in. Status Code: {}"
                             .format(r.status_code))
        except Exception as e:
            logger.error('Login failed: {}'.format(e))

    def search(self):
        for party_id, party in self.db.get_parties():
            try:
                # logger.info('Searching for {} cases for the past {} days'
                #             .format(c, self.num_days))

                self.search_data['party'] = party
                r = self.session.post(self.search_url, data=self.search_data)
                if r.status_code == requests.codes.ok:
                    logger.info("Searched for {}".format(party))
                    self.parse_html(r.text, party, party_id)
                    # with open('test.html', 'w') as outfile:
                    #   outfile.write(r.text)
                else:
                    logger.error("Couldnt search for {}. Status Code: {}"
                                 .format(c, r.status_code))
                    logger.error("Response Body: {}".format(r.text))
            except Exception as e:
                logger.error('Search failed: {}'.format(e))

    def run(self):
        self.login()
        self.search()

    def parse_test(self):
        with open('test.html') as infile:
            self.parse_html(infile, 'test')

    def parse_html(self, html, party, party_id):
            for_db = []
            soup = BeautifulSoup(html, 'html.parser')
            details = soup.find('div', {'id': 'details'})
            tables = details.findAll('table')

            for i, table in enumerate(tables):
                header = table.find('thead')
                table_name = header.text.strip()
                for row in table.findAll('tr'):
                    data = {}
                    data['search_query'] = party
                    data['p_id'] = party_id
                    data['case_type'] = table_name
                    data['line_no'] = self.get_col('line_no', row)
                    data['party_name'] = self.get_col('party_name', row)
                    data['case_id'] = self.get_col('case', row)
                    data['court'] = self.get_col('court_id', row)
                    data['disposition'] = self.get_col('disposition', row)

                    if data['case_id']:
                        data['case_url'], data['case_title'] = self.get_case_info(row)

                    if self.db.check_case_exists(data['case_id']) > 0:
                        logger.info('Skippping {}, already have it'.format(data['case_id']))
                        continue
                    if not data['disposition']:
                        data['disposition'] = None

                    if data['line_no']:
                        dates = row.findAll('td', {'class': 'cs_date'})
                        if len(dates) == 2:
                            data['date_filed'], data['date_closed'] = [d.text.strip()
                                                                       for d in dates]
                            data['date_filed'] = datetime.strptime(data['date_filed'], "%m/%d/%Y").date()

                            if not data['date_closed']:
                                data['date_closed'] = None
                            else:
                                data['date_closed'] = datetime.strptime(data['date_closed'], "%m/%d/%Y").date()

                            for_db.append(data)

                if for_db:
                    logger.info('Found {} cases. Adding to db'.format(len(for_db)))
                    self.db.add_cases(for_db)

    def get_case_info(self,row):
        case_col = row.find('td', {'class': 'case'})
        if not case_col:
            return '', ''
        else:
            for c in case_col.children:
                return c['href'], c['title']

    def get_col(self, col_name, row):
        return row.find('td', {'class': col_name}) \
                            .text.strip()\
                            if row.find('td', {'class': col_name}) else ''
