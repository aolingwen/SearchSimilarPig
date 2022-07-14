#coding:utf8

import uvicorn
from fastapi import FastAPI, logger
from dataloader import DataLoader
from logger import Logger
from config import *
from search_engine import *
from search_engine import SearchEngine
from pydantic import BaseModel


log = Logger(LOG_PATH)
se = SearchEngine(log)
app = FastAPI()


class DateData(BaseModel):
    StartDate: str
    EndDate: str


class LicenseNoData(BaseModel):
    LicenseNo: str


@app.post('/getSimilarLicenseNo')
async def getSimilarLicenseNo(data: LicenseNoData):
    try:
        log.debug("---------------begin getSimilarLicenseNo-------------------")
        licenseNo = data.LicenseNo
        result = se.search(licenseNo)
        log.debug("---------------end getSimilarLicenseNo-------------------")
        result['status'] = 'success'
        return result
    except Exception as e:
        log.error(traceback.format_exc())
        result = {'status':'failed','result':[]}
        log.debug("---------------end getSimilarLicenseNo-------------------")
        return result


@app.post('/addDataToIndex')
async def addDataToIndex(data: DateData):
    try:
        log.debug("---------------begin addDataToIndex-------------------")
        start_date = data.StartDate
        end_date = data.EndDate
        result = se.add_data(start_date, end_date)
        log.debug("---------------end addDataToIndex-------------------")
        result['status'] = 'success'
        return result
    except Exception as e:
        log.error(traceback.format_exc())
        result = {'status': 'failed', 'count':0}
        log.debug("---------------end addDataToIndex-------------------")
        return result

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=39999, reload=False, log_config=LOGGING_CONFIG)

















