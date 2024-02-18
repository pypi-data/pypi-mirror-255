import datetime as dat
import dateutil
import pandas as pd
import requests
from datetime import datetime


class NotionHeaders:
    def __init__(self, notion_token: str, notion_version: str = "2022-06-28"):
        self.__notion_token__ = notion_token
        self.__notion_version__ = notion_version

    def __repr__(self) -> str:
        return (
            "NotionHeaders(",
            'authorization="Bearer <SECRET_NOTION_TOKEN>", ',
            'content_type="application/json", ',
            f'notion_version="{self.__notion_version__}")',
        )

    def __str__(self) -> str:
        return (
            "NotionHeaders(",
            'authorization="Bearer <SECRET_NOTION_TOKEN>", ',
            'content_type="application/json", ',
            f'notion_version="{self.__notion_version__}")',
        )

    def to_dict(self) -> dict:
        return {
            "Authorization": "Bearer " + self.__notion_token__,
            "Content-Type": "application/json",
            "Notion-Version": f"{self.__notion_version__}",
        }


def get_notion_pages(url_endpoint, headers, num_pages=None, sort_by=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    get_all = num_pages is None
    # TODO: Logic for getting correct number of pages seems wrong. Check this.
    max_notion_pages_per_request = 100
    page_size = max_notion_pages_per_request if get_all else num_pages

    payload = {"page_size": page_size}
    if sort_by is not None:
        payload["sorts"] = sort_by

    response = requests.post(url_endpoint, json=payload, headers=headers)

    data = response.json()

    if response.status_code != 200:
        print(f"status: {response.status_code}")
        print(f"reason: {response.reason}")
        # Calling code can handle a failed request, so return an empty result.

    results = data.get("results", [])
    while data.get("has_more", False) and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        if sort_by is not None:
            payload["sorts"] = sort_by

        response = requests.post(url_endpoint, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


# TODO: Update this to fetch by date range rather than a prescribed number of
# pages and a single database. Provisonally, store all related DBs in a dict,
# fetch from the ones with the relevant data, and paginate on any edge cases.
def get_notion_pages_from_db(
    db_id,
    headers,
    sort_column: str | None = "date",
    sort_direction: str = "ascending",
    num_pages=None,
):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    # The 'date' column should be standard across all personal DBs in Notion.
    # However, it would be ideal to minimise the amount of data processing,
    # including sorting. If checking Notion personally, typically only need the
    # latest data, so having it stored in descending order makes sense. On the
    # other hand, most code assumes/prefers ascending order. Importantly, if
    # the data is always inserted in some sorted order, then re-sorting is
    # either trivial or not needed at all.
    # TODO: Decide how to deal with sorting.
    sort_by = [{"property": sort_column, "direction": sort_direction}]
    if sort_column is None:
        sort_by = None

    results = get_notion_pages(
        url,
        headers.to_dict(),
        num_pages=num_pages,
        sort_by=sort_by,
    )

    return results


def extract_airflow_entry(timestamps, data, idx, page):
    properties = page["properties"]
    if properties is None:
        raise Exception(f"Found empty entry at position {idx} (0-based index)")
    ts = dateutil.parser.isoparse(properties["date"]["date"]["start"])
    vals = [
        properties["recording_1"]["number"],
        properties["recording_2"]["number"],
        properties["recording_3"]["number"],
    ]
    timestamps.append(ts)
    data.append(vals)
    return None


def extract_categorical_entry(timestamps, data, idx, page):
    properties = page["properties"]
    if properties is None:
        raise Exception(f"Found empty entry at position {idx} (0-based index)")
    ts = dateutil.parser.isoparse(properties["date"]["date"]["start"])
    for item in properties["category"]["multi_select"]:
        timestamps.append(ts)
        data.append(item["name"])
    return None


def extract_weight_entry(timestamps, data, idx, page):
    properties = page["properties"]
    if properties is None:
        raise Exception(f"Found empty entry at position {idx} (0-based index)")
    ts = dateutil.parser.isoparse(properties["date"]["date"]["start"])
    weight = properties["weight"]["number"]
    categories = properties["category"]["multi_select"]
    timestamps.append(ts)
    data.append((weight, *categories))
    return None


def extract_sleep_entry(timestamps, data, idx, page):
    properties = page["properties"]
    if properties is None:
        raise Exception(f"Found empty entry at position {idx} (0-based index)")
    start = dateutil.parser.isoparse(properties["start_date"]["date"]["start"])
    end = dateutil.parser.isoparse(properties["end_date"]["date"]["start"])
    timestamps.append((start, end))
    duration = properties["duration"]["rich_text"][0]["text"]["content"]
    data.append(duration)
    return None


def get_all_entries(pages, add_data_entry):
    timestamps, data = [], []

    for idx, page in enumerate(pages):
        add_data_entry(timestamps, data, idx, page)

    return timestamps, data


def get_basic_sleep_dataframe(
    ts: list[tuple],
    durations: list[str],
    target_sleep_start: str = "22:30:00",
    target_sleep_end: str = "06:30:00",
):
    N = len(ts)
    starts, ends = zip(*ts)
    all_aligned = len(starts) == len(ends) == len(durations) == N
    if not all_aligned:
        raise Exception(
            f"Unaligned start ({len(starts)} values), "
            f"end ({len(ends)} values), "
            f"duration ({len(durations)} values) columns"
        )
    data = {
        "start_date": starts,
        "end_date": ends,
        "durations": durations,
        "target_sleep_start": [target_sleep_start] * N,
        "target_sleep_end": [target_sleep_end] * N,
    }
    df = pd.DataFrame(data)
    return df


def compute_rounded_matrix(ts, events, rounding_unit, rounding_size):
    """
    Compute a matrix where each (sorted, ascending) row corresponds to a
    timestamp, and the columns the types of events, rounding timestamps
    according to `rounding`.

    Each entry corresponds to the number of events of a particular type
    occurring to the nearest rounded timestamp.

    Any NaNs are converted to 0s.
    """
    data = {"value": [1] * len(events), "categories": events, "date": ts}
    df = pd.DataFrame(data)
    # Make sure to set the date column to datetimes recognisable by pandas.
    df["date"] = pd.to_datetime(df["date"], utc=True)
    rounding_string = str(rounding_size) + rounding_unit
    # Need to use dt field, or else more lengthy to work with native datetimes.
    df["date"] = df["date"].dt.round(rounding_string)
    df = df.pivot_table(
        index="date", columns="categories", values="value", aggfunc="sum"
    )
    return df.fillna(0)


def compute_moving_average_matrix(
    ts, events, rounding_unit, rounding_size, window_size
):
    df = compute_rounded_matrix(ts, events, rounding_unit, rounding_size)
    # TODO: Pad out df with entries prior to first row, to ensure correct
    # aggregation for first event.
    datetime.now(tz=dat.timezone.utc) - dat.timedelta()
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [[0] * len(df.columns)],
                columns=df.columns,
                index=[datetime.now(tz=dat.timezone.utc)],
            ),
        ]
    )
    categories = df.columns

    window_string = str(rounding_size) + rounding_unit
    dense_series = []
    for column in categories:
        dense_series.append(df[column].asfreq(freq=window_string).fillna(0))

    dense_df = pd.DataFrame(dense_series).T

    averaged_df = dense_df.rolling(window=window_size).mean().fillna(0)
    return averaged_df
