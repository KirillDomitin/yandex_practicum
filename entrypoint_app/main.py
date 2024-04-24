import logging
import time

from src.sqlite_to_postgresql import load_data



if __name__ == '__main__':
    file_name = __file__.split('.')[0]
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(filename='logs.log',
                        level=logging.DEBUG,
                        filemode='a',
                        format='%(asctime)s %(levelname)s %(message)s')
    load_data()
    logging.info("___________________THE END___________________")