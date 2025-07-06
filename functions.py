def generate_exercise_plan(steps, sleep, calories, heart_rate, bmi):
    plan = []

    # Basic health-based conditions
    if steps < 5000:
        plan.append("30-minute brisk walk")
    else:
        plan.append("15-minute jog")

    if sleep < 6:
        plan.append("10-minute evening yoga")

    if calories > 2500:
        plan.append("20-minute HIIT workout")

    if heart_rate > 90:
        plan.append("Breathing and stretching exercises")

    if bmi > 25:
        plan.append("Full-body cardio (30 minutes)")

    if bmi < 18.5:
        plan.append("Strength training and protein-focused meals")

    # Goal-specific workouts
    

    return plan


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"