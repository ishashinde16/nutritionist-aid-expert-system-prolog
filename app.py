from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)

app.secret_key = '610220f7b087781e7f5973e0ad0de7c0'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Collect form data
        session['user'] = {
            'name': request.form['name'],
            'age': request.form['age'],
            'gender': request.form['gender'],
            'weight': request.form['weight'],
            'height': request.form['height'],
            'activity': request.form['activity'],
            'goal': request.form['goal']
        }
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/menu')
def menu():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('menu.html', user=user)

@app.route('/substitution')
def substitution():
    return "Substitution Recommender Coming Soon!"

@app.route('/show_calorie_target')
def show_calorie_target():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return "Daily Calorie Target functionality coming soon!"

@app.route('/suggest_high_protein')
def suggest_high_protein():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return "High-Protein Meal Suggestions coming soon!"

@app.route('/generate_meal_plan')
def generate_meal_plan():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return "Full-Day Meal Plan generation coming soon!"

@app.route('/nutrient_choice')
def nutrient_choice():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return "Nutrient-Specific Meal options coming soon!"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
