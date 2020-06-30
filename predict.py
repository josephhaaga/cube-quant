from __future__ import print_function
import datetime
import pickle
import os.path
from pathlib import Path
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import datetime
import pandas as pd
import calendar
from sklearn import linear_model


logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('model_performance.log', encoding='utf-8')])

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SAMPLE_SPREADSHEET_ID = "1fR7O9sgzjfrYCJN2ITZzFYjHiSQUUf_DkuxsfbutZms"
SAMPLE_RANGE_NAME = "Sheet1!A3:B"


class GoogleSheets:
    home = str(Path.home())
    tokenpath = os.path.join(home, ".google", "token.pickle")
    creds = None

    def __init__(self):
        if os.path.exists(self.tokenpath):
            self.creds = self._load_token()

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(self.home, ".google", "credentials.json"), SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.tokenpath, "wb") as token:
                pickle.dump(self.creds, token)

        self.service = build("sheets", "v4", credentials=self.creds)

    def _load_token(self):
        with open(self.tokenpath, "rb") as token:
            return pickle.load(token)

    def get_values(
        self, spreadsheet_id=SAMPLE_SPREADSHEET_ID, sheet_range=SAMPLE_RANGE_NAME
    ):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=sheet_range)
            .execute()
        )
        return result.get("values", [])


def get_data_from_spreadsheet():
    sheets = GoogleSheets()
    cube_times = sheets.get_values()
    return pd.DataFrame(cube_times, columns=['Date of Attempt', 'Attempt Time'])

def engineer_model_features(a):
    a['date'] = pd.to_datetime(a['Date of Attempt'])
    a = a[['date', 'Attempt Time']]
    a['attempt #'] = a.groupby((a['date'] != a['date'].shift(1)).cumsum()).cumcount() + 1

    X = pd.get_dummies(a.date.dt.dayofweek.apply(lambda x: calendar.day_name[x]))
    X['attempt #'] = a['attempt #']
    X = X[['attempt #', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Sunday']]

    y = pd.to_datetime(a['Attempt Time']).dt.second
    return X, y

def fit_regression_model(X, y):
    reg = linear_model.LinearRegression()
    return reg.fit(X,y)

day_name_to_index = {}
for i in range(0,7):
    day_name_to_index[calendar.day_name[i]] = i

def generate_x(attempt_number, day):
    """Generate an X vector to run the predictive model."""
    guess = [0,0,0,0,0,0,0]
    guess[day_name_to_index[day]] = 1
    del guess[day_name_to_index['Saturday']] # no Saturday streams!
    return [attempt_number, *guess]

def build_model_and_predict():
    a = get_data_from_spreadsheet()
    today = datetime.datetime.now()
    attempts_today = a[a['Date of Attempt'] == today.strftime("%m/%d/%Y")]
    attempt_number = len(attempts_today) + 1
    day = calendar.day_name[today.weekday()]
    X, y = engineer_model_features(a)
    model = fit_regression_model(X, y)
    next_cube = generate_x(attempt_number, day)
    prediction = model.predict([next_cube])
    rounded_prediction = round(prediction[0])
    print(f"Attempt #{attempt_number} on a {day} will take: {rounded_prediction} seconds")
    logging.info(f"Predicting attempt #{attempt_number} on a {day} will take: {rounded_prediction} seconds")
    return prediction

if __name__ == "__main__":
    import sys
    a = build_model_and_predict()
