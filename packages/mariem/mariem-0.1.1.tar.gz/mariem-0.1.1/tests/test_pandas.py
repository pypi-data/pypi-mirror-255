from unittest import TestCase

import pandas as pd

from mariem.pandas import combine_collumns


class TestCombineColumns(TestCase):
    def test_combine(self):
        df = pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": [7, 8, 9],
            }
        )

        result = combine_collumns(df, ["a", "b"], "category", "value")

        self.assertDictEqual(
            result.to_dict('list'),
            {
                "category": ["a", "b", "a", "b", "a", "b"],
                "value": [1, 4, 2, 5, 3, 6],
                "c": [7, 7, 8, 8, 9, 9],
            }
        )

    def test_combine_single(self):
        df = pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": [7, 8, 9],
            }
        )

        result = combine_collumns(df, ["a"], "category", "value")

        self.assertDictEqual(
            result.to_dict('list'),
            {
                "category": ["a", "a", "a"],
                "value": [1, 2, 3],
                "b": [4, 5, 6],
                "c": [7, 8, 9],
            }
        )

    def test_column_not_found(self):
        df = pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
                "c": [7, 8, 9],
            }
        )

        with self.assertRaises(AssertionError):
            combine_collumns(df, ["a", "d"], "category", "value")