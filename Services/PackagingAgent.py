import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.Logger import createLogger
from datetime import datetime

# Logger
logger = createLogger()
logger.info("PackagingAgent's logger is warm...")


class PackagingAgent:
    def __init__(self):
        pass

    def upsertIn(self, upsertInPayload):
        logger.info("Packaging upsertIn payload...")
        return (
            upsertInPayload.get("name").strip(),
            upsertInPayload.get("category").strip(),
            f"{upsertInPayload.get('price'):.2f}",
        )

    def upsertOut(self, upsertOutPayload):
        logger.info("Packaging upsertOut payload...")
        return {"id": upsertOutPayload[0]}

    def queryIn(self, queryInPayload):
        logger.info("Packaging queryIn payload...")
        dt_from = (
            datetime.strftime(queryInPayload.get("dt_from"), "%Y-%m-%d %H:%M:%S")
            if queryInPayload.get("dt_from")
            else None
        )
        dt_to = (
            datetime.strftime(queryInPayload.get("dt_to"), "%Y-%m-%d %H:%M:%S")
            if queryInPayload.get("dt_to")
            else None
        )
        category = queryInPayload.get("category").strip()
        return (
            dt_from,
            dt_to,
            category,
            category,
        )

    def queryOut(self, queryOutPayload):
        logger.info("Packaging queryOut payload...")
        totalPrice = sum(float(item[3]) for item in queryOutPayload)
        return {
            "items": [
                {
                    "id": item[0],
                    "name": item[1],
                    "category": item[2],
                    "price": float(item[3]),
                }
                for item in queryOutPayload
            ],
            "total_price": round(totalPrice, 2),
        }

    def advanceQueryIn(self, advanceQueryInPayload):
        logger.info("Packaging advanceQueryIn payload...")

        name = (
            advanceQueryInPayload.get("filters").get("name").strip()
            if advanceQueryInPayload.get("filters").get("name")
            else None
        )
        category = (
            advanceQueryInPayload.get("filters").get("category").strip()
            if advanceQueryInPayload.get("filters").get("category")
            else None
        )
        minPrice = round(advanceQueryInPayload.get("filters").get("price_range")[0], 2)
        maxPrice = round(advanceQueryInPayload.get("filters").get("price_range")[1], 2)
        pagLimit = advanceQueryInPayload.get("pagination").get("limit")
        pagPage = advanceQueryInPayload.get("pagination").get("page")
        sortField = advanceQueryInPayload.get("sort").get("field")
        sortOrder = advanceQueryInPayload.get("sort").get("order")

        return (
            name,
            name,
            category,
            category,
            minPrice,
            maxPrice,
            sortField,
            sortField,
            sortField,
            pagLimit,
            (pagPage - 1) * pagLimit,
            sortOrder,
        )

    def advanceQueryOut(self, advanceQueryOutPayload, advanceQueryInPayload):
        logger.info("Packaging advanceQueryOut payload...")
        totalCount = len(advanceQueryOutPayload)
        return {
            "items": [
                {
                    "id": item[0],
                    "name": item[1],
                    "category": item[2],
                    "price": float(item[3]),
                }
                for item in advanceQueryOutPayload
            ],
            "count": totalCount,
            "page": advanceQueryInPayload.get("pagination").get("page"),
            "limit": advanceQueryInPayload.get("pagination").get("limit"),
        }
