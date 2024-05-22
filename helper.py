import pytz
from datetime import datetime, timedelta
import pandas as pd
from auto_login import fyers
from config import Config


def get_current_IST():
    current_time_utc = datetime.now(pytz.utc)
    # Convert UTC time to Indian Standard Time (IST)
    ist_timezone = pytz.timezone("Asia/Kolkata")
    return current_time_utc.astimezone(ist_timezone)


def get_dates(n):
    # Get the current date and time in UTC
    current_time_utc = datetime.now(pytz.utc)

    # Convert UTC time to Indian Standard Time (IST)
    ist_timezone = pytz.timezone("Asia/Kolkata")
    current_time_ist = current_time_utc.astimezone(ist_timezone)

    # Calculate the date n days ago in IST
    date_n_days_ago_ist = current_time_ist - timedelta(days=n)

    # Format the dates as strings
    current_date_str = current_time_ist.strftime("%Y-%m-%d")
    n_days_ago_str = date_n_days_ago_ist.strftime("%Y-%m-%d")

    return current_date_str, n_days_ago_str


def update_current_ema(current_data_5_timeframe, current_data_15_timeframe, ltp):
    # Update the last row of current_data_5_timeframe with the new LTP
    current_data_5_timeframe.loc[current_data_5_timeframe.index[-1], "close"] = ltp
    current_data_15_timeframe.loc[current_data_15_timeframe.index[-1], "close"] = ltp
    current_data_5_timeframe["ema"] = (
        current_data_5_timeframe["close"].ewm(span=5, min_periods=5).mean()
    )
    current_data_15_timeframe["ema"] = (
        current_data_15_timeframe["close"].ewm(span=5, min_periods=5).mean()
    )


def getdata(sym, res, rfrom, rto, ltp, config: Config) -> Config:
    cdata = {
        "symbol": sym,
        "resolution": str(res),
        "date_format": "1",
        "range_from": rfrom,
        "range_to": rto,
        "cont_flag": "0",
    }
    response = fyers.history(data=cdata)
    data = pd.DataFrame.from_dict(response["candles"])
    cols = ["datetime", "open", "high", "low", "close", "volume"]
    data.columns = cols
    data["datetime"] = pd.to_datetime(data["datetime"], unit="s")
    data["datetime"] = (
        data["datetime"].dt.tz_localize("utc").dt.tz_convert("Asia/Kolkata")
    )
    data["datetime"] = data["datetime"].dt.tz_localize(None)
    data = data.set_index("datetime")
    data["ema"] = data["close"].ewm(span=5, min_periods=5).mean()
    if res == 5:
        config.data_5_timeframe = data.copy()
        config.data_5_timeframe.drop(config.data_5_timeframe.index[-1], inplace=True)
        config.current_data_5_timeframe = data.copy()
        filename = datetime.now().strftime("data_at_every5_%Y-%m-%d_%H%M%S.csv")
        config.data_5_timeframe.to_csv(filename, index=True)
    if res == 15:
        config.data_15_timeframe = data.copy()
        config.data_15_timeframe.drop(config.data_15_timeframe.index[-1], inplace=True)
        config.current_data_15_timeframe = data.copy()
        filename = datetime.now().strftime("data_at_every15_%Y-%m-%d_%H%M%S.csv")
        config.data_15_timeframe.to_csv(filename, index=True)

    return config


################################## not written by me !!!!!!!!!!!!!!!!!!!!!!!!!!
def getNiftyExpiryDate():
    nifty_expiry = {
        datetime(2023, 11, 16).date(): "23N16",
        datetime(2023, 11, 23).date(): "23N23",
        datetime(2023, 11, 30).date(): "23NOV",
        datetime(2023, 12, 7).date(): "23D07",
        datetime(2023, 12, 14).date(): "23D14",
        datetime(2023, 12, 21).date(): "23D21",
        datetime(2023, 12, 28).date(): "23DEC",
        datetime(2024, 1, 4).date(): "24104",
        datetime(2024, 1, 11).date(): "24111",
        datetime(2024, 1, 18).date(): "24118",
        datetime(2024, 1, 25).date(): "24JAN",
        datetime(2024, 2, 1).date(): "24201",
        datetime(2024, 2, 8).date(): "24208",
        datetime(2024, 2, 15).date(): "24215",
        datetime(2024, 2, 22).date(): "24222",
        datetime(2024, 2, 29).date(): "24FEB",
        datetime(2024, 3, 7).date(): "24307",
        datetime(2024, 3, 14).date(): "24314",
        datetime(2024, 3, 21).date(): "24321",
        datetime(2024, 3, 28).date(): "24MAR",
        datetime(2024, 4, 4).date(): "24404",
        datetime(2024, 4, 10).date(): "24410",
        datetime(2024, 4, 18).date(): "24418",
        datetime(2024, 4, 25).date(): "24APR",
        datetime(2024, 5, 2).date(): "24502",
        datetime(2024, 5, 9).date(): "24509",
        datetime(2024, 5, 16).date(): "24516",
        datetime(2024, 5, 23).date(): "24523",
        datetime(2024, 5, 30).date(): "24MAY",
        datetime(2024, 6, 6).date(): "24606",
        datetime(2024, 6, 13).date(): "24613",
        datetime(2024, 6, 20).date(): "24620",
        datetime(2024, 6, 27).date(): "24JUN",
    }

    today = datetime.now().date()

    for date_key, value in nifty_expiry.items():
        if today <= date_key:
            print(value)
            return value


