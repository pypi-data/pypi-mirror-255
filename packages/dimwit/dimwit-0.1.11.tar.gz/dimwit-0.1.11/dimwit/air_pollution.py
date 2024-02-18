from datetime import datetime, timedelta
from tqdm import tqdm

import datetime as dat
import matplotlib.pyplot as plt
import numpy as np
import requests
import time


def get_openweather_air_pollution_data(
    ow_api_key,
    location,
    from_date,
    until_date,
    minute_usage,
    minute_quota,
    day_usage,
    day_quota,
):
    utc_tz = dat.timezone.utc
    # Ensure timezone info is correct at point of call.
    assert from_date.tzinfo == utc_tz and until_date.tzinfo == utc_tz
    start, end = int(from_date.timestamp()), int(until_date.timestamp())
    lat, lon = location

    base_uri = "http://api.openweathermap.org/data/2.5/air_pollution/history?"
    endpoint = base_uri + f"lat={lat}&lon={lon}&start={start}&end={end}"
    openweather_endpoint = endpoint + f"&appid={ow_api_key}"

    if minute_usage == minute_quota:
        secs = 60
        time.sleep(secs)
    if day_usage == day_quota:
        print("Day quota exceeded, wait until tomorrow.")
        return {}, minute_usage, day_usage
    openweather_response = requests.get(openweather_endpoint)

    minute_usage += 1
    day_usage += 1

    if openweather_response.status_code != 200:
        print(f"status: {openweather_response.status_code}")
        print(f"reason: {openweather_response.reason}")
        raise Exception(openweather_response.reason)

    return openweather_response.json(), minute_usage, day_usage


def get_sampled_openweather_air_pollution_data(
    location,
    from_date,
    until_date,
    minute_usage,
    minute_quota,
    day_usage,
    day_quota,
):
    try:
        result = get_openweather_air_pollution_data(
            location,
            from_date,
            datetime.now().astimezone(dat.timezone.utc),
            minute_usage,
            minute_quota,
            day_usage,
            day_quota,
        )
        ow_response, minute_usage, day_usage = result
    except Exception as e:
        _ = e
        empty_ow_response = {"list": [], "coord": {"lat": 300, "lon": 300}}
        return empty_ow_response

    decimated_data = [entry for entry in ow_response["list"][::2]]
    ow_response["list"] = decimated_data

    return ow_response


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


def get_air_pollution_notion_pages(
    db_id, headers, num_pages=None, specified_from_date=None
):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    results = get_notion_pages(
        url,
        headers.to_dict(),
        num_pages=num_pages,
        sort_by=[{"property": "dt", "direction": "ascending"}],
    )

    PIERHEAD_WHARF_LAT_LON = (51.50341932232918, -0.06113393431016998)

    if len(results) > 0:
        entry = extract_air_pollution_entry(len(results) - 1, results[-1])
        vals = entry[1]
        location = (vals[0], vals[1])
        from_date = entry[0]
    else:
        location = PIERHEAD_WHARF_LAT_LON
        # Currently we pass in a date, but ideally this would come from another
        # Notion DB that tracks the latest date for the given location.
        # Of course, having the override from a parameter is still useful.
        from_date = specified_from_date

        if from_date is None:
            msg = (
                "Error: date needs specifying if Notion Air Pollution ",
                "database is empty.",
            )
            raise Exception(msg)

    until_date = datetime.now().astimezone(dat.timezone.utc)
    minute_usage = 0
    minute_quota = 60 - 1
    day_usage = 0
    day_quota = 1000 - 1

    # Upload data to latest
    latest_air_pollution_data = get_sampled_openweather_air_pollution_data(
        location,
        from_date,
        until_date,
        minute_usage,
        minute_quota,
        day_usage,
        day_quota,
    )
    # If only one entry, that includes the latest timestamp from the data we
    # already have, so don't write it. Otherwise skip the head.
    if len(latest_air_pollution_data["list"]) > 1:
        tail = latest_air_pollution_data["list"][1:]
        latest_air_pollution_data["list"] = tail
        uploaded = write_openweather_data_to_notion(
            latest_air_pollution_data,
            db_id,
            headers.to_dict(),
        )
        if not uploaded:
            raise Exception("Failed to upload data, data not synchronised")

        # Now convert the latest AP data to the same format as the data from
        # Notion.
        coord = latest_air_pollution_data["coord"]
        latest_data_converted = [
            map_ow_entry_to_notion_entry(entry, coord)
            for entry in latest_air_pollution_data["list"]
        ]
    else:
        # Since the one entry duplicates the existing data we have, drop it.
        latest_data_converted = []

    # Should be safe, since ordering is temporal and ascending.
    return results + latest_data_converted


