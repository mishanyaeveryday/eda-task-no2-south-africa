Consider the air-quality sensor dataset and find the 5 working days of 2023 with the highest average NO2 concentration during daylight.

To access the dataset use the file no2_readings.csv that I uploaded.
First load the dataset, check what the column names are, and then proceed with next actions.

Rules:
- Timestamps are in UTC. A reading belongs to the calendar date of its timestamp in local time (Africa/Johannesburg).
- A working day is a Monday–Friday that is not a public holiday in South Africa.
- A reading is taken during daylight if, at the reading's timestamp and the sensor's location, the geometric (unrefracted) elevation of the center of the sun is greater than −0.833° (the standard sunrise/sunset definition).
- Readings with a missing no2 value are ignored.
- The daylight average of a day is the mean of all daylight readings of all sensors on that day.

Write and run Python code to compute the answer.
Sort the days from the highest daylight average to the lowest.
Provide answer by printing the list of dates on stdout without any additional numbers/messages/comments/etc.:
"["2023-01-03","2023-01-04","2023-01-05","2023-01-06","2023-01-09"]"
