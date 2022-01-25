from random import choice
# from my_project import Recipe #, sort_recipes

# Tutaj trzeba podmienic plik na ten w ktorym przechowywane jest
# zapotrzebowanie kaloryczne uzytkownika i dieta, podmienic kalorie, dieta
# from jakis_plik import kalorie, dieta
# caloric_demand = kalorie
# zaladam ze dieta uzytkownika to string 'vegan', 'vegetarian', a jej brak to None,
# w razie czego zakomentowane dalej fragmenty gdzie to sprawdzam
# user_diet = dieta


# Slownik przepisow z pliku ze zdefiniowana klasa Recipe (app)
# recipe_dict = sort_recipes()


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
        menu_list.append((breakfast, lunch, dinner, supper, snack))
    return menu_list
# zwracana lista-jadlospis


# if __name__ == '__main__':
#     menu_list = main(
#         caloric_demand, user_diet,
#         recipe_dict['breakfasts'], recipe_dict['lunches'],
#         recipe_dict['dinners'],
#         recipe_dict['suppers'], recipe_dict['snacks'],
#         recipe_dict['vegan_breakfasts'], recipe_dict['vegetarian_lunches'],
#         recipe_dict['vegetarian_dinners'], recipe_dict['vegetarian_suppers'],
#         recipe_dict['vegetarian_snacks'],
#         recipe_dict['vegan_breakfasts'], recipe_dict['vegan_lunches'],
#         recipe_dict['vegan_dinners'], recipe_dict['vegan_suppers'],
#         recipe_dict['vegan_snacks']
#     )