def getBankNiftyExpiryDate():
    banknifty_expiry = {
        datetime(2023, 11, 15).date(): "23N15",
        datetime(2023, 11, 22).date(): "23N22",
        datetime(2023, 11, 30).date(): "23NOV",
        datetime(2023, 12, 6).date(): "23D06",
        datetime(2023, 12, 13).date(): "23D13",
        datetime(2023, 12, 20).date(): "23D20",
        datetime(2023, 12, 28).date(): "23DEC",
        datetime(2024, 1, 3).date(): "24103",
        datetime(2024, 1, 10).date(): "24110",
        datetime(2024, 1, 17).date(): "24117",
        datetime(2024, 1, 25).date(): "24JAN",
        datetime(2024, 1, 31).date(): "24131",
        datetime(2024, 2, 7).date(): "24207",
        datetime(2024, 2, 14).date(): "24214",
        datetime(2024, 2, 21).date(): "24221",
        datetime(2024, 2, 29).date(): "24FEB",
        datetime(2024, 3, 6).date(): "24306",
        datetime(2024, 3, 13).date(): "24313",
        datetime(2024, 3, 20).date(): "24320",
        datetime(2024, 3, 27).date(): "24MAR",
        datetime(2024, 4, 3).date(): "24403",
        datetime(2024, 4, 10).date(): "24410",
        datetime(2024, 4, 16).date(): "24416",
        datetime(2024, 4, 24).date(): "24APR",
        datetime(2024, 4, 30).date(): "24430",
        datetime(2024, 5, 8).date(): "24508",
        datetime(2024, 5, 15).date(): "24515",
        datetime(2024, 5, 22).date(): "24522",
        datetime(2024, 5, 29).date(): "24MAY",
        datetime(2024, 6, 5).date(): "24605",
        datetime(2024, 6, 12).date(): "24612",
        datetime(2024, 6, 19).date(): "24619",
        datetime(2024, 6, 26).date(): "24JUN",
    }

    today = datetime.now().date()

    for date_key, value in banknifty_expiry.items():
        if today <= date_key:
            print(value)
            return value


def getFinNiftyExpiryDate():
    finnifty_expiry = {
        datetime(2024, 2, 20).date(): "24220",
        datetime(2024, 2, 27).date(): "24FEB",
        datetime(2024, 3, 5).date(): "24305",
        datetime(2024, 3, 12).date(): "24312",
        datetime(2024, 3, 19).date(): "24319",
        datetime(2024, 3, 26).date(): "24MAR",
        datetime(2024, 4, 2).date(): "24402",
        datetime(2024, 4, 9).date(): "24409",
        datetime(2024, 4, 16).date(): "24416",
        datetime(2024, 4, 23).date(): "24423",
        datetime(2024, 4, 30).date(): "24APR",
        datetime(2024, 5, 7).date(): "24507",
        datetime(2024, 5, 14).date(): "24514",
        datetime(2024, 5, 21).date(): "24521",
        datetime(2024, 5, 28).date(): "24MAY",
        datetime(2024, 6, 4).date(): "24604",
        datetime(2024, 6, 11).date(): "24611",
        datetime(2024, 6, 18).date(): "24618",
        datetime(2024, 6, 25).date(): "24JUN",
    }

    today = datetime.now().date()

    for date_key, value in finnifty_expiry.items():
        if today <= date_key:
            print(value)
            return value


def getExpiryFormat(year, month, day, monthly):
    if monthly == 0:
        day1 = day
        if month == "JAN":
            month1 = 1
        elif month == "FEB":
            month1 = 2
        elif month == "MAR":
            month1 = 3
        elif month == "APR":
            month1 = 4
        elif month == "MAY":
            month1 = 5
        elif month == "JUN":
            month1 = 6
        elif month == "JUL":
            month1 = 7
        elif month == "AUG":
            month1 = 8
        elif month == "SEP":
            month1 = 9
        elif month == "OCT":
            month1 = "O"
        elif month == "NOV":
            month1 = "N"
        elif month == "DEC":
            month1 = "D"
    elif monthly == 1:
        day1 = ""
        month1 = month

    return str(year) + str(month1) + str(day1)


def getIndexSpot(stock):
    if stock == "BANKNIFTY":
        name = "NSE:NIFTYBANK-INDEX"
    elif stock == "NIFTY":
        name = "NSE:NIFTY50-INDEX"
    elif stock == "FINNIFTY":
        name = "NSE:FINNIFTY-INDEX"

    return name


def getOptionFormat(stock, intExpiry, strike, ce_pe):
    return "NSE:" + str(stock) + str(intExpiry) + str(strike) + str(ce_pe)
