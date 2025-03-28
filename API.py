import uvicorn
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from Utils.Schemas import VAL_INSERT
from Utils.Logger import createLogger, sessionIDVar

from Services.IMSAgent import IMSAgent
from Services.DBAgent import DBAgent

app = FastAPI()

# Logger
logger = createLogger()
logger.info("API's logger is warm...")

# IMS Agent: Packaging Payload
imsAgent = IMSAgent()
logger.info("IMSAgent is warm...")

# DB Agent: Sending Payload
dbAgent = DBAgent()
logger.info("DBAgent is warm...")


# Middleware: Session ID Injection
@app.middleware("http")
async def session_tracking_middleware(request: Request, call_next):
    sessionID = str(uuid4())
    sessionIDVar.set(sessionID)
    request.state.session_id = sessionID
    logger.info("Handling new request...")
    response: Response = await call_next(request)

    return response


# API: Insert/Update
@app.post("/insert")
def insert(insertPayload: VAL_INSERT):
    logger.info("Invoked insert API...")
    itemID = dbAgent.insert(imsAgent.insert(insertPayload.model_dump()))
    response = {"id": itemID}
    logger.info("Completed insert API...")

    return JSONResponse(response, status_code=200)


if __name__ == "__main__":
    uvicorn.run("API:app", host="127.0.0.1", port=2000, reload=True)
