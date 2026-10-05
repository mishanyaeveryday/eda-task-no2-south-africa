# EDA Task — NO2 Working Days in South Africa

## Summary

The challenged LLMs scored **0.64** on a 0-to-1 scale, the same score in all three runs on two different models.

The task asks the model to find the 5 working days of 2023 with the highest daylight NO2 average, using 47 readings
from three air-quality sensors in South Africa. The model has to build two independent variables from raw columns:
the type of day (working day or public holiday) and daylight (solar elevation at each sensor). The Google AI Studio
code sandbox has no `holidays` or `astral` package and no internet, so both have to be built by hand.

Both Gemini runs computed time zones, solar elevation and daily averages correctly, and the ChatGPT answer matches
the same ranking. Every model missed one fact: 15 December 2023 was a one-off public holiday declared by the
President after South Africa won the Rugby World Cup. That day lands at rank 1 of their answer and pushes the rest
down by one place.

## Challenged LLMs and settings

Two models were challenged: Gemini 3.5 Flash Lite in Google AI Studio with web search off, and GPT-5.6 Luna in
ChatGPT with internet access on.

| Run | Model | Where | Settings |
| --- | --- | --- | --- |
| 1 | Gemini 3.5 Flash Lite (`gemini-3.5-flash-lite`) | Google AI Studio | Thinking level Minimal; Code execution on; Grounding with Google Search off; Grounding with Google Maps off; URL context off |
| 2 | Gemini 3.5 Flash Lite (`gemini-3.5-flash-lite`) | Google AI Studio | Same as run 1, except Thinking level Medium |
| 3 | GPT-5.6 Luna | chatgpt.com | Code interpreter; internet access on |

The AI Studio sandbox runs Python 3.12 with pandas, numpy, scipy, pytz, tzdata and pyproj, but no `holidays`,
`astral`, `pvlib` or `ephem`. It has no internet: in run 1 the model tried `pip install holidays astral pytz` and
got a name-resolution error.

GPT-5.6 Luna had internet access and still missed the decree holiday. The ChatGPT interface showed only its first
cell and the final answer, so whether it searched at all is not visible.

## Dataset

`no2_readings.csv` is a synthetic file of 47 NO2 readings from 3 sensors in South Africa during 2023, with one
missing value.

| Column | Meaning |
| --- | --- |
| `sensor_id` | ZA01, ZA02, ZA03 |
| `station` | Johannesburg-Braamfontein, CapeTown-Foreshore, Durban-Umgeni |
| `latitude`, `longitude` | Sensor position, degrees (southern hemisphere) |
| `timestamp` | Reading time in UTC, ISO 8601 |
| `no2` | NO2 concentration, µg/m³ (one empty value) |

```csv
sensor_id,station,latitude,longitude,timestamp,no2
ZA02,CapeTown-Foreshore,-33.9179,18.4287,2023-02-14T16:30:00Z,128.4
ZA02,CapeTown-Foreshore,-33.9179,18.4287,2023-07-05T04:30:00Z,185.9
ZA03,Durban-Umgeni,-29.8046,31.0286,2023-11-22T12:30:00Z,
ZA02,CapeTown-Foreshore,-33.9179,18.4287,2023-12-15T09:30:00Z,95.16
```

The dependent variable is NO2. The independent variables are not columns: the model has to derive them.

| Variable | Role | Built from | Effect on NO2 in the data |
| --- | --- | --- | --- |
| `no2` | Dependent (Y) | Column | — |
| Type of day: working day, weekend, public holiday | Independent (X) | `timestamp` → local date (Africa/Johannesburg) → weekday + South African holiday calendar | Holidays and the Saturday carry the highest NO2 (86–102 µg/m³) |
| Daylight: yes / no | Independent (X) | `timestamp` + `latitude` + `longitude` → solar elevation | Night readings are spikes of 180–251 µg/m³; daylight readings are 32–132 µg/m³ |
| Station and season | Independent (X) | `sensor_id`, date | Decide when it is light: winter mornings in Cape Town are dark until about 07:50 local time |

