import argparse
from tracer import Tracer
from slacker import Slacker
from dbserver import DbServer
from version import __version__
import dotenv
import logging


def parse_args():
        parser = argparse.ArgumentParser()

        parser.add_argument("--version",
                            action='version',
                            version="%(prog)s " + __version__)

        parser.add_argument("-d",
                            dest="drop",
                            action="store_true",
                            help="drop table")

        parser.add_argument("-t",
                            dest="test",
                            action="store_true",
                            help="test html parser")

        parser.add_argument("-p",
                            dest="people",
                            action="store_true",
                            help="add people")

        parser.add_argument("-b",
                            dest="bot",
                            action="store_true",
                            help="slack bot")

        parser.add_argument("-x",
                            dest="all",
                            action="store_true",
                            help="scrape and post")

        parser.add_argument("--quiet",
                            action="store_true",
                            help="Don't log progress to stderr.")
        return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()
    dotenv.load()
    logFormat = '%(asctime)s [%(levelname)s] [ %(name)s ] : %(message)s'

    logging.basicConfig(
            level=(logging.WARN if args.quiet else logging.INFO),
            format=logFormat,
            datefmt="%Y-%m-%d %H:%M:%S")

    db = DbServer(dotenv.get('DB_URL'))

    tracer = Tracer(user=dotenv.get('PACER_USER'),
                    password=dotenv.get('PACER_PASS'),
                    num_days=dotenv.get('NUM_DAYS'),
                    db=db)

    slacker = Slacker(webhook=dotenv.get('SLACK_WEBHOOK'),
                      db=db)

    if args.drop:
        # db.drop_table('cases')
        db.drop_table()
    elif args.test:
        # tracer.parse_test()
        print(db.get_parties())
    elif args.bot:
        slacker.get_latest_counts()
    elif args.all:
        tracer.run()
        slacker.get_latest_counts()
    elif args.people:
        companies = ['facebook',
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
        [db.add_party(c) for c in companies]
    else:
        tracer.run()
