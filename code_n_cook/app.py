
from typing import List
from random import choice
from flask import Flask, redirect, url_for, render_template, request
import flask
from flask_sqlalchemy import SQLAlchemy
import json

# from calorie_intake import calories
# from weekly_menu import weekly_menu

app=Flask(__name__, template_folder='templates', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\krzys\\OneDrive\\Pulpit\\Test_bazy_danych\\data\\data.sqlite'
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
    pancakes = Recipe.query.filter(Recipe.id==2).first()

    return render_template("pancakes.html")

@app.route("/scrambled_eggs")
def scrambled_eggs():
    scrambled_eggs = Recipe.query.filter(Recipe.id==1).first()

    return render_template("scrambled_eggs.html")

@app.route("/banana_overnight_oats")
def banana_overnight_oats():
    banana_overnight_oats = Recipe.query.filter(Recipe.id==3).first()

    return render_template("banana_overnight_oats.html")

@app.route("/shakshuka")
def shakshuka():
    shakshuka = Recipe.query.filter(Recipe.id==4).first()

    return render_template("shakshuka.html")

@app.route("/homemade_granola_bars")
def homemade_granola_bars():
    homemade_granola_bars = Recipe.query.filter(Recipe.id==5).first()

    return render_template("homemade_granola_bars.html")

@app.route("/veggies_with_hummus")
def veggies_with_hummus():
    veggies_with_hummus = Recipe.query.filter(Recipe.id==6).first()

    return render_template("veggies_with_hummus.html")

@app.route("/protein_peanut_butter_shake")
def protein_peanut_butter_shake():
    homemade_granola_bars = Recipe.query.filter(Recipe.id==7).first()

    return render_template("protein_peanut_butter_shake.html")

@app.route("/creamy_tuscan_pasta")
def creamy_tuscan_pasta():
    creamy_tuscan_pasta = Recipe.query.filter(Recipe.id==8).first()

    return render_template("creamy_tuscan_pasta.html")

@app.route("/yellow_chicken_curry")
def yellow_chicken_curry():
    yellow_chicken_curry = Recipe.query.filter(Recipe.id==9).first()

    return render_template("yellow_chicken_curry.html")

@app.route("/pumpkin_soup")
def pumpkin_soup():
    pumpkin_soup = Recipe.query.filter(Recipe.id==10).first()

    return render_template("pumpkin_soup.html")

@app.route("/chinese_pork_dumplings")
def chinese_pork_dumplings():
    chinese_pork_dumplings = Recipe.query.filter(Recipe.id==11).first()

    return render_template("chinese_pork_dumplings.html")

@app.route("/homemade_cinnamon_cereal")
def homemade_cinnamon_cereal():
    homemade_cinnamon_cereal = Recipe.query.filter(Recipe.id==12).first()

    return render_template("homemade_cinnamon_cereal.html")

@app.route("/pasta_alla_cacio_e_peppe")
def pasta_alla_cacio_e_peppe():
    pasta_alla_cacio_e_peppe = Recipe.query.filter(Recipe.id==13).first()

    return render_template("pasta_alla_cacio_e_peppe.html")

@app.route("/kale_chips")
def kale_chips():
    kale_chips = Recipe.query.filter(Recipe.id==14).first()

    return render_template("kale_chips.html")

@app.route("/baked_brussel")
def baked_brussel():
    baked_brusell = Recipe.query.filter(Recipe.id==15).first()

    return render_template("baked_brussel.html")

@app.route("/vegan_tacos")
def vegan_tacos():
    vegan_tacos = Recipe.query.filter(Recipe.id==16).first()

    return render_template("vegan_tacos.html")

@app.route("/mac_and_cheese")
def mac_and_cheese():
    mac_and_cheese = Recipe.query.filter(Recipe.id==17).first()

    return render_template("mac_and_cheese.html")

@app.route("/apple_cinnamon_pancakes")
def apple_cinnamon_pancakes():
    apple_cinnamon_pancakes = Recipe.query.filter(Recipe.id==18).first()

    return render_template("apple_cinnamon_pancakes.html")

@app.route("/banana_shake")
def banana_shake():
    banana_shake = Recipe.query.filter(Recipe.id==19).first()

    return render_template("banana_shake.html")

@app.route("/avocado_and_black_bean_eggs")
def avocado_and_black_bean_eggs():
    avocado_and_black_bean_eggs = Recipe.query.filter(Recipe.id==20).first()

    return render_template("avocado_and_black_bean_eggs.html")

@app.route("/simple_fish_stew")
def simple_fish_stew():
    simple_fish_stew = Recipe.query.filter(Recipe.id==21).first()

    return render_template("simple_fish_stew.html")

@app.route("/bacon_tamato_avocado_sandwich")
def bacon_tamato_avocado_sandwich():
    bacon_tamato_avocado_sandwich = Recipe.query.filter(Recipe.id==22).first()

    return render_template("bacon_tamato_avocado_sandwich.html")

@app.route("/pasta_with_courgette_mozzarella")
def pasta_with_courgette_mozzarella():
    pasta_with_courgette_mozzarella = Recipe.query.filter(Recipe.id==23).first()

    return render_template("pasta_with_courgette_mozzarella.html")

@app.route("/baguette_with_brie")
def baguette_with_brie():
    baguette_with_brie = Recipe.query.filter(Recipe.id==24).first()

    return render_template("baguette_with_brie.html")

@app.route("/green_risotto")
def green_risotto():
    green_risotto = Recipe.query.filter(Recipe.id==25).first()

    return render_template("green_risotto.html")

@app.route("/oat_flakes")
def oat_flakes():
    oat_flakes = Recipe.query.filter(Recipe.id==26).first()

    return render_template("oat_flakes.html")

@app.route("/mango_sticky")
def mango_sticky():
    mango_sticky = Recipe.query.filter(Recipe.id==27).first()

    return render_template("mango_sticky.html")

@app.route("/olive_paste_sandwiches")
def olive_paste_sandwiches():
    olive_paste_sandwiches = Recipe.query.filter(Recipe.id==28).first()

    return render_template("olive_paste_sandwiches.html")

@app.route("/lesco")
def lesco():
    lesco = Recipe.query.filter(Recipe.id==29).first()

    return render_template("lesco.html")

@app.route("/vegan_pancakes")
def vegan_pancakes():
    vegan_pancakes = Recipe.query.filter(Recipe.id==30).first()

    return render_template("vegan_pancakes.html")

@app.route("/roasted_potato")
def roasted_potato():
    roasted_potato = Recipe.query.filter(Recipe.id==31).first()

    return render_template("roasted_potato.html")

@app.route("/aglio")
def aglio():
    aglio = Recipe.query.filter(Recipe.id==32).first()

    return render_template("aglio.html")

@app.route("/cocoa")
def cocoa():
    cocoa = Recipe.query.filter(Recipe.id==33).first()

    return render_template("cocoa.html")

@app.route("/pasta_with_ham")
def pasta_with_ham():
    pasta_with_ham = Recipe.query.filter(Recipe.id==34).first()

    return render_template("pasta_with_ham.html")





# pancakes = Recipe.query.filter(Recipe.id==2).first()
# print(pancakes.weighted_ingredients)

if __name__ == "__main__":
    app.run(debug=True)