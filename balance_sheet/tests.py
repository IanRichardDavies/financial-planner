from datetime import datetime
from django.test import TestCase

from . import Mortgage


class MortgageTestCase(TestCase):
    valid = [
        {
            "principal": 1_000_000,
            "interest_rate": 0.03,
            "term": 3,
            "amortization": 25,
            "start_date": datetime(2021, 7, 1),
            "prepayment_per_period": 0,
        },
        {
            "principal": "500000",
            "interest_rate": 5,
            "term": 5,
            "amortization": 30,
            "start_date": "2021-07-01",
            "prepayment_per_period": 1000,
        },
        ]

    def test_valid_mortgage_init(self):
        for kwargs in self.valid:
            mortgage = Mortgage(**kwargs)
            assert mortgage.payment >= 1000
            assert len(mortgage.amortization_table) > 0

    def test_invalid_principal(self):
        test = self.valid[0].copy()
        for arg in [-1000, "1000!", 12_000_000,]:
            test["principal"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_invalid_interest_rate(self):
        test = self.valid[0].copy()
        for arg in [-0.1, "0.2a", 30, 0.5]:
            test["interest_rate"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_invalid_term(self):
        test = self.valid[0].copy()
        for arg in [0, "2!", 35,]:
            test["term"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_invalid_amortization(self):
        test = self.valid[0].copy()
        for arg in [0, "2!", 35,]:
            test["amortization"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_invalid_start_date(self):
        test = self.valid[0].copy()
        for arg in ["01-25-2021", "25-01-2021"]:
            test["start_date"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_invalid_prepayment(self):
        test = self.valid[0].copy()
        for arg in [-100, "200a", 30_000,]:
            test["prepayment_per_period"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_invalid_payments_per_years(self):
        test = self.valid[0].copy()
        for arg in [-10, 10, 35,]:
            test["payments_per_year"] = arg
            with self.assertRaises(ValueError):
                mortgage = Mortgage(**test)

    def test_calculate_num_payments_dates(self):
        test = self.valid[0].copy()
        for arg in [12, 26, 52,]:
            test["payments_per_year"] = arg
            mortgage = Mortgage(**test)
            test_stat =  mortgage._calculate_num_periods_between_dates(
                start_date = "2022-01-01",
                end_date = "2023-01-5",
            )
            assert test_stat == arg

    def test_create_amortization_table(self):
        test = self.valid[0].copy()
        mortgage = Mortgage(**test)
        assert mortgage.amortization_table.shape == (300, 6)
        assert mortgage.amortization_table["balance"].iloc[0] < test["principal"]
        assert abs(mortgage.amortization_table["balance"].iloc[-1]) < 1
        assert mortgage.amortization_table["payment"].nunique() == 1
