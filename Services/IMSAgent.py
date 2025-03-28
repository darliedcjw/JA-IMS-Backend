from Utils.Logger import createLogger

# Logger
logger = createLogger()
logger.info("IMSAgent's logger is warm...")


class IMSAgent:
    def __init__(self):
        pass

    def insert(self, insertPayload):
        logger.info("Packinging insert payload...")
        return (
            insertPayload.get("name"),
            insertPayload.get("category"),
            insertPayload.get("price"),
        )
