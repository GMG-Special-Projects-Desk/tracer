import argparse
from tracer import Tracer
from slacker import Slacker
from dbserver import DbServer
import requests, json
from version import __version__
import dotenv
import logging, os

def parse_args():
        parser = argparse.ArgumentParser()

        parser.add_argument("--version",
                action='version',
                version="%(prog)s " + __version__)

        parser.add_argument("-c",
                dest="creds",
                action="store_true",
                help="Set credentials file")

        parser.add_argument("-d",
                dest="drop",
                action="store_true",
                help="drop table")

        parser.add_argument("-t",
                dest="test",
                action="store_true",
                help="test html parser")

        parser.add_argument("-b",
                dest="bot",
                action="store_true",
                help="slack bot")

        parser.add_argument("--quiet",
                action="store_true",
                help="Don't log progress to stderr.")


        args = parser.parse_args()
        return args

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
                    num_days = dotenv.get('NUM_DAYS') ,
                    db=db)

    slacker = Slacker(webhook=dotenv.get('SLACK_WEBHOOK'),
                      db=db)

    if args.drop:
        db.drop_table('cases')
    elif args.test:
        tracer.parse_test()
    elif args.bot:
        slacker.get_latest_counts()
    else:
        tracer.run()