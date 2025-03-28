import uvicorn
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from Utils.Schemas import VAL_UPSERT, VAL_QUERY
from Utils.Logger import createLogger, sessionIDVar

from Services.PackagingAgent import PackagingAgent
from Services.DBAgent import DBAgent

app = FastAPI()

# Logger
logger = createLogger()
logger.info("API's logger is warm...")

# IMS Agent: Packaging Payload
packagingAgent = PackagingAgent()
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
@app.post("/upsert")
def upsert(upsertPayload: VAL_UPSERT):
    logger.info("Invoked upsert API...")
    listID = dbAgent.upsert(packagingAgent.upsertIn(upsertPayload.model_dump()))
    response = packagingAgent.upsertOut(listID)
    logger.info("Completed upsert API...")

    return JSONResponse(response, status_code=200)


@app.post("/query")
def query(queryPayload: VAL_QUERY):
    logger.info("Invoked query API...")
    Listitems = dbAgent.query(packagingAgent.queryIn(queryPayload.model_dump()))
    items = packagingAgent.queryOut(Listitems)
    response = {"items": [items]}
    logger.info("Completed query API...")

    return JSONResponse(response, status_code=200)


if __name__ == "__main__":
    uvicorn.run("API:app", host="127.0.0.1", port=2000, reload=True)
