import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from datetime import datetime
from Services.PackagingAgent import PackagingAgent


class TestPackagingAgent(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.packagingAgent = PackagingAgent()

    def test_upsertIn(self):
        """Test the upsertIn method."""
        testCases = [
            # Test case 1: Normal input
            (
                {"name": "Test Item", "category": "Electronics", "price": 99.99},
                ("Test Item", "Electronics", "99.99"),
            ),
            # Test case 2: Price formatting
            (
                {"name": "Test Item", "category": "Electronics", "price": 99},
                ("Test Item", "Electronics", "99.00"),
            ),
        ]

        for testCase, expected in testCases:
            result = self.packagingAgent.upsertIn(testCase)
            self.assertEqual(result, expected)

    def test_upsertOut(self):
        """Test the upsertOut method."""
        testCase, expected = ((123,), {"id": 123})

        result = self.packagingAgent.upsertOut(testCase)
        self.assertEqual(result, expected)

    def test_queryIn(self):
        """Test the queryIn method."""
        dt_from = datetime(2023, 1, 1, 0, 0, 0)
        dt_to = datetime(2023, 12, 31, 23, 59, 59)

        testCases = [
            # Test case 1: With both dates
            (
                {"dt_from": dt_from, "dt_to": dt_to, "category": "Electronics"},
                (
                    "2023-01-01 00:00:00",
                    "2023-12-31 23:59:59",
                    "Electronics",
                    "Electronics",
                ),
            ),
            # Test case 2: With only dt_from
            (
                {"dt_from": dt_from, "category": "Electronics"},
                ("2023-01-01 00:00:00", None, "Electronics", "Electronics"),
            ),
            # Test case 3: With only dt_to
            (
                {"dt_to": dt_to, "category": "Electronics"},
                (None, "2023-12-31 23:59:59", "Electronics", "Electronics"),
            ),
            # Test case 4: Without dates
            (
                {"category": "Electronics"},
                (None, None, "Electronics", "Electronics"),
            ),
        ]

        for testCase, expected in testCases:
            result = self.packagingAgent.queryIn(testCase)
            self.assertEqual(result, expected)

    def test_queryOut(self):
        """Test the queryOut method."""
        testCases = [
            # Test case 1: Multiple items
            (
                [
                    (1, "Item 1", "Electronics", "99.99"),
                    (2, "Item 2", "Books", "19.99"),
                    (3, "Item 3", "Clothing", "29.99"),
                ],
                {
                    "items": [
                        {
                            "id": 1,
                            "name": "Item 1",
                            "category": "Electronics",
                            "price": 99.99,
                        },
                        {
                            "id": 2,
                            "name": "Item 2",
                            "category": "Books",
                            "price": 19.99,
                        },
                        {
                            "id": 3,
                            "name": "Item 3",
                            "category": "Clothing",
                            "price": 29.99,
                        },
                    ],
                    "total_price": 149.97,
                },
            ),
            # Test case 2: Empty list
            (
                [],
                {"items": [], "total_price": 0},
            ),
            # Test case 3: Single item
            (
                [(1, "Item 1", "Electronics", "99.99")],
                {
                    "items": [
                        {
                            "id": 1,
                            "name": "Item 1",
                            "category": "Electronics",
                            "price": 99.99,
                        }
                    ],
                    "total_price": 99.99,
                },
            ),
        ]

        for testCase, expected in testCases:
            result = self.packagingAgent.queryOut(testCase)
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
