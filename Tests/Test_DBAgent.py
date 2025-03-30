import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mysql.connector

# TestDBAgent.py
import unittest
import mysql
from Services.DBAgent import DBAgent


class CredentialsTest(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_DATABASE")
        self.table = os.getenv("DB_TABLE")
        self.dbAgent = DBAgent()

    def test_create_database(self):
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
            print(result)

            result_data = [(row[1], row[2], row[3]) for row in result]

            expected_sorted = sorted(expected)
            result_sorted = sorted(result_data)

            self.assertEqual(
                result_sorted,
                expected_sorted,
                f"Query failed for params {testCase}\n"
                f"Expected: {expected_sorted}\nGot: {result_sorted}",
            )


if __name__ == "__main__":
    unittest.main()
