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
    for day in range(7):
        choice_timer = 0
        while choice_timer < 100000:
            choice_timer += 1
            if not diet:
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