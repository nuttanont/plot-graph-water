import json
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Configure matplotlib for Thai characters
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'Tahoma', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def load_water_level_graph(payload: dict) -> tuple[list[datetime], list[float]]:
	# Handle case where message is a JSON string (double-encoded)
	message = payload.get("message", {})
	if isinstance(message, str):
		message = json.loads(message)
	
	graph = (
		message
		.get("values", {})
		.get("water_level_graph", {})
		.get("0", {})
	)
	values = graph.get("value", [])
	times = graph.get("time", [])

	if not values or not times:
		raise ValueError("water_level_graph/0/value or time is missing")

	# Ensure same length
	count = min(len(values), len(times))
	values = values[:count]
	times = times[:count]

	# Convert Unix seconds to datetime
	time_points = [datetime.fromtimestamp(ts) for ts in times]
	return time_points, values


with open("response-01.json", "r", encoding="utf-8") as f:
	data = json.load(f)

times, water_levels = load_water_level_graph(data)

# Extract metadata for title
message = data.get("message", {})
if isinstance(message, str):
	message = json.loads(message)

code = message.get("code", "")
name = message.get("name", "")
basin_name = message.get("basin", {}).get("name", "")
title = f"{code} - {name} ({basin_name})"

plt.figure(figsize=(12, 5))
plt.plot(times, water_levels, linewidth=2, color='#1f77b4', marker='', linestyle='-')
plt.fill_between(times, water_levels, alpha=0.3, color='#1f77b4')
plt.title(title)
plt.xlabel("Time")
plt.ylabel("m")
plt.grid(True, alpha=0.3)

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
plt.tight_layout()

plt.savefig("station_703.png", dpi=150)
plt.close()