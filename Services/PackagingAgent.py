from Utils.Logger import createLogger
from datetime import datetime

# Logger
logger = createLogger()
logger.info("PackagingAgent's logger is warm...")


class PackagingAgent:
    def __init__(self):
        pass

    def upsertIn(self, upsertInPayload):
        logger.info("Packinging upsertIn payload...")
        return (
            upsertInPayload.get("name"),
            upsertInPayload.get("category"),
            round(upsertInPayload.get("price"), 2),
        )

    def upsertOut(self, upsertOutPayload):
        logger.info("Packinging upsertOut payload...")
        return {"id": upsertOutPayload[0]}

    def queryIn(self, queryInPayload):
        logger.info("Packinging queryIn payload...")
        dt_from = (
            datetime.strftime(queryInPayload.get("dt_from"), "%Y-%m-%d %H:%M:%S")
            if queryInPayload.get("dt_from")
            else None
        )
        dt_to = (
            datetime.strftime(queryInPayload.get("dt_to"), "%Y-%m-%d %H:%M:%S")
            if queryInPayload.get("dt_from")
            else None
        )
        category = queryInPayload.get("category")
        return (dt_from, dt_to, category, category)

    def queryOut(self, queryOutPayload):
        logger.info("Packinging queryOut payload...")
        totalPrice = sum(item[3] for item in queryOutPayload)
        return {
            "items": [
                {"id": item[0], "name": item[1], "category": item[2], "price": item[3]}
                for item in queryOutPayload
            ],
            "total_price": totalPrice,
        }
