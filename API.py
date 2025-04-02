import uvicorn
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from Utils.Schemas import *
from Utils.Logger import createLogger, sessionIDVar

from Services.PackagingAgent import PackagingAgent
from Services.DBAgent import DBAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],
)

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


# API: Upsert
@app.post("/upsert")
def upsert(upsertPayload: VAL_UPSERT):
    logger.info("Invoked upsert API...")
    listID = dbAgent.upsert(packagingAgent.upsertIn(upsertPayload.model_dump()))
    response = packagingAgent.upsertOut(listID)
    logger.info("Completed upsert API...")

    return JSONResponse(response, status_code=200)


# API: Query
@app.post("/query")
def query(queryPayload: VAL_QUERY):
    logger.info("Invoked query API...")
    Listitems = dbAgent.query(packagingAgent.queryIn(queryPayload.model_dump()))
    response = packagingAgent.queryOut(Listitems)
    logger.info("Completed query API...")

    return JSONResponse(response, status_code=200)


# API: Advance Query
@app.post("/advance-query")
def query(advanceQueryPayload: VAL_ADVANCE_QUERY):
    logger.info("Invoked advance query API...")
    print(advanceQueryPayload.model_dump())
    Listitems = dbAgent.advanceQuery(
        packagingAgent.advanceQueryIn(advanceQueryPayload.model_dump())
    )
    response = packagingAgent.advanceQueryOut(
        Listitems, advanceQueryPayload.model_dump()
    )
    logger.info("Completed advance query API...")

    return JSONResponse(response, status_code=200)


if __name__ == "__main__":
    uvicorn.run("API:app", host="127.0.0.1", port=2000, reload=True)
