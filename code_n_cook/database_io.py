from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
db = SQLAlchemy(app)


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    calories = db.Column(db.Integer)
    if_vegan = db.Column(db.Boolean)
    if_vegetarian = db.Column(db.Boolean)
    ingredients = db.Column(db.String)
    weighted_ingredients = db.Column(db.String)
    recipe = db.Column(db.String)
    type = db.Column(db.String)


# tu robie slownik ktory uzywany jest w weekly menu

def sort_recipes():
    recipe_dict = {}

    breakfasts = Recipe.query.filter(Recipe.type=='breakfast').all()
    vege_breakfasts = Recipe.query.filter(Recipe.type=='breakfast', Recipe.if_vegetarian==True).all()
    vegan_breakfasts = Recipe.query.filter(Recipe.type=='breakfast', Recipe.if_vegan==True).all()

    snacks = Recipe.query.filter(Recipe.type=='snack').all()
    vege_snacks = Recipe.query.filter(Recipe.type=='snack', Recipe.if_vegetarian==True).all()
    vegan_snacks = Recipe.query.filter(Recipe.type=='snack', Recipe.if_vegan==True).all()

    lunches = Recipe.query.filter(Recipe.type=='lunch').all()
    vege_lunches = Recipe.query.filter(Recipe.type=='lunch', Recipe.if_vegetarian==True).all()
    vegan_lunches = Recipe.query.filter(Recipe.type=='lunch', Recipe.if_vegan==True).all()

    dinners = Recipe.query.filter(Recipe.type=='dinner').all()
    vege_dinners = Recipe.query.filter(Recipe.type=='dinner', Recipe.if_vegetarian==True).all()
    vegan_dinners = Recipe.query.filter(Recipe.type=='dinner', Recipe.if_vegan==True).all()

    suppers = Recipe.query.filter(Recipe.type=='supper').all()
    vege_suppers = Recipe.query.filter(Recipe.type=='supper', Recipe.if_vegetarian==True).all()
    vegan_suppers = Recipe.query.filter(Recipe.type=='supper', Recipe.if_vegan==True).all()

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
    recipe_dict['vegetarian_suppers'] =  vege_suppers
    recipe_dict['vegan_suppers'] = vegan_suppers
    return recipe_dict

# db.create_all()
# breakfast_recipes = Recipe.query.filter(Recipe.type=="breakfast").all()
# recipes = Recipe.query.all()

# @app.route("/")
# def index():
#     return breakfast_recipes[0].name


if __name__ == "__main__":
    app.run()
