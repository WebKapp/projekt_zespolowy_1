from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/home/")
def home():
    return render_template("index.html")

@app.route("/my_page/")
def my_page():
    return render_template("my_page.html")

@app.route("/meal_planner/")
def meal_planner():
    return render_template("meal_planner.html")

@app.route("/my_fridge/")
def my_fridge():
    return render_template("my_fridge.html")

@app.route("/recipe_inspiration/")
def recipe_inspiration():
    return render_template("recipe_inspiration.html")

if __name__ == "__main__":
    app.run(debug=True)