"""Nutrition and meal planning models.

Internal storage uses metric units (kg, liters, celsius). All values are converted
to the athlete's preferred unit system at display time using fitagent.utils.units.
"""

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class NutritionGoal(str, Enum):
    """Primary nutrition goals."""

    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    BODY_RECOMPOSITION = "body_recomposition"
    RACE_FUELING = "race_fueling"
    RECOVERY = "recovery"


class MacroBreakdown(BaseModel):
    """Daily macronutrient targets."""

    calories: int = Field(description="Total daily calories")
    protein_grams: int = Field(description="Protein in grams")
    carbs_grams: int = Field(description="Carbohydrates in grams")
    fat_grams: int = Field(description="Fat in grams")
    fiber_grams: Optional[int] = None
    notes: Optional[str] = None


class MealTiming(str, Enum):
    """Meal timing categories."""

    PRE_WORKOUT = "pre_workout"
    DURING_WORKOUT = "during_workout"
    POST_WORKOUT = "post_workout"
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class Meal(BaseModel):
    """A single meal or snack."""

    timing: MealTiming
    name: str
    description: str
    calories: Optional[int] = None
    protein_grams: Optional[int] = None
    carbs_grams: Optional[int] = None
    fat_grams: Optional[int] = None
    foods: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class MealPlan(BaseModel):
    """Daily meal plan."""

    athlete_id: str
    date: date
    goal: NutritionGoal
    total_macros: MacroBreakdown
    meals: list[Meal]
    hydration_target_liters: float = Field(default=2.5, description="Hydration target in liters (displayed as fl oz for imperial)")
    supplements: list[str] = Field(default_factory=list)
    pre_workout_timing_minutes: int = Field(default=60, description="Minutes before workout to eat")
    notes: Optional[str] = None


class TrainingDayType(str, Enum):
    """Type of training day for nutrition adjustment."""

    REST_DAY = "rest_day"
    EASY_DAY = "easy_day"
    MODERATE_DAY = "moderate_day"
    HARD_DAY = "hard_day"
    LONG_SESSION_DAY = "long_session_day"
    RACE_DAY = "race_day"


class NutritionPlan(BaseModel):
    """Overall nutrition plan for an athlete. Weights stored in kg internally."""

    athlete_id: str
    goal: NutritionGoal
    start_date: date
    current_weight_kg: float = Field(description="Current weight in kg (displayed in lbs for imperial)")
    target_weight_kg: Optional[float] = Field(default=None, description="Target weight in kg (displayed in lbs for imperial)")
    base_macros: MacroBreakdown = Field(description="Base macros for rest days")
    easy_day_macros: MacroBreakdown
    hard_day_macros: MacroBreakdown
    long_session_macros: MacroBreakdown
    race_day_macros: Optional[MacroBreakdown] = None
    dietary_restrictions: list[str] = Field(default_factory=list)
    food_preferences: list[str] = Field(default_factory=list)
    food_dislikes: list[str] = Field(default_factory=list)
    supplements_recommended: list[str] = Field(default_factory=list)
    hydration_strategy: str = Field(default="Drink to thirst, aim for pale yellow urine")
    race_fueling_strategy: Optional[str] = None
    weekly_check_in_day: str = Field(default="Monday")
    notes: Optional[str] = None
