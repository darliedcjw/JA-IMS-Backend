import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from datetime import datetime, timedelta
from pydantic import ValidationError
from Utils.Schemas import *


class TestAPIValidation(unittest.TestCase):

    def test_1_val_upsert(self):
        """Test the payload validation schema for upsert API."""

        # Valid Test Cases
        validTestCases = [
            # Test case 1: Normal input
            (
                {"name": "Test Item", "category": "Electronics", "price": 99.99},
                {"name": "Test Item", "category": "Electronics", "price": 99.99},
            ),
            # Test Case 2: Price - string to float
            (
                {"name": "Test Item", "category": "Electronics", "price": "99.99"},
                {"name": "Test Item", "category": "Electronics", "price": 99.99},
            ),
        ]

        for validTestCase, expected in validTestCases:
            result = VAL_UPSERT(**validTestCase).model_dump()
            self.assertEqual(
                result,
                expected,
                f"Query failed for params {validTestCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )

        # Test case 3: Invalid input - missing field
        invalidTestCase = {"name": "Test Item", "category": "Electronics"}

        with self.assertRaises(ValidationError):
            VAL_ADVANCE_QUERY(**invalidTestCase)

    def test_2_val_query(self):
        """Test the payload validation schema for query API."""

        now = datetime.now()

        # Valid Test Cases
        validTestCases = [
            # Test case 1: All fields
            (
                {
                    "dt_from": now,
                    "dt_to": now + timedelta(days=1),
                    "category": "Electronics",
                },
                {
                    "dt_from": now,
                    "dt_to": now + timedelta(days=1),
                    "category": "Electronics",
                },
            ),
            # Test case 2: Optional fields omitted
            ({}, {"dt_from": None, "dt_to": None, "category": None}),
            # Test case 3 : Only dt_from
            (
                {"dt_from": now},
                {"dt_from": now, "dt_to": None, "category": None},
            ),
            # Test case 4 : Only dt_to
            (
                {"dt_to": now},
                {"dt_from": None, "dt_to": now, "category": None},
            ),
        ]

        for validTestCase, expected in validTestCases:
            result = VAL_QUERY(**validTestCase).model_dump()
            self.assertEqual(
                result,
                expected,
                f"Query failed for params {validTestCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )

        # Invalid Test Cases
        invalidTestCases = [
            # Test case 5: Empty string category
            ({"category": ""}),
            # Test case 6: dt_from after dt_to
            ({"dt_from": now + timedelta(days=1), "dt_to": now}),
        ]

        for invalidTestCase in invalidTestCases:
            with self.assertRaises(ValidationError):
                VAL_ADVANCE_QUERY(**invalidTestCase)

    def test_3_val_advance_query(self):
        """Test the payload validation schema for advance query API."""

        # Valid Test Cases
        validTestCases = [
            # Test case 1: All fields with valid values
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.0, 50.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                },
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.0, 50.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                },
            ),
            # Test case 2: Different sort field and order
            (
                {
                    "filters": {
                        "name": "pen",
                        "category": "Stationary",
                        "price_range": [1.0, 5.0],
                    },
                    "pagination": {"page": 2, "limit": 20},
                    "sort": {"field": "name", "order": "desc"},
                },
                {
                    "filters": {
                        "name": "pen",
                        "category": "Stationary",
                        "price_range": [1.0, 5.0],
                    },
                    "pagination": {"page": 2, "limit": 20},
                    "sort": {"field": "name", "order": "desc"},
                },
            ),
            # Test case 3: Same price range values
            (
                {
                    "filters": {
                        "name": "eraser",
                        "category": "Stationary",
                        "price_range": [10.0, 10.0],
                    },
                    "pagination": {"page": 1, "limit": 5},
                    "sort": {"field": "category", "order": "asc"},
                },
                {
                    "filters": {
                        "name": "eraser",
                        "category": "Stationary",
                        "price_range": [10.0, 10.0],
                    },
                    "pagination": {"page": 1, "limit": 5},
                    "sort": {"field": "category", "order": "asc"},
                },
            ),
            # Test case 4: No name and category
            (
                {
                    "filters": {
                        "price_range": [10.0, 10.0],
                    },
                    "pagination": {"page": 1, "limit": 5},
                    "sort": {"field": "category", "order": "asc"},
                },
                {
                    "filters": {
                        "name": None,
                        "category": None,
                        "price_range": [10.0, 10.0],
                    },
                    "pagination": {"page": 1, "limit": 5},
                    "sort": {"field": "category", "order": "asc"},
                },
            ),
        ]

        for validTestCase, expected in validTestCases:
            result = VAL_ADVANCE_QUERY(**validTestCase).model_dump()
            self.assertEqual(
                result,
                expected,
                f"Query failed for params {validTestCase}\n"
                f"Expected: {expected}\nGot: {result}",
            )

        # Invalid Test Cases
        invalidTestCases = [
            # Test case 1: Missing filters field
            (
                {
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                }
            ),
            # Test case 2: Missing pagination field
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.0, 50.0],
                    },
                    "sort": {"field": "price", "order": "asc"},
                }
            ),
            # Test case 3: Missing sort field
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.0, 50.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                }
            ),
            # Test case 4: Invalid price range (min > max)
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [50.0, 10.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "asc"},
                }
            ),
            # Test case 5: Invalid sort field
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.0, 50.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "invalid_field", "order": "asc"},
                }
            ),
            # Test case 6: Invalid sort order
            (
                {
                    "filters": {
                        "name": "notebook",
                        "category": "Stationary",
                        "price_range": [10.0, 50.0],
                    },
                    "pagination": {"page": 1, "limit": 10},
                    "sort": {"field": "price", "order": "invalid_order"},
                }
            ),
        ]

        for invalidTestCase in invalidTestCases:
            with self.assertRaises(ValidationError):
                VAL_ADVANCE_QUERY(**invalidTestCase)


if __name__ == "__main__":
    unittest.main()
