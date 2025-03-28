import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mysql.connector
from mysql.connector import errors
from fastapi import status
from fastapi.exceptions import HTTPException
from dotenv import load_dotenv

from Utils.Logger import createLogger

# Logger
logger = createLogger()
logger.info("DBAgent's logger is warm...")


class DBAgent:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_DATABASE")
        self.table = os.getenv("DB_TABLE")

    def upsert(self, upsertInPayload):
        logger.info(f"Upserting payload...")
        try:
            self._verifyDatabase()
            self._verifyTable()
            name, _, _ = upsertInPayload
            connection = self._establishConnection(useDatabase=True)
            cursor = connection.cursor(buffered=True)

            insertQuery = f"""
            INSERT INTO {self.table} (name, category, price)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                price = VALUES(price),
                last_updated_dt = NOW()
            """

            cursor.execute(insertQuery, upsertInPayload)

            searchQuery = f"""
            SELECT id FROM {self.table}
            WHERE name = %s
            """

            cursor.execute(searchQuery, (name,))
            itemID = cursor.fetchone()
            connection.commit()

            return itemID

        except mysql.connector.Error as dbError:
            eMsg = f"Database Error: {dbError}"
            logger.error(eMsg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=eMsg,
            )

        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def query(self, queryInPayload):
        logger.info(f"Querying payload...")
        try:
            self._verifyDatabase()
            self._verifyTable()
            connection = self._establishConnection(useDatabase=True)
            cursor = connection.cursor(buffered=True)

            filterQuery = f"""
            SELECT id, name, category, price FROM {self.table}
            WHERE
                -- Date range filter (both must be provided or omitted)
                last_updated_dt BETWEEN 
                    COALESCE(%s, '1000-01-01') AND 
                    COALESCE(%s, '9999-12-31')
                -- Category filter (optional)
                AND (category = %s OR %s IS NULL)
            """

            cursor.execute(filterQuery, queryInPayload)

            result = cursor.fetchall()
            connection.commit()

            return result

        except mysql.connector.Error as dbError:
            eMsg = f"Database Error: {dbError}"
            logger.error(eMsg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=eMsg,
            )

        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _verifyDatabase(self):
        logger.info(f"Verifying/Creating database - {self.database}...")
        try:
            connection = self._establishConnection(useDatabase=False)
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")

        except mysql.connector.Error as dbError:
            eMsg = f"Database Error: {dbError}"
            logger.error(eMsg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=eMsg,
            )

        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _verifyTable(self):
        logger.info(f"Verifying/Creating table - {self.table}...")
        try:
            connection = self._establishConnection(useDatabase=True)
            cursor = connection.cursor()

            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            category VARCHAR(100) NOT NULL,
            price FLOAT NOT NULL,
            last_updated_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """

            cursor.execute(query)

        except mysql.connector.Error as dbError:
            eMsg = f"Database Error: {dbError}"
            logger.error(eMsg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=eMsg,
            )

        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _establishConnection(self, useDatabase=None):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database if useDatabase else None,
        )


if __name__ == "__main__":
    DBAgent()
