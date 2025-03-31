import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mysql.connector

# TestDBAgent.py
import unittest
import mysql
from Services.DBAgent import DBAgent


class TestDatabaseAgent(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_DATABASE")
        self.table = os.getenv("DB_TABLE")
        self.dbAgent = DBAgent()

    def test_create_database(self):
        """Test the internal create database method."""

        try:
            self.dbAgent._verifyDatabase()

            connection = mysql.connector.connect(
                host=self.host, user=self.user, password=self.password
            )

            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            self.assertIn(self.database, databases)

        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals() and connection.is_connected():
                connection.close()

    def test_create_table(self):
        """Test the internal create table method."""

        try:
            self.dbAgent._verifyTable()
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            self.assertIn(self.table, tables)

        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals() and connection.is_connected():
                connection.close()

    def test_upsert(self):
        """Test the upsert method."""

        # Test case 1: Normal input
        testCase, expected = (("Test Item", "Stationary", "1.70"), int)

        try:
            itemID = self.dbAgent.upsert(testCase)[0]

            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            cursor = connection.cursor()

            cursor.execute(
                f"""
                SELECT name, category, price
                FROM {self.table}
                WHERE name = %s
            """,
                (testCase[0],),
            )

            result = cursor.fetchone()

            self.assertIsInstance(itemID, expected)
            self.assertEqual(result[0], testCase[0])
            self.assertEqual(result[1], testCase[1])
            self.assertEqual(result[2], testCase[2])

        finally:
            if "cursor" in locals():
                cursor.execute(
                    f"DELETE FROM {self.table} WHERE name = %s", (testCase[0],)
                )
                connection.commit()
                cursor.close()
            if "connection" in locals() and connection.is_connected():
                connection.close()

    def test_query(self):
        """Test the query method."""

        sampleUpsert = [
            ("Item 1", "Stationary", "1.70"),
            ("Item 2", "Stationary", "3.70"),
            ("Item 3", "Drinks", "2.50"),
            ("Item 4", "Drinks", "3.50"),
        ]

        testCases = [
            # Test case 1: All records
            ((None, None, None, None), sampleUpsert),
            # Test case 2: Date range ending in future (should get all)
            ((None, "3000-12-28", None, None), sampleUpsert),
            # Test case 3: Date range starting from ancient time (should get all)
            (("1000-12-28", None, None, None), sampleUpsert),
            # Test case 4: Stationery category
            ((None, None, "Stationary", "Stationary"), sampleUpsert[:2]),
            # Test case 5: Non-existent category
            ((None, None, "NonExistent", "NonExistent"), []),
            # Test case 6: Specific date range + category
            (("2023-01-01", "2025-12-31", "Drinks", "Drinks"), sampleUpsert[2:]),
        ]

        for sample in sampleUpsert:
            self.dbAgent.upsert(sample)

        for testCase, expected in testCases:
            result = self.dbAgent.query(testCase)

            resultData = [(row[1], row[2], row[3]) for row in result]

            expectedSorted = sorted(expected)
            resultSorted = sorted(resultData)

            self.assertEqual(
                resultSorted,
                expectedSorted,
                f"Query failed for params {testCase}\n"
                f"Expected: {expectedSorted}\nGot: {resultSorted}",
            )

    def test_advanceQuery(self):
        """Test the advanceQuery method."""

        sampleUpsert = [
            ("Item A", "Stationary", "12.50"),
            ("Item B", "Stationary", "2.75"),
            ("Item C", "Art Supplies", "5.99"),
            ("Item D", "Stationary", "1.25"),
            ("Item E", "Art Supplies", "15.00"),
        ]

        for sample in sampleUpsert:
            self.dbAgent.upsert(sample)

        testCases = [
            # Test case 1: Query for Stationary items within price range 1-5
            (
                {
                    "filters": {
                        "name": "Item B",
                        "category": "Stationary",
                        "price_range": [1.0, 5.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                },
                [(2, "Item B", "Stationary", "2.75")],
            ),
            # Test case 2: Query for Art Supplies within price range 5-20
            (
                {
                    "filters": {
                        "name": "Item C",
                        "category": "Art Supplies",
                        "price_range": [5.0, 20.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                },
                [(3, "Item C", "Art Supplies", "5.99")],
            ),
            # Test case 3: Query with no results
            (
                {
                    "filters": {
                        "name": "NonExistent",
                        "category": "NonExistent",
                        "price_range": [1.0, 100.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                },
                [],
            ),
            # Test case 4: Query with pagination
            (
                {
                    "filters": {
                        "name": "Item A",
                        "category": "Stationary",
                        "price_range": [10.0, 15.0],
                    },
                    "pagination": {"page": 2, "limit": 5},
                    "sort": {"field": "name", "order": "desc"},
                },
                [(1, "Item A", "Stationary", "12.50")],
            ),
        ]

        for testCase, expected in testCases:
            result = self.dbAgent.advanceQuery(testCase)

            self.assertEqual(
                result,
                expected,
                f"Query failed for params {testCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )


if __name__ == "__main__":
    unittest.main()
