# Cube Quant

Simple model to predict Rubiks cube solver performance on the [beginbot](https://twitch.tv/beginbot) Twitch stream.

Predictions are based on past performance as documented [here](https://docs.google.com/spreadsheets/d/1fR7O9sgzjfrYCJN2ITZzFYjHiSQUUf_DkuxsfbutZms/edit#gid=0)

## Usage

Ensure you have a `~/.google/credentials.json` file with valid credentials as per the [Google Sheets API Quickstart](https://developers.google.com/sheets/api/quickstart/python)

```sh
 ~/Documents/code/cube-quant  python3 predict.py         
Attempt #3 on a Monday will take: 43.0 seconds
```

## How it works

We fit a simple LinearRegression model on a Dataframe listing prior performance.

Features include:
- One-hot encoded day-of-the-week
- Attempt of the day (is this the first attempt? or the third?)

```
    attempt #  Monday  Tuesday  Wednesday  Thursday  Friday  Sunday
0           1       0        0          0         0       0       1
1           2       0        0          0         0       0       1
2           3       0        0          0         0       0       1
3           1       1        0          0         0       0       0
4           2       1        0          0         0       0       0
5           1       0        1          0         0       0       0
6           1       0        0          0         1       0       0
7           2       0        0          0         1       0       0
8           1       0        0          0         0       1       0
```

The model is re-fit with the latest data every time the script is run, so our predictions should get better over time.

Linear Regression is cool because the coefficients can tell us the relative importance of the features.

```
[('attempt #', 1.967471143756559), 
 ('Monday', 2.205753760055965),
 ('Tuesday', -2.3304477089891598),
 ('Wednesday', -6.658359566281916),
 ('Thursday', -1.9971143756558263),
 ('Friday', 7.599772647778948),
 ('Sunday', 1.180395243091989)]
```

Wednesdays result in the fastest times (6 seconds faster than than the y-intercept), while Fridays result in the slowest (7 seconds slower). This doesn't currently account fo sampling differences (e.g. beginbot cubes much less on Fridays than Wednesdays)
