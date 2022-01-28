from random import choice

###############################################################################
####           FUNCTION THAT CALCULATES YOUR CALORIE INTAKE                ####
###############################################################################

def calories(age, gender, weight, height, activity, goal):
    if gender == 'male':
        static = 66
        hm =  5 * height
        wm = 13.7 * weight
        am = 6.8 * age
    elif gender == 'female':
        static = 655
        hm = 1.8 * height
        wm = 9.6 * weight
        am = 4.7 * age

    bmr_result = static + hm + wm - am
    bmr_result = int(bmr_result)

    if activity == 'none':
        consumption = 1.2 * bmr_result
    elif activity == 'light':
        consumption = 1.375 * bmr_result
    elif activity == 'medium':
        consumption = 1.55 * bmr_result
    elif activity == 'heavy':
        consumption = 1.725 * bmr_result
    elif activity == 'extreme':
        consumption = 1.9 * bmr_result

    if goal == 'lose':
        calories = consumption - 500
    elif goal == 'maintain':
        calories = consumption
    elif goal == 'gain':
        calories = consumption + 500

    return int(calories)

###############################################################################
####           FUNCTION THAT CREATES WEEK MEAL PLAN BASED ON               ####
####             YOUR CALORIE INTAKE AND OTHER PARAMETERS                  ####
###############################################################################

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
            return None

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