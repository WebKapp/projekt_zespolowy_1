
from typing import List
from random import choice
from flask import Flask, redirect, url_for, render_template, request
import flask
from flask_sqlalchemy import SQLAlchemy
import json

# from calorie_intake import calories
# from weekly_menu import weekly_menu

app=Flask(__name__, template_folder='templates', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/malgorzatakozlowska/PZSP1/recipes_database.sqlite'
app.config["SQLACHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# region Database

class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    calories = db.Column(db.Integer)
    if_vegan = db.Column(db.Integer)
    if_vegetarian = db.Column(db.Integer)
    ingredients = db.Column(db.String)
    weighted_ingredients = db.Column(db.String)
    recipe = db.Column(db.String)
    type = db.Column(db.String)

    # def title(self):
    #     return self.name

    # def


# tu robie slownik ktory uzywany jest w weekly menu

def sort_recipes():
    recipe_dict = {}

    breakfasts = Recipe.query.filter(Recipe.type=='breakfast').all()
    vege_breakfasts = Recipe.query.filter((Recipe.type=='breakfast') & (Recipe.if_vegetarian==1)).all()
    vegan_breakfasts = Recipe.query.filter((Recipe.type=='breakfast') & (Recipe.if_vegan==1)).all()

    snacks = Recipe.query.filter(Recipe.type=='snack').all()
    vege_snacks = Recipe.query.filter((Recipe.type=='snack') & (Recipe.if_vegetarian==1)).all()
    vegan_snacks = Recipe.query.filter((Recipe.type=='snack') & (Recipe.if_vegan==1)).all()

    lunches = Recipe.query.filter(Recipe.type=='lunch').all()
    vege_lunches = Recipe.query.filter((Recipe.type=='lunch') & (Recipe.if_vegetarian==1)).all()
    vegan_lunches = Recipe.query.filter((Recipe.type=='lunch') & (Recipe.if_vegan==1)).all()

    dinners = Recipe.query.filter(Recipe.type=='dinner').all()
    vege_dinners = Recipe.query.filter((Recipe.type=='dinner') & (Recipe.if_vegetarian==1)).all()
    vegan_dinners = Recipe.query.filter((Recipe.type=='dinner') & (Recipe.if_vegan==1)).all()

    suppers = Recipe.query.filter(Recipe.type=='supper').all()
    vege_suppers = Recipe.query.filter((Recipe.type=='supper') & (Recipe.if_vegetarian==1)).all()
    vegan_suppers = Recipe.query.filter((Recipe.type=='supper') & (Recipe.if_vegan==1)).all()

    recipe_dict['breakfasts'] = breakfasts
    recipe_dict['vegetarian_breakfasts'] = vege_breakfasts
    recipe_dict['vegan_breakfasts'] = vegan_breakfasts
    recipe_dict['snacks'] = snacks
    recipe_dict['vegetarian_snacks'] = vege_snacks
    recipe_dict['vegan_snacks'] = vegan_snacks
    recipe_dict['lunches'] = lunches
    recipe_dict['vegetarian_lunches'] = vege_lunches
    recipe_dict['vegan_lunches'] = vegan_lunches
    recipe_dict['dinners'] = dinners
    recipe_dict['vegetarian_dinners'] = vege_dinners
    recipe_dict['vegan_dinners'] = vegan_dinners
    recipe_dict['suppers'] = suppers
    recipe_dict['vegetarian_suppers'] = vege_suppers
    recipe_dict['vegan_suppers'] = vegan_suppers
    return recipe_dict


class TooLittleProductsError(Exception):
    pass

def weekly_menu(
    calories, diet,
    breakfasts, lunches, dinners, suppers, snacks,
    vege_breakfasts, vege_lunches, vege_dinners, vege_suppers, vege_snacks,
    vegan_breakfasts, vegan_lunches, vegan_dinners, vegan_suppers, vegan_snacks,
):
    menu_list = []
    used_yesterday = []
    for _ in range(7):
        choice_timer = 0
        while choice_timer < 100000:
            choice_timer += 1
            if diet == 'standard':
                dinner = choice(dinners)
                lunch = choice(lunches)
                breakfast = choice(breakfasts)
                supper = choice(suppers)
                snack = choice(snacks)
            if diet == 'vegetarian':  # nazwa diety
                dinner = choice(vege_dinners)
                lunch = choice(vege_lunches)
                breakfast = choice(vege_breakfasts)
                supper = choice(vege_suppers)
                snack = choice(vege_snacks)
            if diet == 'vegan':  # nazwa diety
                dinner = choice(vegan_dinners)
                lunch = choice(vegan_lunches)
                breakfast = choice(vegan_breakfasts)
                supper = choice(vegan_suppers)
                snack = choice(vegan_snacks)
            if (dinner in used_yesterday or
                    lunch in used_yesterday or
                    snack in used_yesterday or
                    breakfast in used_yesterday or
                    supper in used_yesterday):
                continue

            d_kcal = dinner.calories
            l_kcal = lunch.calories
            b_kcal = breakfast.calories
            sp_kcal = supper.calories
            sc_kcal = snack.calories

            five_pct = calories*0.05
            sum_of_meals = d_kcal + l_kcal + b_kcal + sp_kcal + sc_kcal
            average_except_dinner = (sum_of_meals - d_kcal) / 4
            if (calories - five_pct < sum_of_meals < calories + five_pct and
                    d_kcal > average_except_dinner):
                break

        if choice_timer == 100000:
            raise TooLittleProductsError
            # mam nadzieje ze rozwiazanie z exception bedzie git

        used_yesterday.clear()
        used_yesterday.extend([breakfast, lunch, dinner, supper, snack])
        menu_list.append([breakfast, lunch, dinner, supper, snack])
    return menu_list

recipe_dict = sort_recipes()

week_menu = weekly_menu(2100, "standard", recipe_dict['breakfasts'], recipe_dict['lunches'],
        recipe_dict['dinners'],
        recipe_dict['suppers'], recipe_dict['snacks'],
        recipe_dict['vegan_breakfasts'], recipe_dict['vegetarian_lunches'],
        recipe_dict['vegetarian_dinners'], recipe_dict['vegetarian_suppers'],
        recipe_dict['vegetarian_snacks'],
        recipe_dict['vegan_breakfasts'], recipe_dict['vegan_lunches'],
        recipe_dict['vegan_dinners'], recipe_dict['vegan_suppers'],
        recipe_dict['vegan_snacks']
    )

print(week_menu)


def convert_to_json(recipes: List):
    recipes_list = []
    for recipe in recipes:
        recipe_dict = {
            "name": recipe.name.title(),
            "calories": recipe.calories,
            "ingredients": recipe.ingredients,
            "weighted_ingredients": recipe.weighted_ingredients,
            "recipe": recipe.recipe
        }
        recipes_list.append(recipe_dict)
    new_recipe_list = json.loads(recipes_list)
    return new_recipe_list


recipes_dict = sort_recipes()

def transform_to_dict(menu):
    meal_names = ["breakfast", "snack", "lunch", "dinner", "supper"]
    # week_menu = []
    day_index = 0
    meal = {}
    for each_day in menu:
        given_day = []
        for each_meal in each_day:
            recipe_dict = [
                            each_meal.name.title(),
                            each_meal.calories,
                            # "ingredients": each_meal.ingredients,
                            # "weighted_ingredients": each_meal.weighted_ingredients,
                            # "recipe": each_meal.recipe
                            ]
            given_day.append(recipe_dict)
        meal[meal_names[day_index]] = given_day
        # week_menu.append(meal)
        day_index += 1
    return meal


# print(convert_to_json(recipes_dict['breakfasts']))


# # for breakfast in vege_breakfasts:
# #     print(breakfast.name.title())
# print(recipes_dict["breakfasts"][0].name.title())

breakfasts = recipes_dict['breakfasts'][0:5]
snacks = recipes_dict['snacks'][0:5]
lunches = recipes_dict['lunches'][0:5]
dinners = recipes_dict['dinners'][0:5]
suppers = recipes_dict['suppers'][0:5]
sample_menu = [breakfasts, snacks, lunches, dinners, suppers]
# print(sample_menu)
# endregion

# print(transform_to_dict(sample_menu))


# def convert_meal_plan_for_query(menu):
#     print(menu)
#     meal_plan = []
#     for every_meal in menu:
#         meals = convert_to_json(every_meal)
#         print("")
#         print("")
#         print("")
#         print(meals)
#         meal_plan.append(meals)
#     # json_meal = json.dumps(meal_plan)
#     print("SPRAWDZAM!!!")
#     print("SPRAWDZAM!!!")
#     print(meal_plan)
#     return meal_plan
# print(sample_menu)
# sample_query = convert_meal_plan_for_query(sample_menu)
# print(sample_query)





@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/my_page", methods = ['GET'])
def my_page():
    return render_template("my_page.html")


@app.route("/meal_planner", methods = ['POST', 'GET'])
def meal_planner():

    if request.method == 'POST':
        name = request.form.get('projectFilePath')
        # weight = request.form.get('weight')
        # height = request.form.get('height')
        # age = request.form.get('age')
        # gender = request.form.get('gender')
        # activity  = request.form.get('activity')
        # goal = request.form.get('goal')
        # diet = request.form.get('diet')
        # calorie_intake = calories(age, gender, weight, height, activity, goal)
        # recipes = sort_recipes()
        # week_menu = weekly_menu(
        #                             calorie_intake, diet,
        #                             recipes['breakfasts'], recipes['lunches'],
        #                             recipes['dinners'],
        #                             recipes['suppers'], recipes['snacks'],
        #                             recipes['vegetarian_breakfasts'], recipes['vegetarian_lunches'],
        #                             recipes['vegetarian_dinners'], recipes['vegetarian_suppers'],
        #                             recipes['vegetarian_snacks'],
        #                             recipes['vegan_breakfasts'], recipes['vegan_lunches'],
        #                             recipes['vegan_dinners'], recipes['vegan_suppers'],
        #                             recipes['vegan_snacks']
        #                             )
        # name = "Gosia"
        calorie_intake = 2000
        # week_menu = "menu"
        query = transform_to_dict(sample_menu)
        # print(query)
        # print(sample_menu)


        dane = {"name": name, "calorie_intake": calorie_intake, "week_menu": query}
        res = flask.make_response(render_template('meal_planner.html', name=name,
                                calorie_intake=calorie_intake, week_menu=query))
        res.set_cookie("dane_meal_planner", value=json.dumps(dane))
        # print(res)
        return res


    if request.method == "GET":
        dane = request.cookies.get('dane_meal_planner')
        dane = json.loads(dane)
        week_menu = dane["week_menu"]

        return render_template('meal_planner.html', name=dane["name"],
                                calorie_intake=dane["calorie_intake"], week_menu=dane["week_menu"])

    # def week_menu(week_menu):
    #     dict_week_menu = json.loads(week_menu)
    #     return dict_week_menu

    #   [[<Recipe 1>, <Recipe 2>, <Recipe 6>, <Recipe 4>, <Recipe 12>], [<Recipe 7>, <Recipe 14>, <Recipe 19>, <Recipe 27>, <Recipe 28>], [<Recipe 5>, <Recipe 10>, <Recipe 13>, <Recipe 16>, <Recipe 23>], [<Recipe 8>, <Recipe 9>, <Recipe 11>, <Recipe 25>, <Recipe 29>], [<Recipe 6>, <Recipe 15>, <Recipe 17>, <Recipe 18>, <Recipe 20>]]
    # to jest sample_menu
    # def transform_to_dict(menu):
    #     week_menu = []
    #     for each_day in menu:
    #         give_day = []
    #         for each_meal in each_day:
    #             recipe_dict = {
    #                             "name": each_meal.name.title(),
    #                             "calories": each_meal.calories,
    #                             "ingredients": each_meal.ingredients,
    #                             "weighted_ingredients": each_meal.weighted_ingredients,
    #                             "recipe": each_meal.recipe
    #                             }
    #             give_day.append(recipe_dict)
    #     week_menu.append(give_day)
    #     return week_menu


@app.route("/my_fridge")
def my_fridge():
    return render_template("my_fridge.html")

@app.route("/recipe_inspiration")
def recipe_inspiration():
    return render_template("recipe_inspiration.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/pasta")
def pasta():
    return render_template("pasta.html")

@app.route("/pancakes")
def pancakes():
    pancakes = Recipe.query.filter(Recipe.id==2)

    return render_template("pancakes.html")

# pancakes = Recipe.query.filter(Recipe.id==2).first()
# print(pancakes.weighted_ingredients)

if __name__ == "__main__":
    app.run(debug=True)