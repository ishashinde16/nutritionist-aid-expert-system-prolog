:- consult('food_db.pl').
:- consult('substitutions.pl').  
:- dynamic(user/7).

% ------------------ USER DATA ------------------

% user(Name, Age, Gender, Weight_kg, Height_cm, ActivityLevel, Goal).
user(isha, 22, female, 55, 165, moderately_active, weight_loss).
user(ravi, 30, male, 75, 175, sedentary, muscle_gain).

% ------------------ BMR + CALORIE GOAL ------------------

% Basal Metabolic Rate (BMR) - Mifflin St Jeor Formula
bmr(female, Weight, Height, Age, BMR) :-
    BMR is 655 + (9.6 * Weight) + (1.8 * Height) - (4.7 * Age).
bmr(male, Weight, Height, Age, BMR) :-
    BMR is 66 + (13.7 * Weight) + (5 * Height) - (6.8 * Age).

% Activity Multipliers
activity_multiplier(sedentary, 1.2).
activity_multiplier(lightly_active, 1.375).
activity_multiplier(moderately_active, 1.55).
activity_multiplier(very_active, 1.725).

% Total Daily Energy Expenditure
caloric_needs(User, Calories) :-
    user(User, Age, Gender, Weight, Height, Activity, _),
    bmr(Gender, Weight, Height, Age, BMR),
    activity_multiplier(Activity, Multiplier),
    Calories is BMR * Multiplier.

adjust_calories(weight_loss, Base, Adjusted) :- Adjusted is Base - 500.
adjust_calories(muscle_gain, Base, Adjusted) :- Adjusted is Base + 300.
adjust_calories(maintenance, Base, Base).

goal_calories(User, FinalCalories) :-
    caloric_needs(User, Base),
    user(User, _, _, _, _, _, Goal),
    adjust_calories(Goal, Base, FinalCalories).

% ------------------ MEAL SUGGESTIONS ------------------

% Suggest meals under calorie target with high protein
suggest_meal(User, Dish, Calories, Protein) :-
    goal_calories(User, MaxCal),
    food(Dish, Calories, Macros, _),
    Calories =< MaxCal,
    member(protein:Protein, Macros),
    Protein >= 10.

% ------------------ USER INTERFACE ------------------

start :-
    write('Enter your name: '), read(Name),
    write('Enter your age: '), read(Age),
    write('Gender (male/female): '), read(Gender),
    write('Weight (kg): '), read(Weight),
    write('Height (cm): '), read(Height),
    write('Activity (sedentary/lightly_active/moderately_active/very_active): '), read(Activity),
    write('Goal (weight_loss/maintenance/muscle_gain): '), read(Goal),
    assert(user(Name, Age, Gender, Weight, Height, Activity, Goal)),
    menu(Name).

menu(Name) :-
    nl, write('--- Nutritionist Aid Menu ---'), nl,
    write('1. Show daily calorie target'), nl,
    write('2. Suggest high-protein meals'), nl,
    write('3. Generate full-day meal plan'), nl,
    write('4. Show nutrient-specific meals'), nl,
    write('5. Find ingredient substitutes'), nl, 
    write('6. Exit'), nl,
    write('Choose an option: '), read(Choice),
    handle_choice(Choice, Name).

handle_choice(1, Name) :-
    goal_calories(Name, Cals),
    format('Your daily target calories: ~2f kcal~n', [Cals]),
    menu(Name).
handle_choice(2, Name) :-
    (suggest_meal(Name, Dish, Cal, Protein),
     format('~w: ~w kcal, ~w g protein~n', [Dish, Cal, Protein]),
     fail ; true),
    menu(Name).
handle_choice(4, Name) :-
    nutrition_goal(Name),
    menu(Name).
handle_choice(5, Name) :-             
    find_substitute,
    menu(Name).
handle_choice(6, _) :-
    write('Goodbye!'), nl.
handle_choice(_, Name) :-
    write('Invalid choice.'), nl,
    menu(Name).

print_meals([]).
print_meals([(Dish, Cal, Protein) | T]) :-
    format('~w - ~w kcal, ~w g protein~n', [Dish, Cal, Protein]),
    print_meals(T).

% ------------------ NUTRIENT GOAL FILTERS ------------------

% Nutrient-based filtering
nutrition_goal(_) :-
    write('Show (1) High Fiber or (2) Low Sodium dishes? '), read(Opt),
    (Opt = 1 -> high_fiber_dishes ;
     Opt = 2 -> low_sodium_dishes ;
     write('Invalid input.'), nl).

high_fiber_dishes :-
    food(Dish, _, Macros, _),
    member(fiber:F, Macros),
    F > 5,
    format('High fiber dish: ~w (~w g fiber)~n', [Dish, F]),
    fail.
high_fiber_dishes.

low_sodium_dishes :-
    food(Dish, _, _, Micros),
    member(sodium:S, Micros),
    S < 100,
    format('Low sodium dish: ~w (~w mg sodium)~n', [Dish, S]),
    fail.
low_sodium_dishes.

% ------------------ SUBSTITUTION FINDER ------------------

find_substitute :-
    write('Enter the ingredient you want to substitute (use underscores for spaces, e.g., butter_salted): '),
    read(UserInput),
    atom_string(UserInput, UserInputStr),
    replace_underscores_with_comma_underscore(UserInputStr, FormattedStr),
    atom_string(FormattedAtom, FormattedStr),
    findall(Sub, substitute(FormattedAtom, Sub), Substitutes),
    (   Substitutes \= []
    ->  (   format('Substitutes for ~w:~n', [FormattedAtom]),
            print_substitutes(Substitutes)
        )
    ;   format('Sorry, no substitutes found for ~w.~n', [FormattedAtom])
    ).

print_substitutes([]).
print_substitutes([Sub | Rest]) :-
    format('- ~w~n', [Sub]),
    print_substitutes(Rest).

% Replace underscores _ with comma + underscore ,_
replace_underscores_with_comma_underscore(Input, Output) :-
    split_string(Input, "_", "", List),
    atomic_list_concat(List, ',_', Output).


% Define benefit rules:
benefit(low_sodium, 'Maintaining Blood Pressure Levels').
benefit(high_fiber, 'Gut Health Improvement').