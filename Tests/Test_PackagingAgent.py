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
            self.assertEqual(
                result,
                expected,
                f"Test failed for params {testCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )

    def test_upsertOut(self):
        """Test the upsertOut method."""

        # Test case 1: Normal input
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
            self.assertEqual(
                result,
                expected,
                f"Test failed for params {testCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )

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
            self.assertEqual(
                result,
                expected,
                f"Test failed for params {testCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )

    def test_advanceQueryIn(self):
        """Test the advanceQueryIn method."""

        testCases = [
            # Test case 1: Basic query with all fields
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.5, 50.75],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                },
                (
                    "notebook",
                    "Stationary",
                    10.50,
                    50.75,
                    "price",
                    "asc",
                    10,
                ),
            ),
            # Test case 2: Different pagination values
            (
                {
                    "filters": {
                        "name": "pen",
                        "category": "Office Supplies",
                        "price_range": [1.99, 5.99],
                    },
                    "pagination": {"page": 2, "limit": 20},
                    "sort": {"field": "name", "order": "desc"},
                },
                (
                    "pen",
                    "Office Supplies",
                    1.99,
                    5.99,
                    "name",
                    "desc",
                    40,  # page * limit = 2 * 20
                ),
            ),
            # Test case 3: Rounding of price values
            (
                {
                    "filters": {
                        "name": "eraser",
                        "category": "School Supplies",
                        "price_range": [0.333, 9.666],
                    },
                    "pagination": {"page": 3, "limit": 15},
                    "sort": {"field": "category", "order": "asc"},
                },
                (
                    "eraser",
                    "School Supplies",
                    0.33,
                    9.67,
                    "category",
                    "asc",
                    45,
                ),
            ),
            # Test case 4: Large pagination values
            (
                {
                    "filters": {
                        "name": "marker",
                        "category": "Art Supplies",
                        "price_range": [5.0, 25.0],
                    },
                    "pagination": {"page": 10, "limit": 100},
                    "sort": {"field": "price", "order": "desc"},
                },
                (
                    "marker",
                    "Art Supplies",
                    5.00,
                    25.00,
                    "price",
                    "desc",
                    1000,
                ),
            ),
        ]

        for testCase, expected in testCases:
            result = self.packagingAgent.advanceQueryIn(testCase)
            self.assertEqual(
                result,
                expected,
                f"Test failed for params {testCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )


def test_advanceQueryOut(self):
    """Test the advanceQueryOut method."""

    testCases = [
        # Test case 1: Empty result set
        (
            [],
            {
                "filters": {
                    "name": "notebook",
                    "category": "Stationary",
                    "price_range": [10.5, 50.75],
                },
                "pagination": {"page": 1, "limit": 10},
                "sort": {"field": "price", "order": "asc"},
            },
            {
                "items": [],
                "count": 0,
                "page": 1,
                "limit": 10,
            },
        ),
        # Test case 2: Single item result
        (
            [(1, "Blue Pen", "Stationary", "2.50")],
            {
                "filters": {
                    "name": "pen",
                    "category": "Stationary",
                    "price_range": [1.0, 5.0],
                },
                "pagination": {"page": 1, "limit": 10},
                "sort": {"field": "price", "order": "asc"},
            },
            {
                "items": [
                    {
                        "id": 1,
                        "name": "Blue Pen",
                        "category": "Stationary",
                        "price": 2.50,
                    }
                ],
                "count": 1,
                "page": 1,
                "limit": 10,
            },  # expected result
        ),
        # Test case 3: Multiple items result
        (
            [
                (1, "Blue Pen", "Stationary", "2.50"),
                (2, "Red Pen", "Stationary", "2.50"),
                (3, "Black Pen", "Stationary", "2.75"),
            ],
            {
                "filters": {
                    "name": "pen",
                    "category": "Stationary",
                    "price_range": [1.0, 5.0],
                },
                "pagination": {"page": 1, "limit": 10},
                "sort": {"field": "name", "order": "asc"},
            },
            {
                "items": [
                    {
                        "id": 1,
                        "name": "Blue Pen",
                        "category": "Stationary",
                        "price": 2.50,
                    },
                    {
                        "id": 2,
                        "name": "Red Pen",
                        "category": "Stationary",
                        "price": 2.50,
                    },
                    {
                        "id": 3,
                        "name": "Black Pen",
                        "category": "Stationary",
                        "price": 2.75,
                    },
                ],
                "count": 3,
                "page": 1,
                "limit": 10,
            },
        ),
        # Test case 4: Different pagination values
        (
            [
                (4, "Notebook", "Stationary", "12.99"),
                (5, "Planner", "Stationary", "15.50"),
            ],
            {
                "filters": {
                    "name": "notebook",
                    "category": "Stationary",
                    "price_range": [10.0, 20.0],
                },
                "pagination": {"page": 2, "limit": 5},
                "sort": {"field": "price", "order": "desc"},
            },
            {
                "items": [
                    {
                        "id": 4,
                        "name": "Notebook",
                        "category": "Stationary",
                        "price": 12.99,
                    },
                    {
                        "id": 5,
                        "name": "Planner",
                        "category": "Stationary",
                        "price": 15.50,
                    },
                ],
                "count": 2,
                "page": 2,
                "limit": 5,
            },
        ),
        # Test case 5: String price conversion to float
        (
            [(6, "Premium Marker", "Art Supplies", "7.99999")],
            {
                "filters": {
                    "name": "marker",
                    "category": "Art Supplies",
                    "price_range": [5.0, 10.0],
                },
                "pagination": {"page": 1, "limit": 10},
                "sort": {"field": "price", "order": "asc"},
            },
            {
                "items": [
                    {
                        "id": 6,
                        "name": "Premium Marker",
                        "category": "Art Supplies",
                        "price": 7.99999,
                    }
                ],
                "count": 1,
                "page": 1,
                "limit": 10,
            },
        ),
    ]

    for testCaseOutPayload, testCaseInPayload, expected in testCases:
        result = self.packagingAgent.advanceQueryOut(
            testCaseOutPayload, testCaseInPayload
        )
        self.assertEqual(
            result,
            expected,
            f"Test failed for params {testCaseOutPayload, testCaseInPayload}\n"
            f"Expected: {expected}\nGot: {result}",
        )


if __name__ == "__main__":
    unittest.main()
