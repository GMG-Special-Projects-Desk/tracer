from os.path import join, dirname
import dotenv

dotenv_path = join(dirname(__file__), '.env')
dotenv.load()

LOG_FILE = join(dirname(__file__), 'tracer.log')
PACER_USER = dotenv.get('PACER_USER')
PACER_PASS = dotenv.get('PACER_PASS')
NUM_DAYS = dotenv.get('NUM_DAYS')
SLACK_WEBHOOK = dotenv.get('SLACK_WEBHOOK')
DB_URL = dotenv.get('DB_URL')

INTITAL_PARTIES = ['Facebook',
                   'Trump',
                   'Alphabet',
                   'Google',
                   'Palantir',
                   'Washington Post',
                   'Wall Street journal',
                   'New York Times',
                   'Glittering Steel',
                   'Steve Bannon',
                   'Breitbart News',
                   'American Vantage Media',
                   'Jeffrey Epstein',
                   'Affinity Media',
                   'Cambridge Analytica',
                   'SCL Group',
                   'Alexander Nix',
                   'Brittany Kaiser',
                   'Cambridge Analytica']
