import calendar
import datetime
import logging

_logger = logging.getLogger(__name__)


def compute_bussiness_days(month: int, year: int, holidays: list = None):
    if holidays is None:
        holidays = []
    _logger.debug(f"Computing bussiness days for month {month} of year {year}")
    start = datetime.date(year, month, 1)
    _, month_days = calendar.monthrange(year, month)
    businessdays = 0
    for i in range(1, month_days + 1):
        try:
            thisdate = datetime.date(start.year, start.month, i)
        except (ValueError):
            _logger.error(
                f"Error computing bussiness days for month {month} of year {year}"
            )
            break
        if thisdate.weekday() > 4:
            _logger.debug(f"Day: {i} from month {month} is weekend")
            continue
        if thisdate in holidays:
            _logger.info(f"Day: {i} from month {month} is a holiday")
            continue
        businessdays += 1
        _logger.debug(f"Bussiness / Regular days: {businessdays}/{i}")
    _logger.info(f"[{year}]Month {month} has {businessdays} bussiness days")
    return businessdays


def compute_year_bussiness_days(year: int, holidays: list = None):
    if holidays is None:
        holidays = []
    months = {}
    for month in range(1, 13):
        months[month] = compute_bussiness_days(month, year, holidays)
    return months
