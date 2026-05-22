"""Tools for workout planning and management used by coaching agents."""

import json
import uuid
from datetime import date, timedelta
from typing import Any

from fitagent.models.athlete import Athlete
from fitagent.models.workout import (
    Workout,
    WorkoutType,
    WeeklyPlan,
    TrainingBlock,
    TrainingPhase,
    WorkoutFeedback,
    IntensityZone,
    WorkoutStep,
)


def create_workout(
    athlete_id: str,
    workout_date: str,
    workout_type: str,
    title: str,
    description: str,
    main_set_description: str,
    total_duration_minutes: int,
    total_distance_km: float = None,
    primary_zone: str = "zone_2",
    rpe_target: int = 5,
    notes: str = None,
) -> dict[str, Any]:
    """Create a single workout for an athlete.

    Args:
        athlete_id: The athlete's unique identifier.
        workout_date: Date for the workout in YYYY-MM-DD format.
        workout_type: Type of workout (e.g., easy_run, interval, tempo_run).
        title: Short title for the workout.
        description: Detailed description of the workout.
        main_set_description: Description of the main workout set.
        total_duration_minutes: Expected total duration in minutes.
        total_distance_km: Expected total distance in kilometers.
        primary_zone: Primary heart rate/effort zone (zone_1 through zone_5).
        rpe_target: Target Rate of Perceived Exertion (1-10).
        notes: Additional coaching notes.

    Returns:
        Dictionary containing the created workout details.
    """
    workout = Workout(
        id=str(uuid.uuid4()),
        athlete_id=athlete_id,
        date=date.fromisoformat(workout_date),
        workout_type=WorkoutType(workout_type),
        title=title,
        description=description,
        main_set=[WorkoutStep(description=main_set_description)],
        total_duration_minutes=total_duration_minutes,
        total_distance_km=total_distance_km,
        primary_zone=IntensityZone(primary_zone),
        rpe_target=rpe_target,
        notes=notes,
    )
    return workout.model_dump(mode="json")


def create_weekly_plan(
    athlete_id: str,
    week_number: int,
    start_date: str,
    workouts_json: str,
    focus: str,
    weekly_volume_km: float = None,
    notes: str = None,
) -> dict[str, Any]:
    """Create a weekly training plan for an athlete.

    Args:
        athlete_id: The athlete's unique identifier.
        week_number: Week number in the training block.
        start_date: Start date of the week in YYYY-MM-DD format.
        workouts_json: JSON string containing list of workout dictionaries.
        focus: Primary focus/theme for this training week.
        weekly_volume_km: Total planned volume in kilometers.
        notes: Additional coaching notes for the week.

    Returns:
        Dictionary containing the weekly plan details.
    """
    start = date.fromisoformat(start_date)
    workouts_data = json.loads(workouts_json)
    workouts = [Workout(**w) for w in workouts_data]

    plan = WeeklyPlan(
        athlete_id=athlete_id,
        week_number=week_number,
        start_date=start,
        end_date=start + timedelta(days=6),
        workouts=workouts,
        weekly_volume_km=weekly_volume_km,
        focus=focus,
        notes=notes,
    )
    return plan.model_dump(mode="json")


def adjust_plan_from_feedback(
    current_plan_json: str,
    feedback_json: str,
    available_days: int,
) -> dict[str, Any]:
    """Analyze athlete feedback and suggest plan adjustments.

    Args:
        current_plan_json: JSON string of the current weekly plan.
        feedback_json: JSON string containing workout feedback from the athlete.
        available_days: Number of days the athlete can train next week.

    Returns:
        Dictionary with adjustment recommendations including volume changes,
        intensity modifications, and suggested focus areas.
    """
    current_plan = json.loads(current_plan_json)
    feedback_list = json.loads(feedback_json)

    # Analyze feedback patterns
    hard_sessions = sum(1 for f in feedback_list if f.get("perceived_effort") in ["hard", "very_hard", "maximal"])
    easy_sessions = sum(1 for f in feedback_list if f.get("perceived_effort") in ["very_easy", "easy"])
    pain_reported = any(f.get("pain_or_discomfort") for f in feedback_list)
    avg_sleep = None
    sleep_scores = [f["sleep_quality_last_night"] for f in feedback_list if f.get("sleep_quality_last_night")]
    if sleep_scores:
        avg_sleep = sum(sleep_scores) / len(sleep_scores)

    # Determine adjustment direction
    adjustments = {
        "volume_adjustment_percent": 0,
        "intensity_adjustment": "maintain",
        "available_days": available_days,
        "recommendations": [],
        "concerns": [],
    }

    if pain_reported:
        adjustments["volume_adjustment_percent"] = -20
        adjustments["intensity_adjustment"] = "reduce"
        adjustments["concerns"].append("Pain/discomfort reported - reducing load")
        adjustments["recommendations"].append("Include extra mobility and recovery work")

    elif hard_sessions > len(feedback_list) * 0.6:
        adjustments["volume_adjustment_percent"] = -10
        adjustments["intensity_adjustment"] = "reduce"
        adjustments["recommendations"].append("Most sessions felt hard - backing off slightly")

    elif easy_sessions > len(feedback_list) * 0.7:
        adjustments["volume_adjustment_percent"] = 10
        adjustments["intensity_adjustment"] = "increase"
        adjustments["recommendations"].append("Sessions feeling easy - progressive overload appropriate")

    if avg_sleep and avg_sleep < 6:
        adjustments["volume_adjustment_percent"] = min(adjustments["volume_adjustment_percent"], -10)
        adjustments["concerns"].append(f"Poor sleep quality (avg: {avg_sleep:.1f}/10) - prioritize recovery")

    if available_days < current_plan.get("workouts", []).__len__():
        adjustments["recommendations"].append(
            f"Fewer days available ({available_days}) - consolidating key sessions"
        )

    return adjustments


