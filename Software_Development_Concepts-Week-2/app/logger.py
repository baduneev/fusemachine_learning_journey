# app/logger.py
# यो file logging setup गर्न प्रयोग हुन्छ
# Logging = app मा के भइरहेको छ भनेर record राख्ने process


# Python को built-in logging module import gareko
# यो module ले info, warning, error, debug logs store/print गर्न help गर्छ
import logging


# Logging को basic configuration setup gareko
# यसले log कहाँ save गर्ने, कुन level ko log save गर्ने, र format कस्तो हुने define गर्छ
logging.basicConfig(

    # Logs save हुने file name
    # app.log file project भित्र create हुन्छ
    filename="app.log",

    # कुन level सम्मका logs record गर्ने भनेर define गर्छ
    # INFO means info, warning, error, critical सबै log हुन्छन्
    level=logging.INFO,

    # Log message को format define gareko
    # asctime   -> log आएको date/time
    # levelname -> log level, e.g. INFO, ERROR
    # message   -> actual log message
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# logger object create gareko
# __name__ means current file/module को name use हुन्छ
# यो logger use गरेर पछि logger.info(), logger.error() etc. लेख्न सकिन्छ
logger = logging.getLogger(__name__)