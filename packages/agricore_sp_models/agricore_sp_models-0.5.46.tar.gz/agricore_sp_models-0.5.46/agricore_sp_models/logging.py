from __future__ import annotations
from loguru import logger
from .simulation_models import LogLevel, LogMessage
from time import time
from urllib.parse import urljoin
import json
import requests

class ORMLogHandler:
    def __init__(self, base_path: str = "https://abm.agricore.idener.es/"):
        self.base_path = base_path
        self.headers = {'Accept': 'text/plain', 'Content-Type': 'application/json'}
        
    def write(self, message):
        try:
            log = LogMessage(
                description="" if message.record["exception"] is None else str(message.record["exception"]),
                logLevel=int(message.record["level"].no),
                simulationRunId=0 if "simulationRunId" not in message.record["extra"] else message.record["extra"]["simulationRunId"],
                source="" if "logSource" not in message.record["extra"] else message.record["extra"]["logSource"],
                timestamp=float(time() * 1000),
                title=message.record["message"],
            )
            url = urljoin(self.base_path, f"/simulationRun/{log.simulationRunId}/logMessage/add")
            x = requests.post(url, json.dumps(log.dict(exclude={"id"})), headers= self.headers)
            if x.status_code == 415:
                logger.debug(f"The log message could not be added to the ORM. Object sent: {log.dict()}") 
                     
        except Exception as e:
            print("Unable to generate Log Message in ORM for message. " + str(e) )
            if log is not None:
                print (log.dict())
                
def check_orm_log(record):
    if "simulationRunId" in record["extra"] and "logSource" in record["extra"]:
        return True
    else:
        return False

def configure_orm_logger(url: str, enqueue: bool = True) -> None:
    logger.configure(handlers=[{"sink": ORMLogHandler(url), "filter": check_orm_log, "enqueue": enqueue}])
    
    