def calculate_training_zones(
    easy_pace: str,
    race_pace: str,
    goal_marathon_pace: str,
    max_hr: int = None,
    resting_hr: int = None,
) -> dict[str, Any]:
    """Calculate training zones based on athlete's pace information.

    Args:
        easy_pace: Current easy pace (e.g., '5:30' for 5:30/km).
        race_pace: Current race pace (e.g., '4:30' for 4:30/km).
        goal_marathon_pace: Goal marathon pace (e.g., '4:15' for 4:15/km).
        max_hr: Maximum heart rate (optional).
        resting_hr: Resting heart rate (optional).

    Returns:
        Dictionary containing pace zones and heart rate zones if HR data provided.
    """

    def pace_to_seconds(pace_str: str) -> int:
        parts = pace_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    def seconds_to_pace(seconds: int) -> str:
        return f"{seconds // 60}:{seconds % 60:02d}"

    easy_sec = pace_to_seconds(easy_pace)
    race_sec = pace_to_seconds(race_pace)
    goal_sec = pace_to_seconds(goal_marathon_pace)

    zones = {
        "pace_zones": {
            "zone_1_recovery": f"{seconds_to_pace(easy_sec + 30)} - {seconds_to_pace(easy_sec + 60)}",
            "zone_2_easy": f"{seconds_to_pace(easy_sec - 15)} - {seconds_to_pace(easy_sec + 30)}",
            "zone_3_tempo": f"{seconds_to_pace(goal_sec)} - {seconds_to_pace(goal_sec + 20)}",
            "zone_4_threshold": f"{seconds_to_pace(race_sec - 10)} - {seconds_to_pace(race_sec + 10)}",
            "zone_5_vo2max": f"{seconds_to_pace(race_sec - 30)} - {seconds_to_pace(race_sec - 10)}",
        },
        "key_paces": {
            "recovery": seconds_to_pace(easy_sec + 45),
            "easy": easy_pace,
            "marathon_pace": goal_marathon_pace,
            "tempo": seconds_to_pace(goal_sec - 10),
            "threshold": race_pace,
            "interval": seconds_to_pace(race_sec - 20),
            "repetition": seconds_to_pace(race_sec - 40),
        },
    }

    if max_hr and resting_hr:
        hr_reserve = max_hr - resting_hr
        zones["heart_rate_zones"] = {
            "zone_1": f"{resting_hr + int(hr_reserve * 0.5)} - {resting_hr + int(hr_reserve * 0.6)}",
            "zone_2": f"{resting_hr + int(hr_reserve * 0.6)} - {resting_hr + int(hr_reserve * 0.7)}",
            "zone_3": f"{resting_hr + int(hr_reserve * 0.7)} - {resting_hr + int(hr_reserve * 0.8)}",
            "zone_4": f"{resting_hr + int(hr_reserve * 0.8)} - {resting_hr + int(hr_reserve * 0.9)}",
            "zone_5": f"{resting_hr + int(hr_reserve * 0.9)} - {max_hr}",
        }

    return zones


def get_workout_history(athlete_id: str, weeks_back: int = 4) -> dict[str, Any]:
    """Retrieve recent workout history for plan adjustment decisions.

    Args:
        athlete_id: The athlete's unique identifier.
        weeks_back: Number of weeks of history to retrieve.

    Returns:
        Dictionary containing workout history summary and trends.
    """
    # In production, this would query the database
    return {
        "athlete_id": athlete_id,
        "weeks_back": weeks_back,
        "message": "Workout history retrieval - connect to database for production use",
        "summary": {
            "total_workouts": 0,
            "total_distance_km": 0,
            "total_duration_hours": 0,
            "average_rpe": 0,
            "completion_rate": 0,
        },
    }