Each of the 13 days has three daytime readings (09:30, 11:30, 13:30 UTC), one per sensor; selected days carry extra
night or evening readings.

## Task prompt

The full prompt is in [`prompt.md`](prompt.md):

```markdown
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
```

The example dates in the last line avoid 2 January 2023, which is a public holiday in South Africa, so the format
example gives no hint either way.

## Correct answer

The correct answer ([`answer.json`](answer.json)) is `["2023-07-18","2023-05-18","2023-02-14","2023-11-22","2023-09-12"]`.

| Date | Weekday | Status in South Africa | Daylight average, µg/m³ | Rank |
| --- | --- | --- | ---: | --- |
| 2023-06-17 | Sat | Weekend | 99.0 | excluded |
| 2023-12-15 | Fri | **Public holiday by Presidential decree** (Rugby World Cup win) | 95.0 | excluded |
| 2023-09-25 | Mon | Public holiday (Heritage Day 24 Sep fell on a Sunday) | 90.0 | excluded |
| 2023-01-02 | Mon | Public holiday (New Year 1 Jan fell on a Sunday) | 87.0 | excluded |
| 2023-07-18 | Tue | Working day (Mandela Day is not a public holiday) | 84.0 | 1 |
| 2023-05-18 | Thu | Working day (Ascension Day is not a public holiday) | 79.0 | 2 |
| 2023-02-14 | Tue | Working day | 73.0 | 3 |
| 2023-11-22 | Wed | Working day | 68.0 | 4 |
| 2023-09-12 | Tue | Working day | 63.0 | 5 |
| 2023-01-24 | Tue | Working day | 58.0 | 6 |
| 2023-04-25 | Tue | Working day | 53.0 | 7 |
| 2023-07-05 | Wed | Working day | 49.0 | 8 |
| 2023-12-13 | Wed | Working day | 47.0 | 9 |

The answer was checked with the `holidays` package (`country_holidays("ZA", years=2023)`, which lists 2023-12-15 as
"Public Holiday by Presidential Decree") and `astral.sun.elevation` without refraction. It gives the same top-7
ranking with the same averages to two decimals.

The nearest readings to the −0.833° threshold sit at +3.93° (2023-02-14 18:30 local, Johannesburg) and −4.94°
(2023-07-05 07:30 local, Cape Town). Any threshold between about −4.9° and +3.9° classifies every reading the same
way, so any correct solar formula gives the same answer.

## Measure definition

The score is 1 minus the total position penalty divided by its maximum n², so it is 1 for the exact answer, 0 when
nothing in it is right, and in between otherwise.

For reference list R and answer list A, both of length n (here n = 5), each answer position i gets a penalty:

```math
p_i = \begin{cases} |\,\mathrm{rank}_R(A_i) - i\,| & \text{if } A_i \in R \text{ and } A_i \text{ not seen earlier in } A \\ n & \text{otherwise (missing, repeated, or empty position)} \end{cases}
\qquad
\mathrm{score} = 1 - \frac{\sum_{i=1}^{n} p_i}{n^2}
```

Why this shape:

- The task asks for a sorted list, so order counts: a right item in the wrong place costs its displacement.
- A wrong item always costs more (n) than the largest possible displacement (n − 1), so including a right item
  never scores worse than leaving it out.
- A short, empty or padded answer cannot score well: empty positions and repeats cost n each.
- The maximum penalty is n × n, so the score stays in [0, 1].

| Reference | Answer | Penalties | Score |
| --- | --- | --- | ---: |
| [1, 3, 6, 11] (generic example, n = 4) | [1, 3, 7, 15] | 0 + 0 + 4 + 4 = 8 of 16 | 0.50 |
| correct answer of this task | same list | 0 | 1.00 |
| correct answer of this task | `[]` | 5 × 5 = 25 | 0.00 |
| correct answer of this task | same 5 dates in reverse order | 4 + 2 + 0 + 2 + 4 = 12 | 0.52 |
| correct answer of this task | model output (see below) | 5 + 1 + 1 + 1 + 1 = 9 | 0.64 |

