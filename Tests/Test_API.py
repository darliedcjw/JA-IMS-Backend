import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from datetime import datetime, timedelta
from pydantic import ValidationError
from Utils.Schemas import *


class TestValidationPayloads(unittest.TestCase):

    def test_val_upsert(self):
        testCases = [
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

        for testCase, expected in testCases:
            result = VAL_UPSERT(**testCase).model_dump()
            self.assertEqual(result, expected)

        # Test case 3: Invalid input - missing field
        with self.assertRaises(ValidationError):
            VAL_UPSERT(name="Test Item", category="Electronics")

    def test_val_query(self):
        now = datetime.now()

        # Test case 1: Valid input - all fields
        test_case, expected = (
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
        )
        result = VAL_QUERY(**test_case).model_dump()
        self.assertEqual(result, expected)

        # Test case 2: Valid input - optional fields omitted
        test_case, expected = ({}, {"dt_from": None, "dt_to": None, "category": None})
        result = VAL_QUERY(**test_case).model_dump()
        self.assertEqual(result, expected)

        # Test case 3: Invalid input - empty string category
        with self.assertRaises(ValidationError):
            VAL_QUERY(category="")

        # Test case 4: Invalid input - dt_from after dt_to
        with self.assertRaises(ValidationError):
            VAL_QUERY(dt_from=now + timedelta(days=1), dt_to=now)

        # Test case 5: Valid input - only dt_from
        test_case, expected = (
            {"dt_from": now},
            {"dt_from": now, "dt_to": None, "category": None},
        )
        result = VAL_QUERY(**test_case).model_dump()
        self.assertEqual(result, expected)

        # Test case 6: Valid input - only dt_to
        test_case, expected = (
            {"dt_to": now},
            {"dt_from": None, "dt_to": now, "category": None},
        )
        result = VAL_QUERY(**test_case).model_dump()
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
