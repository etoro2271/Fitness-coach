"""Data models for FitAgent."""

from fitagent.models.athlete import Athlete, AthleteProfile, TrainingPreferences
from fitagent.models.workout import (
    Workout,
    WorkoutType,
    WeeklyPlan,
    TrainingBlock,
    WorkoutFeedback,
)
from fitagent.models.nutrition import NutritionPlan, NutritionGoal, MealPlan

__all__ = [
    "Athlete",
    "AthleteProfile",
    "TrainingPreferences",
    "Workout",
    "WorkoutType",
    "WeeklyPlan",
    "TrainingBlock",
    "WorkoutFeedback",
    "NutritionPlan",
    "NutritionGoal",
    "MealPlan",
]