Implementation: [`score.py`](score.py) (`python3 score.py '<model output>'`).

## Model outputs

All three runs printed the same five dates in the same order and scored 0.64.

| Run | Model | Printed answer | Score |
| --- | --- | --- | ---: |
| 1 | Gemini 3.5 Flash Lite, Thinking Minimal | `["2023-12-15", "2023-07-18", "2023-05-18", "2023-02-14", "2023-11-22"]` | 0.64 |
| 2 | Gemini 3.5 Flash Lite, Thinking Medium | `["2023-12-15", "2023-07-18", "2023-05-18", "2023-02-14", "2023-11-22"]` | 0.64 |
| 3 | GPT-5.6 Luna (ChatGPT) | `["2023-12-15","2023-07-18","2023-05-18","2023-02-14","2023-11-22"]` | 0.64 |

In both Gemini runs the answer is the stdout of executed code (`json.dumps`, hence the spaces); run 2 also repeated it
as its final text reply. The holiday list the model wrote by hand in run 1 is complete except for one date (the last
comment line is ours):

```python
sa_holidays_2023 = {
    date(2023, 1, 2),   # New Year's Day observed
    date(2023, 3, 21),  # Human Rights Day
    date(2023, 4, 7),   # Good Friday
    date(2023, 4, 10),  # Family Day
    date(2023, 4, 27),  # Freedom Day
    date(2023, 5, 1),   # Workers' Day
    date(2023, 6, 16),  # Youth Day
    date(2023, 8, 9),   # National Women's Day
    date(2023, 9, 25),  # Heritage Day observed
    date(2023, 12, 16), # Day of Reconciliation
    date(2023, 12, 25), # Christmas Day
    date(2023, 12, 26), # Day of Goodwill
}
# missing: date(2023, 12, 15)  public holiday by Presidential decree
```

Run 2 wrote the same 12 dates and went further: it printed a per-date check, but the check used the same incomplete
list and did not catch the mistake: `2023-12-15: Friday | Weekend? False | Holiday? False`.

The transcripts are in [`model_outputs/`](model_outputs/): full code cells for runs 1 and 2, the first cell and the
final answer for run 3.

## Why every model fails at the same point

The models rebuild the holiday calendar from rules, and 15 December 2023 cannot be derived from any rule.

- **What the models got right is exactly what rules give.** The Gemini runs took the statutory list from the Public
  Holidays Act and applied the Sunday-to-Monday rule (2 January, 25 September); all three answers correctly keep
  Mandela Day and Ascension Day as working days.
- **The missed day is a one-off.** The President declared 15 December 2023 a public holiday after the Springboks
  won the Rugby World Cup final on 28 October 2023. No rule produces it.
- **The common version of the list is the wrong one.** Calendar pages for "South Africa public holidays 2023" were
  mostly published before the decree, so the list without 15 December appears far more often in web text than the
  news of the decree. This is a frequency problem, not a knowledge-cutoff problem: 2023 is well inside every
  model's training period.
- **The models share a blind spot.** Gemini and ChatGPT learned from largely the same web text, so they make the
  same error rather than independent ones.
- **They did not check.** The sandbox cannot install `holidays`, so a check had to happen outside the code. Gemini
  ran with search off. GPT-5.6 Luna had internet access but still gave the wrong list. Only a Gemini app run that
  actually searched found the decree and scored 1.00.

In EDA terms, the models failed while building one independent variable, the type of day, and they were confident
about it: none of them flagged 15 December as unusual, even though its NO2 average (95.0 µg/m³) stands far above
every true working day.

## Other traps in the data

The dataset holds seven more traps; the models avoided all of them, so the 0.64 comes from one error only.

