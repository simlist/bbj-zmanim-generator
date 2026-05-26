from datetime import date, timedelta
from zmanim.util.geo_location import GeoLocation
from zmanim.zmanim_calendar import ZmanimCalendar
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
    return dt.strftime("%H:%M:%S")


def compute_zmanim(d: date) -> dict:
    cal = ZmanimCalendar(geo_location=LOCATION, date=d)
    return {
        "Date": d.strftime("%Y-%m-%d"),
        "Day": d.strftime("%A"),
        "Shkia": _fmt(cal.shkia()),
        "Plag HaMincha": _fmt(cal.plag_hamincha()),
    }


def generate_excel(rows: list[dict], save_path: str) -> None:
    df = pd.DataFrame(rows, columns=["Date", "Day", "Shkia", "Plag HaMincha"])
    df.to_excel(save_path, index=False, engine="openpyxl")