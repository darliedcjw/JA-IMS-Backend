from Utils.Logger import createLogger

# Logger
logger = createLogger()
logger.info("IMSAgent's logger is warm...")


class IMSAgent:
    def __init__(self):
        pass

    def upsert(self, upsertPayload):
        logger.info("Packinging upsert payload...")
        return (
            upsertPayload.get("name"),
            upsertPayload.get("category"),
            upsertPayload.get("price"),
        )
