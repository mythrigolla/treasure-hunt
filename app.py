from flask import Flask, render_template, request, redirect, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'treasure_secret'

# Load CSV
df = pd.read_csv("questions.csv")

# Convert semicolon-separated options to list
def parse_options(opt):
    if isinstance(opt, str):
        return [x.strip() for x in opt.split(';')]
    return []

df['options'] = df['options'].apply(parse_options)

# Get questions by age group and sort by difficulty
def get_questions(age_group):
    filtered = df[df['age_group'].str.lower() == age_group.lower()].copy()
    difficulty_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
    filtered['difficulty_order'] = filtered['difficulty'].map(difficulty_order)
    filtered.sort_values('difficulty_order', inplace=True)
    filtered.drop('difficulty_order', axis=1, inplace=True)
    return filtered.to_dict(orient='records')

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        age = int(request.form['age'])
        if age <= 12:
            session['age_group'] = 'Kids'
        elif age <= 18:
            session['age_group'] = 'Teens'
        elif age <= 59:
            session['age_group'] = 'Adults'
        else:
            session['age_group'] = 'Seniors'

        session['questions'] = get_questions(session['age_group'])
        random.shuffle(session['questions'])
        session['current_index'] = 0
        session['score'] = 0
        session['progress'] = 0
        return redirect('/game')
    return render_template('index.html')

@app.route('/game', methods=['GET','POST'])
def game():
    if 'questions' not in session or session['current_index'] >= len(session['questions']):
        return redirect('/result')

    idx = session['current_index']
    question = session['questions'][idx]
    total_questions = len(session['questions'])
    progress_increment = 100 / total_questions

    if request.method == 'POST':
        selected = request.form.get('option')
        if selected == question['correct_answer']:
            session['score'] += 1
            session['progress'] += progress_increment
            session['feedback'] = "Correct! 🎉 Keep going!"
        else:
            session['progress'] -= progress_increment / 2
            if session['progress'] < 0:
                session['progress'] = 0
            session['feedback'] = f"Oops! The correct answer was: {question['correct_answer']} 😢"
        session['current_index'] += 1
        return redirect('/game')

    feedback = session.pop('feedback', '')
    return render_template(
        'game.html',
        question=question,
        options=question['options'],
        feedback=feedback,
        current_level=idx + 1,
        total=total_questions,
        progress=session['progress']
    )

@app.route('/result')
def result():
    score = session.get('score',0)
    total = len(session.get('questions',[]))
    return render_template('result.html', score=score, total=total)

if __name__ == '__main__':
    app.run(debug=True)
