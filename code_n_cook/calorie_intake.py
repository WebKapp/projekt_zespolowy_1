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

print(calories(19, "female", 49, 167 , "medium", "lose"))