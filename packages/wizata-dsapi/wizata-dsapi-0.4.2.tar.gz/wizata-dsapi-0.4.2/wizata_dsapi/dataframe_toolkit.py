import pandas
import io
from datetime import datetime, timedelta, timezone
import re


def validate(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    validate dataframe format to match supported Wizata format.
    :param df: dataframe to validate.
    :return: validated and formatted df - raise error if not valid.
    """
    if not isinstance(df.index, pandas.DatetimeIndex):
        raise TypeError(f'df.index is not a DatatimeIndex {df.index}')

    if df.index.name != "Timestamp":
        df.index.name = "Timestamp"

    if len(df.axes) < 2 or df.axes[1].name != "sensorId":
        df.rename_axis("sensorId", axis="columns", inplace=True)

    df = df.astype(float)

    return df


def df_to_csv(df: pandas.DataFrame) -> bytes:
    """
    Convert the DataFrame to a strongly formatted CSV.
    :param df: pandas DataFrame compatible with Wizata standards.
    :return: bytes containing the full CSV file.
    """
    b_buf = io.BytesIO()

    df.to_csv(b_buf,
              date_format="%Y-%m-%d-%H-%M-%S-%f",
              sep=",",
              decimal=".",
              encoding="utf-8")

    b_buf.seek(0)
    return b_buf.read()


def df_from_csv(b_data: bytes) -> pandas.DataFrame:
    """
    Convert the bytes to a pandas.DataFrame.
    :param b_data: bytes representing a CSV file.
    :return: pandas DataFrame formatted.
    """
    b_buf = io.BytesIO(b_data)

    df = pandas.read_csv(b_buf,
                         sep=",",
                         decimal=".",
                         encoding="utf-8")

    # detect timestamp column
    if "timestamp" in df.columns:
        df = df.rename(columns={'timestamp': 'Timestamp'})
    if "Timestamp" not in df.columns:
        raise ValueError('Cannot read dataframe as no Timestamp columns exists.')

    # detect timestamp type
    if df['Timestamp'].dtypes == 'int64':
        df['Timestamp'] = pandas.to_datetime(df['Timestamp'], unit="ms")
    elif df['Timestamp'].dtypes == 'object':
        df['Timestamp'] = df['Timestamp'].apply(lambda _: datetime.strptime(_, "%Y-%m-%d-%H-%M-%S-%f"))

    df = df.set_index('Timestamp')
    df.rename_axis("sensorId", axis="columns", inplace=True)

    return df


def df_from_json(json):
    """
    Convert a dictionary dataframe using JSON convention into a panda Dataframe.

    Dataframe must contain a timestamp column and be compatible to float data types.

    :param json: JSON formatted dataframe.
    :return: panda Dataframe
    """
    df = pandas.DataFrame.from_dict(json, orient='columns')
    df = df.set_index('Timestamp')

    if df.index.dtype == 'int64':
        df.index = [datetime.fromtimestamp(i) for i in (df.index / 1000).astype(int)]
        df.index.name = 'Timestamp'
    if not isinstance(df.index, pandas.DatetimeIndex):
        raise TypeError("Unexpected type {0}".format(df.index))

    df.rename_axis("sensorId", axis="columns", inplace=True)
    return df


def df_to_json(df: pandas.DataFrame):
    """
    Convert a panda Dataframe to a JSON compatible dictionary.

    Dataframe must be compatible to Wizata format using Timestamp index and float data types.

    :param df: panda Dataframe to convert.
    :return: dictionary representing JSON compatible dataframe.
    """
    df_json = {
        "Timestamp": list(df.index)
    }
    for col in list(df.columns):
        if col != 'Timestamp':
            df_json[col] = list(df[col].values.astype(float))
        else:
            df_json[col] = list(df[col].values)
    return df_json


def generate_epoch(formatted_string: str, now=None):
    """
    generate an epoch based on a formatted string (e.g. now+6h) - see documentation.
    * now = datetime.utcnow() can be override
    * units = 'y' = 365d, 'M'=30d , 'w'=7d , 'd'=24h , 'h'=60m, 'm'=60s , 's'=1000'ms'
    * operators = '+' or '-'
    :param formatted_string: formatted epoch representation using relative time.
    :param now: override now datetime.
    :return: epoch in ms.
    """
    if now is None:
        now = datetime.utcnow()

    pattern = r'^now([+-]\d+([yMwdHhms]{1,2}))?$'
    match = re.match(pattern, formatted_string)
    if not match:
        raise ValueError(f"invalid time delay format {formatted_string}")

    operator = match.group(1)[0] if match.group(1) else None
    value_unit_str = match.group(1)[1:] if match.group(1) else None

    if value_unit_str:
        value_str = re.search(r'\d+', value_unit_str).group()
        unit_str = re.search(r'[yMwdHhms]{1,2}', value_unit_str).group()

        value = int(value_str)

        if unit_str == 'y':
            delta = timedelta(days=365) * value
        elif unit_str == 'M':
            delta = timedelta(days=30) * value
        elif unit_str == 'w':
            delta = timedelta(days=7) * value
        elif unit_str == 'd':
            delta = timedelta(days=value)
        elif unit_str == 'H' or unit_str == 'h':
            delta = timedelta(hours=value)
        elif unit_str == 'm':
            delta = timedelta(minutes=value)
        elif unit_str == 's':
            delta = timedelta(seconds=value)
        elif unit_str == 'ms':
            delta = timedelta(milliseconds=value)
        else:
            raise ValueError("invalid time unit")

        if operator == '+':
            timestamp = now + delta
        elif operator == '-':
            timestamp = now - delta
        else:
            raise ValueError("invalid time delay format")
    else:
        timestamp = now

    epoch = datetime.utcfromtimestamp(0)
    timestamp_ms = int((timestamp - epoch).total_seconds() * 1000)
    return timestamp_ms
