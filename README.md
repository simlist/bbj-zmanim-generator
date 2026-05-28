# Zmanim Blanks

A desktop app for generating printable zmanim (Jewish halachic times) schedules for the needs of the BBJ Synagogue. Given a date range, it produces forms with times for davening, Shabbos, and other halachic events and allows for exporting to excel.

## Features

- Calculates halachic times (zmanim) for any location by latitude/longitude
- Supports Hebrew calendar dates via Gregorian-to-Hebrew conversion
- Exports schedules to Excel (`.xlsx`)
- Cross-platform desktop UI built with Flet (Flutter-based)

## Installation

Requires Python 3.13. Install with pip:

```cmd
pip install .
```

Or with [uv](https://docs.astral.sh/uv/):

```cmd
uv sync
```

## Running

```cmd
zmanim-blanks
```

## Building

To publish a standalone Windows executable:

```cmd
flet build windows
```

Flutter will be downloaded and installed automatically if not already present. See the [Flet packaging docs](https://flet.dev/docs/publish/windows/) for prerequisites (Visual Studio with the Desktop development with C++ workload is required).
