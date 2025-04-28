from flask import Flask, redirect, render_template, render_template_string, request, session, url_for
from pyswip import Prolog

app = Flask(__name__)
app.secret_key = '610220f7b087781e7f5973e0ad0de7c0'

prolog = Prolog()
prolog.consult("./prolog_logic/nutritionist.pl")

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

@app.route('/substitution', methods=['GET', 'POST'])
def substitution():
    # 1️⃣ Build the dropdown list of all foods
    raw_ings = set()
    for sol in prolog.query("substitute(Food,_)" ):
        raw_ings.add(sol['Food'])
    # Display‐friendly list: "butter_salted" → "Butter Salted"
    ingredients = sorted([ing.replace('_', ' ').title() for ing in raw_ings])

    substitutes = None
    ingredient = None

    if request.method == 'POST':
        # 2️⃣ Get the user’s choice
        raw = request.form['ingredient']               # e.g. "Butter Salted"
        ingredient = raw                              # for display

        # 3️⃣ Map back to Prolog atom format
        atom = raw.strip().lower().replace(' ', '_')   # "butter_salted"
        
        # 4️⃣ Query Prolog
        subs = []
        try:
            for sol in prolog.query(f"substitute('{atom}', Sub)"):
                subs.append(sol['Sub'])
        except Exception as e:
            print("Prolog substitution query error:", e)

        # 5️⃣ Make them pretty: "oil_sunflower" → "Oil Sunflower"
        substitutes = [s.replace('_', ' ').title() for s in subs]

    # 6️⃣ Always render with these three variables
    return render_template(
        'substitution.html',
        ingredients=ingredients,
        substitutes=substitutes,
        ingredient=ingredient
    )


# @app.route('/show_calorie_target')
# def show_calorie_target():
#     user = session.get('user')
#     if not user:
#         return redirect(url_for('login'))
#     return "Daily Calorie Target functionality coming soon!"

@app.route('/show_calorie_target')
def show_calorie_target():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    # Extract user info
    name = user['name']
    age = user['age']
    gender = user['gender']
    weight = user['weight']
    height = user['height']
    activity = user['activity']
    goal = user['goal']

    # First, assert user into Prolog
    try:
        prolog.assertz(f"user('{name}', {age}, '{gender}', {weight}, {height}, '{activity}', '{goal}')")
    except Exception as e:
        print(f"Prolog assertion error: {e}")

    # Now, query the calorie goal
    calories = None
    try:
        query = list(prolog.query(f"goal_calories('{name}', FinalCalories)"))
        if query:
            calories = int(query[0]['FinalCalories'])
    except Exception as e:
        print(f"Prolog query error: {e}")

    if calories is not None:
            return render_template('show_calorie_target.html',
                           user=user,
                           calories=calories)
    else:
        return "Could not calculate calories. Please check your information."

@app.route('/suggest_high_protein')
def suggest_high_protein():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    name = user['name']
    suggestions = []
    try:
        query = list(prolog.query(f"suggest_meal('{name}', Dish, Calories, Protein)"))
        for result in query:
            suggestions.append((result['Dish'], result['Calories'], result['Protein']))
    except Exception as e:
        print(f"Prolog high-protein query error: {e}")
    
    return render_template('suggest_high_protein.html',
                           suggestions=suggestions)


# @app.route('/generate_meal_plan')
# def generate_meal_plan():
#     user = session.get('user')
#     if not user:
#         return redirect(url_for('login'))
    
#     name = user['name']
#     meals = []
#     total_cals = 0
#     try:
#         query = list(prolog.query(f"meal_plan('{name}', Meals, TotalCals)"))
#         print("Meal Plan Query Result:", query)  # Debug print
#         if query:
#             meals = query[0]['Meals']
#             total_cals = query[0]['TotalCals']
#             meals = [dish for (dish, _, _) in meals]
#     except Exception as e:
#         print(f"Prolog meal plan query error: {e}")
    
#     return render_template('meal_plan.html', meals=meals, total_cals=total_cals)


# @app.route('/nutrient_choice', methods=['GET', 'POST'])
# def nutrient_choice():
#     dishes = []  # Initialize dishes to an empty list.
#     benefit = None  # Initialize benefit message
    
#     if request.method == 'POST':
#         choice = request.form['choice']
        
#         try:
#             if choice == 'high_fiber':
#                 query = list(prolog.query("food(Dish, _, Macros, _), member(fiber:Fiber, Macros), Fiber > 5"))
#                 dishes = [result['Dish'] for result in query]
#             elif choice == 'low_sodium':
#                 query = list(prolog.query("food(Dish, _, _, Micros), member(sodium:Sodium, Micros), Sodium < 100"))
#                 dishes = [result['Dish'] for result in query]
            
#             # 🔥 Fetch the corresponding benefit based on choice
#             benefit_query = list(prolog.query(f"benefit({choice}, Benefit)"))
#             if benefit_query:
#                 benefit = benefit_query[0]['Benefit']
        
#         except Exception as e:
#             print(f"Prolog nutrient choice query error: {e}")
#             dishes = []
#             benefit = None  # No benefit if error occurs

#         # Render the result after processing.
#         return render_template('nutrient_choice.html', dishes=dishes, benefit=benefit)
    
#     # Handle GET request: Render the form initially.
#     return render_template('nutrient_choice.html', dishes=dishes)

@app.route('/nutrient_choice', methods=['GET', 'POST'])
def nutrient_choice():
    dishes = []  # Initialize dishes to an empty list.

    if request.method == 'POST':
        goal = request.form['goal']
        
        try:
            if goal == 'improve_gut_health':
                # Improve Gut Health → High Fiber dishes
                query = list(prolog.query("food(Dish, _, Macros, _), member(fiber:Fiber, Macros), Fiber > 5"))
                dishes = [result['Dish'] for result in query]
            elif goal == 'improve_blood_pressure':
                # Improve BP → Low Sodium dishes
                query = list(prolog.query("food(Dish, _, _, Micros), member(sodium:Sodium, Micros), Sodium < 100"))
                dishes = [result['Dish'] for result in query]
        except Exception as e:
            print(f"Prolog nutrient choice query error: {e}")
            dishes = []  # Handle errors gracefully

        return render_template('nutrient_choice.html', dishes=dishes)
    
    # Handle GET request: Render the form initially.
    return render_template('nutrient_choice.html', dishes=dishes)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)