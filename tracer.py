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
        headers = {
            'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        self.session.headers.update(headers)
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
        self.post_headers = {
            'Pragma': 'no-cache',
            'Origin': 'https://pcl.uscourts.gov',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Referer': 'https://pcl.uscourts.gov/search',
            'Connection': 'keep-alive',
            'DNT': '1',
        }

    def login(self):
        try:
            logger.info('Logging in to Pacer...')
            r = self.session.post(self.login_url,  data=self.login_data)
            if r.status_code == requests.codes.ok:
                with open('login.html', 'w') as outfile:
                  outfile.write(r.text)
                logger.info("Successfully logged in")
                logger.info("Searching for cases filed between {} and {}"
                            .format(self.search_data['date_filed_start'], self.search_data['date_filed_end']))
            else:
                logger.error("Couldnt log in. Status Code: {}"
                             .format(r.status_code))
        except Exception as e:
            logger.error('Login failed: {}'.format(e))

    def search(self):
        if len(self.db.get_parties()) == 0:
          logger.error("No parties to search for in db. Quitting.")
          return

        for party_id, party in self.db.get_parties():
            variations = self.get_variations(party)
            for party_variation in variations:
                try:
                    self.search_data['party'] = party_variation
                    self.session.headers.update(self.post_headers)
                    r = self.session.post(self.search_url, data=self.search_data, allow_redirects=True )
                    if r.status_code == requests.codes.ok:
                        logger.info("Searched for {}".format(party_variation))
                        # with open('test.html', 'w') as outfile:
                        #   outfile.write(r.text)
                        self.parse_html(r.text, party, party_id)
                    else:
                        logger.error("Couldnt search for {}. Status Code: {}"
                                     .format(party_variation, r.status_code))
                        logger.error("Response Body: {}".format(r.text))
                except Exception as e:
                    logger.error('Search failed: {}'.format(e))
    def get_variations(self, party):
        tokens = party.split(' ')
        if len(tokens) == 2:
            alt = " ".join([tokens[1],tokens[0]])
            return [party, alt]
        else:
            pass
            return [party]
            # Add this later when we have people with a middle name in the list
            # last = tokens[-1]
            # first = " ".join(tokens[:-1])
            # alt = " " .join([last, first])

# application/x-www-form-urlencoded
    def run(self):
        self.login()
        self.search()

    def parse_test(self):
        self.login()
        with open('test.html') as infile:
            self.search()

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

                    print(party)
                    print(data['party_name'])

                    if data['case_id']:
                        data['case_url'], data['case_title'] = self.get_case_info(row)

                    if self.db.check_case_exists(data['case_id'], data['court']) > 0:
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
