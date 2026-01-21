# Provide a default configured logger for BDD modules.
#
# Logger dumps all output to "$TOP/log/bdd.log" (or "%TEMP%/bdd.log for environment)
# and also echos log output to stdout so that it can be captured and dumped by the behave
# framework's stdout capture mechanisms when a test fails.
#
# The philosophy of logging for modules shared with SIT has not been discussed.
# Either SIT code should provide us a logger or else we create our own.
# For now, we create our own to keep interface to SIT simpler.  In the future
# it may be desired for SIT test code to provide a logger to the product
# test support modules.

try:
    # For product level BDD we will have Top.py defining DIR_TOP
    from Top import DIR_TOP
    DIR_LOG = DIR_TOP + '\\log'
    LOGFILE = DIR_LOG + '\\bdd.log'
    
except:
    # For logging we will just default to the current working directory as project 
    import os
    #DIR_LOG = os.environ['TEMP']
    DIR_LOG = os.getcwd()
    LOGFILE = DIR_LOG + '\\fuel-bdd.log'
    

import datetime
import logging
import logging.handlers
import sys
import os
import inspect
    

# For some reason just making a StreamHandler(sys.stdout) does not
# result in the stdout being captured in the same way it is captured
# when using this class.  At the end of the day, I want to always
# log my events to my file "jag-bdd.log" but allow behave to capture
# and display the log output to the terminal on failure.
class StdOutLoggerHandler(logging.StreamHandler):
    stdlogger = logging.getLogger()
    """
    A handler class which prints records to stdout
    """
    on_same_line = False
    def emit(self, record):
        msg = self.format(record)
        stream = self.stream
        sys.stdout.write(msg)
        sys.stdout.write("\n")
        self.flush()
        pass
#          01234567890123456789012345
_lvlstr = '| | | | | | | | | | | | | '

class LevelAdapter(logging.LoggerAdapter):
    def __init__(self, logger):
        super().__init__(logger, {})
        self.level = 0
        self.creation_datetime = datetime.datetime.now()

    def process(self, msg, kwargs):
        if self.level > 0:
            prefix = _lvlstr[25-(self.level*2):]
        else:
            prefix = ''
        
        if True:
            if len(msg) > 0:
                fncaller = inspect.stack()[3].function + '():'
            else:
                fncaller = ''
            return '%s%s %s' % (prefix, fncaller, msg), kwargs
        else:
            return '%s%s' % (prefix, msg), kwargs

    def adjust_level(self, level):
        self.level = self.level + level


def _get_bdd_logger():

    print('===bdd_logging.py: Creating BDD logger=== at ' + LOGFILE)
    
    try:
        if os.path.exists(LOGFILE):
            os.remove(LOGFILE)
    except Exception as e:
        pass   
    
    handler = logging.handlers.RotatingFileHandler(
        LOGFILE, maxBytes=(1048576*5), backupCount=7
    )
    
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)5s: %(message)s',
                                  datefmt='%y%m%d %H:%M:%S')
    
    handler.setFormatter(formatter)
    
    _logger = logging.getLogger("BDD")
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(handler)
    _logger.debug("===bdd_logging.py: created basic logger for bdd.log===")
    
    stdout_handler = StdOutLoggerHandler()
    stdout_handler.setFormatter(
        logging.Formatter(fmt='%(asctime)s %(levelname)5s: %(message)s',
                          datefmt='%H:%M:%S'))
    _logger.addHandler(stdout_handler)
    
    logger = LevelAdapter(_logger)

    return logger


logger = _get_bdd_logger()

