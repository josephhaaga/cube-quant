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

The model is re-fit with the latest data every time the script is run, so our predictions should get better over time
