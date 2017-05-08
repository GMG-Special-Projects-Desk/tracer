import argparse
from tracer import Tracer
from slacker import Slacker
from dbserver import DbServer
from version import __version__
from settings import *
import logging
import linecache
import sys

def PrintException(logging):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    logging.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


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
    logFormat = '%(asctime)s [%(levelname)s] [ %(name)s ] : %(message)s'
    formatter = logging.Formatter(fmt=logFormat, datefmt="%Y-%m-%d %H:%M:%S")

    logging.basicConfig(level=(logging.WARN if args.quiet else logging.INFO),
                        format=logFormat,
                        filename=LOG_FILE,
                        filemode= 'w',
                        datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    console.setLevel(logging.WARN if args.quiet else logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    try:
        db = DbServer(DB_URL)
        tracer = Tracer(user=PACER_USER,
                        password=PACER_PASS,
                        num_days=NUM_DAYS,
                        db=db)

        slacker = Slacker(webhook=SLACK_WEBHOOK,
                            db=db)
        if args.drop:
                db.delete_all_cases()
                db.drop_tables()
        elif args.test:
            tracer.parse_test()
        elif args.bot:
                slacker.get_latest_counts(days=10)
        elif args.all:
                tracer.run()
                slacker.get_latest_counts()
        elif args.people:
                [db.add_party(c) for c in INTITAL_PARTIES]
        else:
            tracer.run()
            slacker.get_latest_counts()

    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        logging.error(e)
        PrintException(logging)

