"""Tools for nutrition planning used by the nutritionist agent."""

import json
from datetime import date
from typing import Any

from fitagent.models.nutrition import (
    NutritionGoal,
    NutritionPlan,
    MacroBreakdown,
    MealPlan,
    Meal,
    MealTiming,
    TrainingDayType,
)


def calculate_macros(
    weight_kg: float,
    goal: str,
    training_day_type: str,
    activity_level: str = "moderate",
    age: int = None,
    height_cm: float = None,
    sex: str = "male",
) -> dict[str, Any]:
    """Calculate macronutrient targets based on athlete profile and goals.

    Args:
        weight_kg: Athlete's current weight in kilograms.
        goal: Nutrition goal (fat_loss, muscle_gain, performance_optimization, body_recomposition).
        training_day_type: Type of training day (rest_day, easy_day, moderate_day, hard_day, long_session_day).
        activity_level: General activity level (sedentary, light, moderate, active, very_active).
        age: Athlete's age in years (optional, improves accuracy).
        height_cm: Athlete's height in centimeters (optional, improves accuracy).
        sex: Biological sex for BMR calculation (male/female).

    Returns:
        Dictionary containing calculated macro targets and rationale.
    """
    # Calculate BMR using Mifflin-St Jeor
    if age and height_cm:
        if sex == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 22 * weight_kg  # Simplified estimate

    # Activity multipliers
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    tdee = bmr * activity_multipliers.get(activity_level, 1.55)

    # Training day adjustments
    day_adjustments = {
        "rest_day": -200,
        "easy_day": 0,
        "moderate_day": 200,
        "hard_day": 400,
        "long_session_day": 600,
        "race_day": 800,
    }
    day_calories = day_adjustments.get(training_day_type, 0)

    # Goal-based adjustments
    goal_config = {
        "fat_loss": {"calorie_adjustment": -400, "protein_per_kg": 2.2, "fat_percent": 0.25},
        "muscle_gain": {"calorie_adjustment": 300, "protein_per_kg": 2.0, "fat_percent": 0.25},
        "performance_optimization": {"calorie_adjustment": 0, "protein_per_kg": 1.8, "fat_percent": 0.28},
        "body_recomposition": {"calorie_adjustment": -200, "protein_per_kg": 2.2, "fat_percent": 0.25},
    }

    config = goal_config.get(goal, goal_config["performance_optimization"])

    total_calories = int(tdee + config["calorie_adjustment"] + day_calories)
    protein_grams = int(weight_kg * config["protein_per_kg"])
    fat_grams = int((total_calories * config["fat_percent"]) / 9)
    carbs_grams = int((total_calories - (protein_grams * 4) - (fat_grams * 9)) / 4)

    return {
        "calories": total_calories,
        "protein_grams": protein_grams,
        "carbs_grams": carbs_grams,
        "fat_grams": fat_grams,
        "protein_per_kg": config["protein_per_kg"],
        "bmr_estimate": int(bmr),
        "tdee_estimate": int(tdee),
        "training_day_type": training_day_type,
        "goal": goal,
        "rationale": (
            f"Based on {weight_kg}kg body weight with goal '{goal}' on a {training_day_type}. "
            f"Protein set at {config['protein_per_kg']}g/kg for optimal {goal.replace('_', ' ')}. "
            f"Carbs adjusted for training demands."
        ),
    }


def create_meal_plan(
    athlete_id: str,
    plan_date: str,
    goal: str,
    macros_json: str,
    training_time: str = "morning",
    dietary_restrictions: str = "",
) -> dict[str, Any]:
    """Create a daily meal plan based on macro targets and training schedule.

    Args:
        athlete_id: The athlete's unique identifier.
        plan_date: Date for the meal plan in YYYY-MM-DD format.
        goal: Nutrition goal driving the plan.
        macros_json: JSON string with macro targets (calories, protein, carbs, fat).
        training_time: When the athlete trains (morning, midday, afternoon, evening).
        dietary_restrictions: Comma-separated dietary restrictions (e.g., 'gluten-free,dairy-free').

    Returns:
        Dictionary containing the structured meal plan.
    """
    macros = json.loads(macros_json)
    restrictions = [r.strip() for r in dietary_restrictions.split(",") if r.strip()]

    plan = MealPlan(
        athlete_id=athlete_id,
        date=date.fromisoformat(plan_date),
        goal=NutritionGoal(goal),
        total_macros=MacroBreakdown(**macros),
        meals=[],
        hydration_target_liters=2.5 + (0.5 if macros.get("calories", 0) > 2500 else 0),
        notes=f"Training time: {training_time}. Restrictions: {', '.join(restrictions) or 'None'}",
    )

    return plan.model_dump(mode="json")


