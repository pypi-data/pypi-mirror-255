from datetime import date

import unittest

from qtl_trading_calendar import FuturesTradingCalendar
from qtl_trading_calendar import StockTradingCalendar


class TestFutures(unittest.TestCase):
    def setUp(self):
        self.calendar = FuturesTradingCalendar()

    def test_case1(self):
        test_date = date(2022, 12, 13)
        self.assertTrue(self.calendar.is_trading_day(test_date))
        self.assertTrue(self.calendar.has_day_trading(test_date))
        self.assertTrue(self.calendar.has_night_trading(test_date))
        self.assertEqual(self.calendar.next_trading_day(test_date), date(2022, 12, 14))
        self.assertEqual(self.calendar.previous_trading_day(test_date), date(2022, 12, 12))

    def test_case2(self):
        test_date = date(2022, 12, 10)
        self.assertFalse(self.calendar.is_trading_day(test_date))
        self.assertFalse(self.calendar.has_day_trading(test_date))
        self.assertFalse(self.calendar.has_night_trading(test_date))
        self.assertEqual(self.calendar.next_trading_day(test_date), date(2022, 12, 12))
        self.assertEqual(self.calendar.previous_trading_day(test_date), date(2022, 12, 9))

    def test_case3(self):
        test_date = date(2022, 10, 3)
        self.assertFalse(self.calendar.is_trading_day(test_date))
        self.assertFalse(self.calendar.has_day_trading(test_date))
        self.assertFalse(self.calendar.has_night_trading(test_date))
        self.assertEqual(self.calendar.next_trading_day(test_date), date(2022, 10, 10))
        self.assertEqual(self.calendar.previous_trading_day(test_date), date(2022, 9, 30))


class TestStock(unittest.TestCase):
    def setUp(self):
        self.calendar = StockTradingCalendar()

    def test_case1(self):
        test_date = date(2022, 12, 13)
        self.assertTrue(self.calendar.is_trading_day(test_date))
        self.assertEqual(self.calendar.next_trading_day(test_date), date(2022, 12, 14))
        self.assertEqual(self.calendar.previous_trading_day(test_date), date(2022, 12, 12))

    def test_case2(self):
        test_date = date(2022, 12, 10)
        self.assertFalse(self.calendar.is_trading_day(test_date))
        self.assertEqual(self.calendar.next_trading_day(test_date), date(2022, 12, 12))
        self.assertEqual(self.calendar.previous_trading_day(test_date), date(2022, 12, 9))

    def test_case3(self):
        test_date = date(2022, 10, 3)
        self.assertFalse(self.calendar.is_trading_day(test_date))
        self.assertEqual(self.calendar.next_trading_day(test_date), date(2022, 10, 10))
        self.assertEqual(self.calendar.previous_trading_day(test_date), date(2022, 9, 30))


if __name__ == '__main__':
    unittest.main()
