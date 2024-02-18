import unittest
from datetime import datetime

from dateutil.parser import parse
from python_calendar import Calendar


class TestCalendar(unittest.TestCase):
    def test_get_calendar_until(self):
        date_from = parse('2023-08-23')
        date_to = parse('2024-08-23')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(len(calendar.days.keys()), 366)
        self.assertEqual(len(calendar.weeks.keys()), 53)
        self.assertEqual(len(calendar.months.keys()), 13)
        self.assertEqual(len(calendar.years), 2)

        date_from = parse('2023-12-23')
        date_to = parse('2024-02-19')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(len(calendar.days.keys()), 58)
        self.assertEqual(len(calendar.weeks.keys()), 9)
        self.assertEqual(len(calendar.months.keys()), 3)
        self.assertEqual(len(calendar.years), 2)

        date_from = parse('2023-01-02')
        date_to = parse('2023-01-09')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(len(calendar.days.keys()), 7)
        self.assertEqual(len(calendar.weeks.keys()), 1)
        self.assertEqual(len(calendar.months.keys()), 1)
        self.assertEqual(len(calendar.years), 1)

        date_from = parse('2023-08-22')
        date_to = parse('2023-08-29')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(len(calendar.days.keys()), 7)
        self.assertEqual(len(calendar.weeks.keys()), 2)
        self.assertEqual(len(calendar.months.keys()), 1)
        self.assertEqual(len(calendar.years), 1)

        date_from = parse('2023-08-21')
        date_to = parse('2023-08-28')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(len(calendar.days.keys()), 7)
        self.assertEqual(len(calendar.weeks.keys()), 1)
        self.assertEqual(len(calendar.months.keys()), 1)
        self.assertEqual(len(calendar.years), 1)

        date_from = parse('2023-08-22')
        date_to = parse('2024-08-29')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(len(calendar.days.keys()), 373)
        self.assertEqual(len(calendar.weeks.keys()), 54)
        self.assertEqual(len(calendar.months.keys()), 13)
        self.assertEqual(len(calendar.years), 2)

    def test_get_calendar_until_values(self):
        date_from = parse('2023-08-23')
        date_to = parse('2024-08-23')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(calendar.years, [2023, 2024])
        self.assertEqual(list(calendar.months.keys()), [
            '8-2023',
            '9-2023',
            '10-2023',
            '11-2023',
            '12-2023',
            '1-2024',
            '2-2024',
            '3-2024',
            '4-2024',
            '5-2024',
            '6-2024',
            '7-2024',
            '8-2024'
        ])

        date_from = parse('2023-12-23')
        date_to = parse('2024-01-03')
        calendar = Calendar.get(date_from, date_to)

        self.assertEqual(calendar.years, [2023, 2024])
        self.assertEqual(list(calendar.months.keys()), [
            '12-2023',
            '1-2024',
        ])
        self.assertEqual(calendar.months['12-2023'][0], 12)
        self.assertEqual(calendar.months['12-2023'][1], 2023)

        self.assertEqual(list(calendar.weeks.keys()), [
            '51-2023',
            '52-2023',
            '1-2024'
        ])
        self.assertEqual(calendar.weeks['51-2023'][0], 51)
        self.assertEqual(calendar.weeks['51-2023'][1], 2023)

        self.assertEqual(list(calendar.days.keys()), [
            '2023-12-23',
            '2023-12-24',
            '2023-12-25',
            '2023-12-26',
            '2023-12-27',
            '2023-12-28',
            '2023-12-29',
            '2023-12-30',
            '2023-12-31',
            '2024-01-01',
            '2024-01-02'
        ])
        self.assertEqual(calendar.days['2023-12-23'], datetime(2023, 12, 23, 0, 0))
