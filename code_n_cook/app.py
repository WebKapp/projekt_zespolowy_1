###############################################################################
####                                 IMPORTS                               ####
###############################################################################
from typing import List
from random import choice
from flask import Flask, redirect, url_for, render_template, request
import flask
from flask_sqlalchemy import SQLAlchemy
from calorie_intake import calories
# from weight_code.wifi_data import send_data

###############################################################################
####                        WEB APP CONFIGURATION                          ####
###############################################################################

app=Flask(__name__, template_folder='templates', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/malgorzatakozlowska/PZSP1/recipes_database_with_url.sqlite'
app.config["SQLACHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


###############################################################################
####                  DATA EXTRACTION FROM DATABASE                        ####
###############################################################################

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
    url = db.Column(db.String)



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


###############################################################################
####           FUNCTION THAT CREATES WEEK MEAL PLAN BASED ON               ####
####             YOUR CALORIE INTAKE AND OTHER PARAMETERS                  ####
###############################################################################


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
    breakfast_list = []
    lunches_list = []
    dinners_list = []
    suppers_list = []
    snacks_list = []
    for _ in range(5):
        choice_timer = 0
        while choice_timer < 100000:
            choice_timer += 1
            if diet == 'standard':
                dinner = choice(dinners)
                lunch = choice(lunches)
                breakfast = choice(breakfasts)
                supper = choice(suppers)
                snack = choice(snacks)
            if diet == 'vegetarian':
                dinner = choice(vege_dinners)
                lunch = choice(vege_lunches)
                breakfast = choice(vege_breakfasts)
                supper = choice(vege_suppers)
                snack = choice(vege_snacks)
            if diet == 'vegan':
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

        used_yesterday.clear()
        used_yesterday.extend([breakfast, lunch, dinner, supper, snack])
        breakfast_list.append(breakfast)
        lunches_list.append(lunch)
        dinners_list.append(dinner)
        suppers_list.append(supper)
        snacks_list.append(snack)
    menu_list = [
        breakfast_list, lunches_list, dinners_list, suppers_list, snacks_list
    ]
    return menu_list


###############################################################################
####                     MAIN ROUTES OF THE WEB APP                        ####
###############################################################################


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
        name = request.form.get('name')
        weight_data = request.form.get('weight')
        weight = int(weight_data)
        height_data = request.form.get('height')
        height = int(height_data)
        age_data = request.form.get('age')
        age = int(age_data)
        gender = request.form.get('gender')
        activity  = request.form.get('activity')
        goal = request.form.get('goal')
        diet = request.form.get('diet')
        calorie_intake = calories(age, gender, weight, height, activity, goal)
        recipes = sort_recipes()
        week_menu = weekly_menu(
                                    calorie_intake, diet,
                                    recipes['breakfasts'], recipes['lunches'],
                                    recipes['dinners'],
                                    recipes['suppers'], recipes['snacks'],
                                    recipes['vegetarian_breakfasts'], recipes['vegetarian_lunches'],
                                    recipes['vegetarian_dinners'], recipes['vegetarian_suppers'],
                                    recipes['vegetarian_snacks'],
                                    recipes['vegan_breakfasts'], recipes['vegan_lunches'],
                                    recipes['vegan_dinners'], recipes['vegan_suppers'],
                                    recipes['vegan_snacks']
                                    )


        result = flask.make_response(render_template('meal_planner.html', name=name,
                                calorie_intake=calorie_intake, week_menu=week_menu))
        return result


    if request.method == "GET":
        return render_template('message.html')

###############################################################################
####                     ROUTES TO OTHER PAGES                             ####
###############################################################################

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

###############################################################################
####                     RECIPES FROM THE DATABASE                         ####
###############################################################################
@app.route("/pancakes")
def pancakes():
    pancakes = Recipe.query.filter(Recipe.id==2).first()
    # send_data(pancakes.weighted_ingredients)

    return render_template("pancakes.html")

@app.route("/scrambled_eggs")
def scrambled_eggs():
    scrambled_eggs = Recipe.query.filter(Recipe.id==1).first()
    # send_data(scrambled_eggs.weighted_ingredients)

    return render_template("scrambled_eggs.html")

@app.route("/banana_overnight_oats")
def banana_overnight_oats():
    banana_overnight_oats = Recipe.query.filter(Recipe.id==3).first()
    # send_data(banana_overnight_oats.weighted_ingredients)

    return render_template("banana_overnight_oats.html")

@app.route("/shakshuka")
def shakshuka():
    shakshuka = Recipe.query.filter(Recipe.id==4).first()
    # send_data(shakshuka.weighted_ingredients)

    return render_template("shakshuka.html")

@app.route("/homemade_granola_bars")
def homemade_granola_bars():
    homemade_granola_bars = Recipe.query.filter(Recipe.id==5).first()
    # send_data(homemade_granola_bars.weighted_ingredients)

    return render_template("homemade_granola_bars.html")

@app.route("/veggies_with_hummus")
def veggies_with_hummus():
    # veggies_with_hummus = Recipe.query.filter(Recipe.id==6).first()
    # # send_data(veggies_with_hummus.weighted_ingredients)

    return render_template("veggies_with_hummus.html")

@app.route("/protein_peanut_butter_shake")
def protein_peanut_butter_shake():
    homemade_granola_bars = Recipe.query.filter(Recipe.id==7).first()
    # send_data(homemade_granola_bars.weighted_ingredients)

    return render_template("protein_peanut_butter_shake.html")

@app.route("/creamy_tuscan_pasta")
def creamy_tuscan_pasta():
    creamy_tuscan_pasta = Recipe.query.filter(Recipe.id==8).first()
    # send_data(creamy_tuscan_pasta.weighted_ingredients)

    return render_template("creamy_tuscan_pasta.html")

@app.route("/yellow_chicken_curry")
def yellow_chicken_curry():
    yellow_chicken_curry = Recipe.query.filter(Recipe.id==9).first()
    # send_data(yellow_chicken_curry.weighted_ingredients)

    return render_template("yellow_chicken_curry.html")

@app.route("/pumpkin_soup")
def pumpkin_soup():
    pumpkin_soup = Recipe.query.filter(Recipe.id==10).first()
    # send_data(pumpkin_soup.weighted_ingredients)

    return render_template("pumpkin_soup.html")

@app.route("/chinese_pork_dumplings")
def chinese_pork_dumplings():
    chinese_pork_dumplings = Recipe.query.filter(Recipe.id==11).first()
    # send_data(chinese_pork_dumplings.weighted_ingredients)

    return render_template("chinese_pork_dumplings.html")

@app.route("/homemade_cinnamon_cereal")
def homemade_cinnamon_cereal():
    homemade_cinnamon_cereal = Recipe.query.filter(Recipe.id==12).first()
    # send_data(homemade_cinnamon_cereal.weighted_ingredients)

    return render_template("homemade_cinnamon_cereal.html")

@app.route("/pasta_alla_cacio_e_peppe")
def pasta_alla_cacio_e_peppe():
    pasta_alla_cacio_e_peppe = Recipe.query.filter(Recipe.id==13).first()
    # send_data(pasta_alla_cacio_e_peppe.weighted_ingredients)

    return render_template("pasta_alla_cacio_e_peppe.html")

@app.route("/kale_chips")
def kale_chips():
    kale_chips = Recipe.query.filter(Recipe.id==14).first()
    # send_data(kale_chips.weighted_ingredients)

    return render_template("kale_chips.html")

@app.route("/baked_brussel")
def baked_brussel():
    baked_brusell = Recipe.query.filter(Recipe.id==15).first()
    # send_data(baked_brusell.weighted_ingredients)

    return render_template("baked_brussel.html")

@app.route("/vegan_tacos")
def vegan_tacos():
    vegan_tacos = Recipe.query.filter(Recipe.id==16).first()
    # send_data(vegan_tacos.weighted_ingredients)

    return render_template("vegan_tacos.html")

@app.route("/mac_and_cheese")
def mac_and_cheese():
    mac_and_cheese = Recipe.query.filter(Recipe.id==17).first()
    # send_data(mac_and_cheese.weighted_ingredients)

    return render_template("mac_and_cheese.html")

@app.route("/apple_cinnamon_pancakes")
def apple_cinnamon_pancakes():
    apple_cinnamon_pancakes = Recipe.query.filter(Recipe.id==18).first()
    # send_data(apple_cinnamon_pancakes.weighted_ingredients)

    return render_template("apple_cinnamon_pancakes.html")

@app.route("/banana_shake")
def banana_shake():
    banana_shake = Recipe.query.filter(Recipe.id==19).first()
    # send_data(banana_shake.weighted_ingredients)

    return render_template("banana_shake.html")

@app.route("/avocado_and_black_bean_eggs")
def avocado_and_black_bean_eggs():
    avocado_and_black_bean_eggs = Recipe.query.filter(Recipe.id==20).first()
    # send_data(avocado_and_black_bean_eggs.weighted_ingredients)

    return render_template("avocado_and_black_bean_eggs.html")

@app.route("/simple_fish_stew")
def simple_fish_stew():
    simple_fish_stew = Recipe.query.filter(Recipe.id==21).first()
    # send_data(simple_fish_stew.weighted_ingredients)

    return render_template("simple_fish_stew.html")

@app.route("/bacon_tamato_avocado_sandwich")
def bacon_tamato_avocado_sandwich():
    bacon_tamato_avocado_sandwich = Recipe.query.filter(Recipe.id==22).first()
    # send_data(bacon_tamato_avocado_sandwich.weighted_ingredients)

    return render_template("bacon_tamato_avocado_sandwich.html")

@app.route("/pasta_with_courgette_mozzarella")
def pasta_with_courgette_mozzarella():
    pasta_with_courgette_mozzarella = Recipe.query.filter(Recipe.id==23).first()
    # send_data(pasta_with_courgette_mozzarella.weighted_ingredients)

    return render_template("pasta_with_courgette_mozzarella.html")

@app.route("/baguette_with_brie")
def baguette_with_brie():
    baguette_with_brie = Recipe.query.filter(Recipe.id==24).first()
    # send_data(baguette_with_brie.weighted_ingredients)

    return render_template("baguette_with_brie.html")

@app.route("/green_risotto")
def green_risotto():
    green_risotto = Recipe.query.filter(Recipe.id==25).first()
    # send_data(green_risotto.weighted_ingredients)

    return render_template("green_risotto.html")

@app.route("/oat_flakes")
def oat_flakes():
    oat_flakes = Recipe.query.filter(Recipe.id==26).first()
    # send_data(oat_flakes.weighted_ingredients)

    return render_template("oat_flakes.html")

@app.route("/mango_sticky")
def mango_sticky():
    mango_sticky = Recipe.query.filter(Recipe.id==27).first()
    # send_data(mango_sticky.weighted_ingredients)

    return render_template("mango_sticky.html")

@app.route("/olive_paste_sandwiches")
def olive_paste_sandwiches():
    olive_paste_sandwiches = Recipe.query.filter(Recipe.id==28).first()
    # send_data(olive_paste_sandwiches.weighted_ingredients)

    return render_template("olive_paste_sandwiches.html")

@app.route("/lesco")
def lesco():
    lesco = Recipe.query.filter(Recipe.id==29).first()
    # send_data(lesco.weighted_ingredients)

    return render_template("lesco.html")

@app.route("/vegan_pancakes")
def vegan_pancakes():
    vegan_pancakes = Recipe.query.filter(Recipe.id==30).first()
    # send_data(vegan_pancakes.weighted_ingredients)

    return render_template("vegan_pancakes.html")

@app.route("/roasted_potato")
def roasted_potato():
    roasted_potato = Recipe.query.filter(Recipe.id==31).first()
    # send_data(roasted_potato.weighted_ingredients)

    return render_template("roasted_potato.html")

@app.route("/aglio")
def aglio():
    aglio = Recipe.query.filter(Recipe.id==32).first()
    # send_data(aglio.weighted_ingredients)

    return render_template("aglio.html")

@app.route("/cocoa")
def cocoa():
    cocoa = Recipe.query.filter(Recipe.id==33).first()
    # send_data(cocoa.weighted_ingredients)

    return render_template("cocoa.html")

@app.route("/pasta_with_ham")
def pasta_with_ham():
    pasta_with_ham = Recipe.query.filter(Recipe.id==34).first()
    # send_data(pasta_with_ham.weighted_ingredients)

    return render_template("pasta_with_ham.html")

@app.route("/french_toast_with_dried_apricots")
def french_toast_with_dried_apricots():
    french_toast_with_dried_apricots = Recipe.query.filter(Recipe.id==36).first()
    # send_data(pasta_with_ham.weighted_ingredients)

    return render_template("french_toast_with_dried_apricots.html")


@app.route("/chicory_salad")
def chicory_salad():
    chicory_salad = Recipe.query.filter(Recipe.id==35).first()
    # send_data(pasta_with_ham.weighted_ingredients)

    return render_template("chicory_salad.html")


if __name__ == "__main__":
    app.run(debug=True)