For each trap, the answer a model would print after falling into it was scored with `score.py`, to check that the
trap gives a score strictly between 0 and 1 and leaves a recognisable mark in the answer.

| Trap | Data | Score if missed | Observed |
| --- | --- | ---: | --- |
| Presidential-decree holiday | 2023-12-15 has the highest weekday NO2 | 0.64 | **missed in all 3 runs** |
| Sunday-to-Monday holidays | 2023-01-02 and 2023-09-25 have high NO2 | 0.36 | avoided |
| Days wrongly taken as holidays | Mandela Day and Ascension Day are ranks 1 and 2 | 0.36 | avoided |
| Weekend | Saturday 2023-06-17 has the highest NO2 overall | 0.64 | avoided |
| Fixed 06:00–18:00 window instead of solar elevation | dark winter morning spikes in Cape Town (2023-07-05); light summer evening readings at 18:30 (2023-02-14) | 0.72 | avoided |
| UTC and local time swapped in the solar formula | night spikes at 04:30 and 20:30 local time (2023-12-13) | 0.40 | avoided |
| No daylight filter | night spikes of 180–251 µg/m³ | 0.36 | avoided |
| Missing value | one empty `no2` | — | avoided |

The models used different solar formulas: run 1 the NOAA Solar Calculator through the Julian day, run 2 a simpler
fractional-year approximation (+4.00° and −4.92° for the two readings nearest the threshold, against +3.93° and
−4.94° in run 1). Both classified every reading the same way. The answer therefore depends on how the model reasons,
not on which correct formula it happens to pick.

## Limitations

The result holds for models that build the holiday list from memory; a model that actually searched solved the task.

- **One point of failure.** The whole penalty comes from a single fact. The other seven traps did not fire on these
  models, so the task tests careful rule-following plus one piece of knowledge that rules cannot produce.
- **Searching changes the outcome, having access does not.** In the Gemini app the model searched Google, found the
  decree and scored 1.00. GPT-5.6 Luna had internet access and still scored 0.64, like Gemini with search off.
- **The independent variables are named in the prompt.** The model has to build them, but it does not have to
  discover that they matter.
- **Synthetic data.** The values were designed for the test: daily averages are round numbers (84.0, 79.0, …) and
  the night spikes stand out. This makes the ground truth easy to verify, but the data does not look like a real
  monitoring export.
- **Small sample of runs.** Three runs on two models. More runs and more models would show how stable the 0.64 is.
- **Run 3 is only partly visible.** ChatGPT showed only the first cell and the final answer, so how it built the
  holiday list and the daylight filter cannot be checked.

Earlier versions of the task (closest sensor pairs on the WGS84 ellipsoid, interval logic with time zones, moving
sensors, Brandenburg holidays) were either solved fully by Gemini or failed for unrelated reasons: the model ran out
of code executions or printed an answer without running its code.

## Deliverables and reproduction

Only `no2_readings.csv` and the prompt are given to the LLM.

| Deliverable | File |
| --- | --- |
| Dataset | [`no2_readings.csv`](no2_readings.csv) (47 rows, 6 columns) |
| Task prompt | [`prompt.md`](prompt.md) |
| Model outputs | [`model_outputs/run1_gemini-3.5-flash-lite-minimal.md`](model_outputs/run1_gemini-3.5-flash-lite-minimal.md), [`run2_gemini-3.5-flash-lite.md`](model_outputs/run2_gemini-3.5-flash-lite.md), [`run3_gpt-5.6-luna.md`](model_outputs/run3_gpt-5.6-luna.md) |
| Measure definition | this README, section [Measure definition](#measure-definition); code in [`score.py`](score.py) |
| Correct answer | [`answer.json`](answer.json) |

To reproduce:

1. Give the LLM `no2_readings.csv` and the text of `prompt.md`, with code execution on (runs 1–2: web search off,
   Thinking level Minimal / Medium; run 3: internet access on).
2. `python3 score.py '<printed list>'` gives the score.

Do not upload `answer.json` to the LLM: it is the answer.
