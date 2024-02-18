import logging


logger = logging.getLogger("staircase")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("staircase.log")
fileHandler.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]\n%(message)s")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
