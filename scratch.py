import requests

session = requests.Session()

login_url = 'https://pacer.login.uscourts.gov/csologin/login.jsf'
data = {
  'login': 'login',
  'login:loginName': 'Gmg10011',
  'login:password': '114-Fifth',
  'login:clientCode': '',
  'login:fbtnLogin': '',
  'javax.faces.ViewState': 'stateless'
}

r = session.post(login_url,  data=data)

data = {
  'case_no': '',
  'mdl_id': '',
  'stitle': '',
  'date_filed_start': '01/01/2017',
  'date_filed_end': '02/14/2017',
  'date_term_start': '',
  'date_term_end': '',
  'date_dismiss_start': '',
  'date_dismiss_end': '',
  'date_discharge_start': '',
  'date_discharge_end': '',
  'party': 'facebook',
  'ssn4': '',
  'ssn': '',
  'court_type': 'all',
  'default_form': 'b'
}

r = session.post('https://pcl.uscourts.gov/dquery',  data=data)

print(r.text)

#
# cookies = {
#     'PacerSession': 'Ro87tLtamcP54jZC6DtjxU2iaT8lgcbyotYnN4XiSoSOY7bCuiEAGS90yhjD5oET0BTXCXx8D8GsA1v0AZhHiPF7uowaVeW2XyqvQfhr5HJ7go0JQc1Lv6Zrr1uzx1sV',
#     'NextGenCSO': 'Ro87tLtamcP54jZC6DtjxU2iaT8lgcbyotYnN4XiSoSOY7bCuiEAGS90yhjD5oET0BTXCXx8D8GsA1v0AZhHiPF7uowaVeW2XyqvQfhr5HJ7go0JQc1Lv6Zrr1uzx1sV',
#     'PacerClientCode': '',
#     'ClientValidation': '',
#     'ClientCodeDescription': '',
#     'PacerClient': '',
#     'ClientDesc': '',
#     'PacerPref': 'receipt=Y',
#     'default_form': 'b',
# }

# headers = {
#     'Pragma': 'no-cache',
#     'Origin': 'https://pcl.uscourts.gov',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'en-US,en;q=0.8',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'Cache-Control': 'no-cache',
#     'Referer': 'https://pcl.uscourts.gov/search',
#     'Connection': 'keep-alive',
#     'DNT': '1',
# }

# data = {
#   'case_no': '',
#   'mdl_id': '',
#   'stitle': '',
#   'date_filed_start': '01/01/2017',
#   'date_filed_end': '02/14/2017',
#   'date_term_start': '',
#   'date_term_end': '',
#   'date_dismiss_start': '',
#   'date_dismiss_end': '',
#   'date_discharge_start': '',
#   'date_discharge_end': '',
#   'party': 'facebook',
#   'ssn4': '',
#   'ssn': '',
#   'court_type': 'all',
#   'default_form': 'b'
# }

# requests.post('https://pcl.uscourts.gov/dquery', headers=headers, cookies=cookies, data=data)