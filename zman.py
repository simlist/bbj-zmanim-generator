from datetime import date, timedelta

from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
from pyluach.dates import HebrewDate
import pandas as pd

LOCATION = GeoLocation(
    "Savannah, GA",
    32.026,
    -81.108,
    "America/New_York"
)


def get_weekend_dates(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        if current.weekday() in (4, 5, 6):  # Friday, Saturday, Sunday
            days.append(current)
        current += timedelta(days=1)
    return days


def _fmt(dt) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime('%#I:%M:%S %p')


def compute_zmanim(d: date) -> dict:
    cal = ZmanimCalendar(geo_location=LOCATION, date=d)
    weekday = d.weekday()
    data = {
        "Date": d.strftime('%A, %B %d'),
        "Hebrew Date": format(HebrewDate.from_pydate(d), '%*d %*B'),
        "Day": 'Shabbos' if d.weekday() == 5 else d.strftime('%A'),
        "Shkia": _fmt(cal.shkia()),
        "Plag HaMincha": _fmt(cal.plag_hamincha()),
    }
    if weekday == 4:  # Friday
        data["Early Candle Lighting"] = _fmt(cal.plag_hamincha())
        data["Late Candle Lighting"] = _fmt(cal.shkia() - timedelta(minutes=20))
        data['Mincha'] = _fmt(cal.plag_hamincha() - timedelta(minutes=15))
    elif weekday == 5:  # Shabbos
        data['Talmud Class'] = _fmt(cal.shkia() - timedelta(minutes=90))
        data['Shabbos Concludes'] = _fmt(cal.shkia() + timedelta(minutes=45))
    return data


def generate_excel(rows: list[dict], save_path: str) -> None:
    df = pd.DataFrame(
        rows,
        columns=[
            "Date",
            "Hebrew Date",
            "Day",
            "Shkia",
            "Plag HaMincha",
            "Early Candle Lighting",
            "Late Candle Lighting",
            "Mincha",
            "Talmud Class",
            "Shabbos Concludes",
        ]
    )
    df.to_excel(save_path, index=False, engine="openpyxl")