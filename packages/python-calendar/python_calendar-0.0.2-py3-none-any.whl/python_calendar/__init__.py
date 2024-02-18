from datetime import datetime
from dateutil.relativedelta import relativedelta


class Calendar:
    def __init__(self):
        self.days = {}
        self.weeks = {}
        self.months = {}
        self.years = []

    def get_or_create_year(self, year):
        if year not in self.years:
            self.years.append(year)
        return year

    def get_or_create_week(self, n, year):
        key = '%s-%s' % (n, year)
        if key not in self.weeks.keys():
            year = self.get_or_create_year(year)
            self.weeks[key] = (n, year)
        return self.weeks[key]

    def get_or_create_month(self, n, year):
        key = '%s-%s' % (n, year)
        if key not in self.months.keys():
            year = self.get_or_create_year(year)
            self.months[key] = (n, year)
        return self.months[key]

    def get_or_create_day(self, date):
        if not isinstance(date, datetime):
            raise Exception('`date` must be a instance of datetime')

        key = date.strftime('%Y-%m-%d')
        if key not in self.days.keys():
            self.get_or_create_year(date.year)
            self.get_or_create_month(date.month, date.year)
            self.get_or_create_week(
                date.isocalendar()[1],
                date.isocalendar()[0]
            )
            self.days[key] = date
        return self.days[key]

    @staticmethod
    def get(date_from, date_to):
        if not isinstance(date_from, datetime):
            raise Exception('`date_from` must be a instance of datetime')
        if not isinstance(date_to, datetime):
            raise Exception('`date_to` must be a instance of datetime')

        d = date_to - date_from

        calendar = Calendar()
        for i in range(0, d.days):
            t = date_from + relativedelta(days=+i)
            calendar.get_or_create_day(t)
        return calendar