def calculate_race_fueling(
    race_distance: str,
    expected_duration_hours: float,
    weight_kg: float,
    stomach_tolerance: str = "moderate",
) -> dict[str, Any]:
    """Calculate race-day fueling strategy.

    Args:
        race_distance: Race distance (5k, 10k, half_marathon, marathon, 70.3, ironman, hyrox).
        expected_duration_hours: Expected race duration in hours.
        weight_kg: Athlete's weight in kilograms.
        stomach_tolerance: How well the athlete tolerates fuel during exercise (low, moderate, high).

    Returns:
        Dictionary containing pre-race, during-race, and post-race nutrition strategy.
    """
    # Carb targets per hour based on duration
    if expected_duration_hours < 1:
        carbs_per_hour = 0  # Mouth rinse only
    elif expected_duration_hours < 2:
        carbs_per_hour = 30
    elif expected_duration_hours < 3:
        carbs_per_hour = 60
    else:
        carbs_per_hour = 90  # Requires gut training

    # Adjust for stomach tolerance
    tolerance_multiplier = {"low": 0.7, "moderate": 1.0, "high": 1.2}
    carbs_per_hour = int(carbs_per_hour * tolerance_multiplier.get(stomach_tolerance, 1.0))

    # Fluid needs
    fluid_per_hour_ml = 500 if expected_duration_hours > 1 else 250

    strategy = {
        "race_distance": race_distance,
        "expected_duration_hours": expected_duration_hours,
        "pre_race": {
            "night_before": "Carb-rich dinner, moderate protein, low fiber. 8-10g carbs/kg.",
            "morning_of": f"3-4 hours before: {int(weight_kg * 2)}g carbs. Example: oatmeal, banana, toast with honey.",
            "30_min_before": "Small easily digestible carb source (gel or sports drink).",
        },
        "during_race": {
            "carbs_per_hour_grams": carbs_per_hour,
            "fluid_per_hour_ml": fluid_per_hour_ml,
            "sodium_per_hour_mg": 500 if expected_duration_hours > 2 else 300,
            "fueling_frequency": "Every 20-30 minutes" if carbs_per_hour > 0 else "Not needed for this duration",
            "suggested_sources": _get_fuel_sources(carbs_per_hour, race_distance),
            "total_carbs_needed": int(carbs_per_hour * expected_duration_hours),
        },
        "post_race": {
            "immediate": "30-60g carbs + 20-30g protein within 30 minutes",
            "first_meal": "Balanced meal within 2 hours: carbs, protein, healthy fats",
            "hydration": "Replace 150% of fluid lost (weigh before/after to estimate)",
        },
        "gut_training_notes": (
            "Practice this fueling strategy in training. Start with lower amounts and build up over 4-6 weeks."
            if carbs_per_hour >= 60
            else "This fueling rate should be manageable without specific gut training."
        ),
    }

    return strategy


def _get_fuel_sources(carbs_per_hour: int, race_distance: str) -> list[str]:
    """Get suggested fuel sources based on carb needs."""
    if carbs_per_hour == 0:
        return ["Water only", "Optional: sports drink mouth rinse"]
    elif carbs_per_hour <= 30:
        return ["1 gel per 45 min", "OR sports drink (500ml/hr)", "OR 2-3 chews per 30 min"]
    elif carbs_per_hour <= 60:
        return [
            "1 gel every 30 min",
            "OR alternate gel + sports drink",
            "Mix glucose sources",
        ]
    else:
        return [
            "2:1 glucose:fructose ratio required",
            "1 gel every 20 min + sports drink",
            "OR specialized high-carb drink (e.g., 80-90g/bottle)",
            "Practice in training - gut adaptation needed",
        ]


def assess_hydration_needs(
    weight_kg: float,
    training_duration_minutes: int,
    temperature_celsius: float = 20,
    humidity_percent: float = 50,
) -> dict[str, Any]:
    """Calculate hydration needs based on training and conditions.

    Args:
        weight_kg: Athlete's weight in kilograms.
        training_duration_minutes: Duration of training session in minutes.
        temperature_celsius: Ambient temperature.
        humidity_percent: Ambient humidity percentage.

    Returns:
        Dictionary containing hydration recommendations.
    """
    # Base sweat rate estimate (ml/hour)
    base_sweat_rate = weight_kg * 10  # ~10ml/kg/hr at moderate intensity

    # Temperature adjustment
    if temperature_celsius > 30:
        temp_multiplier = 1.5
    elif temperature_celsius > 25:
        temp_multiplier = 1.3
    elif temperature_celsius > 20:
        temp_multiplier = 1.1
    else:
        temp_multiplier = 1.0

    # Humidity adjustment
    humidity_multiplier = 1.0 + (humidity_percent - 50) * 0.005

    estimated_sweat_ml = int(
        base_sweat_rate * (training_duration_minutes / 60) * temp_multiplier * humidity_multiplier
    )

    return {
        "estimated_sweat_loss_ml": estimated_sweat_ml,
        "recommended_intake_during_ml": int(estimated_sweat_ml * 0.7),  # Replace 70% during
        "recommended_intake_after_ml": int(estimated_sweat_ml * 0.5),  # Additional 50% after
        "drink_frequency": "Every 15-20 minutes",
        "electrolyte_needed": training_duration_minutes > 60,
        "sodium_recommendation_mg": int(estimated_sweat_ml * 1.0) if training_duration_minutes > 60 else 0,
        "conditions": {
            "temperature_celsius": temperature_celsius,
            "humidity_percent": humidity_percent,
            "heat_risk": "high" if temperature_celsius > 30 else "moderate" if temperature_celsius > 25 else "low",
        },
    }
