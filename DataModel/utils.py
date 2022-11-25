import datetime
import dateutil.parser as dp


def convertISO8601toUnix(iso_ts):
    parsed_t = dp.parse(iso_ts)
    return int(parsed_t.timestamp())