def get_start_of_week_for(ts):
    start_of_given_week = ts - timedelta(days=ts.weekday())
    midnight_delta = timedelta(
        hours=ts.hour,
        minutes=ts.minute,
        seconds=ts.second,
    )
    start_of_given_week_midnight = start_of_given_week - midnight_delta

    return start_of_given_week_midnight


def get_all_air_pollution_entries(pages):
    week_starts, timestamps, data = set(), [], []
    num_weeks = 0
    for idx, page in enumerate(pages):
        ts, vals = extract_air_pollution_entry(idx, page)
        week_starts.add(get_start_of_week_for(ts))
        if len(week_starts) > num_weeks:
            num_weeks = len(week_starts)
            timestamps.append([ts])
            data.append([vals])
        else:
            timestamps[-1].append(ts)
            data[-1].append(vals)

    week_starts = [[ws] for ws in sorted(list(week_starts))]
    return week_starts, timestamps, data


def write_openweather_data_to_notion(ow_data, db_id, headers):
    """
    Write the OpenWeather response `ow_data`, containing 1+ sequential entries
    for a given location, to the Notion database given by `db_id`.

    Note that this assumes `ow_data` has already been filtered temporally - all
    data will be uploaded in this function.
    """
    url = "https://api.notion.com/v1/pages"

    lat, lon = ow_data["coord"]["lat"], ow_data["coord"]["lon"]
    name_entry = {"title": [{"text": {"content": ""}}]}

    for entry in tqdm(ow_data["list"]):
        aqi = entry["main"]["aqi"]
        dt = entry["dt"]
        components = {k: {"number": v} for k, v in entry["components"].items()}

        iso_dt = dat.datetime.fromtimestamp(dt, dat.timezone.utc).isoformat()

        # Note: Avoid logging the full payload, as we want to avoid revealing
        # the database ID.
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "id": name_entry,
                "lat": {"number": lat},
                "lon": {"number": lon},
                "aqi": {"number": aqi},
                "dt": {"date": {"start": iso_dt, "end": None}},
                **components,
            },
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(response.status_code)
            print(response.reason)

    return True


def map_ow_entry_to_notion_entry(ow_entry, coord):
    return {
        "properties": {
            "dt": {
                "date": {
                    "start": dat.datetime.fromtimestamp(
                        ow_entry["dt"], dat.timezone.utc
                    ).isoformat()
                }
            },
            "lat": {"number": coord["lat"]},
            "lon": {"number": coord["lon"]},
            "aqi": {"number": ow_entry["main"]["aqi"]},
            "co": {"number": ow_entry["components"]["co"]},
            "no": {"number": ow_entry["components"]["no"]},
            "no2": {"number": ow_entry["components"]["no2"]},
            "o3": {"number": ow_entry["components"]["o3"]},
            "so2": {"number": ow_entry["components"]["so2"]},
            "pm2_5": {"number": ow_entry["components"]["pm2_5"]},
            "pm10": {"number": ow_entry["components"]["pm10"]},
            "nh3": {"number": ow_entry["components"]["nh3"]},
        }
    }


def extract_air_pollution_entry(idx, page):
    properties = page["properties"]
    if properties is None:
        raise Exception(f"Found empty entry at position {idx} (0-based index)")
    naive_dt = datetime.fromisoformat(properties["dt"]["date"]["start"])
    dt = naive_dt.replace(tzinfo=dat.timezone.utc)
    vals = [
        properties["lat"]["number"],
        properties["lon"]["number"],
        properties["aqi"]["number"],
        properties["co"]["number"],
        properties["no"]["number"],
        properties["no2"]["number"],
        properties["o3"]["number"],
        properties["so2"]["number"],
        properties["pm2_5"]["number"],
        properties["pm10"]["number"],
        properties["nh3"]["number"],
    ]
    return dt, vals


def filter_data_by_date(timestamps, values, date):
    ts = timestamps[np.asarray(timestamps >= date).nonzero()[0]]
    N = len(ts)
    vals = values[-N:]
    return ts, vals


def ap_data_over_period(
    data, timestamps, from_date, moving_average_window_size, events, title
):
    x, points = filter_data_by_date(data, timestamps, from_date)
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    ys = [points[:, 8], points[:, 9], points[:, 2]]
    labels = ["PM 2.5", "PM 10", "AQI"]
    window_size = moving_average_window_size

    for ax, y, label in zip(axes, ys, labels):
        ax.scatter(x, y, label=label, alpha=0.3)

        rolling_average = get_moving_average_trend(y, window_size)
        ax.plot(
            x,
            rolling_average,
            label=f"Rolling Avg ({window_size}) for {label}",
            color="green",
        )

        for event in events:
            event_date, event_colour, event_style, event_label = event
            ax.axvline(
                event_date,
                color=event_colour,
                linestyle=event_style,
                linewidth=1,
                label=event_label,
            )

        ax.legend()
    # Add a title to the entire figure
    fig.suptitle(title, fontsize=16)

    return fig, axes
