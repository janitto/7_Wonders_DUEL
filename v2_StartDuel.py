import logging
import seven_wonders_utils

logging.basicConfig(filename='gamelog.log',
                    filemode='w',
                    format='%(levelname)s: %(funcName)s() at line %(lineno)d: %(message)s',
                    level=logging.DEBUG)

logging.info('Game started.')

prvy_vek = seven_wonders_utils.SevenWondersPrvyVek()

logging.info('Game ended.')