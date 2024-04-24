import logging
import time

from src.etl_app import ETL, JsonFileStorage



if __name__ == '__main__':
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(filename='logs.log',
                        level=logging.DEBUG,
                        filemode='a',
                        format='%(asctime)s %(levelname)s %(message)s')
    ETL(JsonFileStorage('JsonFileStorage.txt')).start()