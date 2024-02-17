from datetime import date, timedelta


def first_day_next_month():
    today = date.today()
    if today.month == 12:
        first_day = date(day=1, month=1, year=today.year + 1)
    else:
        first_day = today.replace(day=1, month=today.month + 1)
    return first_day


def last_day_of_month():
    return first_day_next_month() - timedelta(days=1)


def date_to_str(date):
    return date.strftime("%Y-%m-%d")
