# Importing essential libraries
from flask import Flask, render_template, request
import pickle
import numpy as np

# from collections import Mapping
# from collections.abc import Mapping

# Load the Random Forest Classifier model
filename = 'first-innings-score-lr-model.pkl'
regressor = pickle.load(open(filename, 'rb'))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    temp_array = []

    if request.method == 'POST':
        batting_team = request.form['batting-team']
        bowling_team = request.form['bowling-team']
        overs = float(request.form['overs'])
        runs = int(request.form['runs'])
        wickets = int(request.form['wickets'])
        runs_in_prev_5 = int(request.form['runs_in_prev_5'])
        wickets_in_prev_5 = int(request.form['wickets_in_prev_5'])

        # Use a dictionary to map team names to one-hot encoded values
        team_mapping = {
            'Chennai Super Kings': [1, 0, 0, 0, 0, 0, 0, 0],
            'Delhi Daredevils': [0, 1, 0, 0, 0, 0, 0, 0],
            'Kings XI Punjab': [0, 0, 1, 0, 0, 0, 0, 0],
            'Kolkata Knight Riders': [0, 0, 0, 1, 0, 0, 0, 0],
            'Mumbai Indians': [0, 0, 0, 0, 1, 0, 0, 0],
            'Rajasthan Royals': [0, 0, 0, 0, 0, 1, 0, 0],
            'Royal Challengers Bangalore': [0, 0, 0, 0, 0, 0, 1, 0],
            'Sunrisers Hyderabad': [0, 0, 0, 0, 0, 0, 0, 1],
        }

        temp_array += team_mapping.get(batting_team, [0, 0, 0, 0, 0, 0, 0, 0])
        temp_array += team_mapping.get(bowling_team, [0, 0, 0, 0, 0, 0, 0, 0])

        temp_array += [overs, runs, wickets, runs_in_prev_5, wickets_in_prev_5]

        data = np.array([temp_array])
        my_prediction = int(regressor.predict(data)[0])

        return render_template('result.html', lower_limit=my_prediction - 10, upper_limit=my_prediction + 5)

if __name__ == '__main__':
    app.run(debug=True)
