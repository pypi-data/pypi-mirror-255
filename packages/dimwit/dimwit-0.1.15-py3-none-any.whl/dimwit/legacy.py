import matplotlib.pyplot as plt
import numpy as np

from datetime import timedelta


def set_up_chart_metadata(week_starts, timestamps, data, weeks_to_plot):
    while len(week_starts) < weeks_to_plot:
        week_starts.append([])
    while len(timestamps) < weeks_to_plot:
        timestamps.append([])
    while len(data) < weeks_to_plot:
        data.append([])

    for week in range(len(week_starts)):
        if len(timestamps[week]) == 0:
            continue
        next_week = week_starts[week][0] + timedelta(weeks=1)
        week_starts[week].append(
            max(next_week, timestamps[week][-1]) + timedelta(hours=3)
        )

    ticks_per_week = []
    labels_per_week = []
    for week in range(weeks_to_plot):
        labels_per_week.append([])
        ticks_per_week.append([])
        # Want to range over the last k weeks, so the indexing needs to be from
        # the end less k, plus the current week to add ticks and labels for.
        idx = len(week_starts) - weeks_to_plot + week
        if week_starts[idx] == []:
            continue
        tick_start = week_starts[idx][0]
        label_start = week_starts[idx][0] + timedelta(hours=12)
        for i in range(7):
            current_tick = tick_start + timedelta(days=i)
            current_label = label_start + timedelta(days=i)
            ticks_per_week[-1].append(current_tick)
            labels_per_week[-1].append(current_label)

    return week_starts, timestamps, data, ticks_per_week, labels_per_week


def create_weekly_airflow_plots(
    data, timestamps, week_starts, labels_per_week, rows, cols
):
    # Create a figure with subplots
    fig, axes = plt.subplots(rows, cols, figsize=(9, 5 * rows + 2), sharey=True)
    weeks_to_plot = rows * cols

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Plot data for each week on separate axes
    for i, ax in enumerate(axes):
        if i < weeks_to_plot and len(data[i]) > 0:
            points = np.array(data[i])
            x = np.array(timestamps[i])
            ax.scatter(x, points[:, 0], label="Point 1", alpha=0.5)
            ax.scatter(x, points[:, 1], label="Point 2", alpha=0.5)
            ax.scatter(x, points[:, 2], label="Point 3", alpha=0.5)

            # Plot a line for the maximum of the points
            max_point = np.max(points, axis=1)
            ax.plot(x, max_point, label="Max", color="red")

            ax.set_xlim(week_starts[i])
            ax.set_xticklabels([days[label.weekday()] for label in labels_per_week[i]])

            ax.set_xlabel("Date")
            ax.set_ylabel("Air Outflow")
            # Rotate x-axis labels by 45 degrees
            ax.tick_params(axis="x", rotation=45)
            # Set the legend for the current axes
            ax.legend()
            formatted_date = week_starts[i][0].strftime("%Y-%m-%d")
            ax.set_title(f"{formatted_date}")

    # Add a title to the entire figure
    fig.suptitle("Air Outflow Over Time", fontsize=16, y=0.99)
    return fig, axes
