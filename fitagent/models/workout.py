"""Workout and training plan models.

Internal storage uses metric units (km, min/km). All values are converted
to the athlete's preferred unit system at display time using fitagent.utils.units.
"""

from datetime import date, timedelta
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class WorkoutType(str, Enum):
    """Types of workouts."""

    # Running
    EASY_RUN = "easy_run"
    LONG_RUN = "long_run"
    TEMPO_RUN = "tempo_run"
    INTERVAL = "interval"
    FARTLEK = "fartlek"
    HILL_REPEATS = "hill_repeats"
    RECOVERY_RUN = "recovery_run"
    RACE_PACE_RUN = "race_pace_run"
    PROGRESSION_RUN = "progression_run"

    # Triathlon
    SWIM_ENDURANCE = "swim_endurance"
    SWIM_INTERVALS = "swim_intervals"
    SWIM_TECHNIQUE = "swim_technique"
    BIKE_ENDURANCE = "bike_endurance"
    BIKE_INTERVALS = "bike_intervals"
    BIKE_TEMPO = "bike_tempo"
    BRICK_WORKOUT = "brick_workout"

    # Hyrox
    HYROX_SIMULATION = "hyrox_simulation"
    STATION_PRACTICE = "station_practice"
    HYROX_INTERVALS = "hyrox_intervals"
    SLED_WORK = "sled_work"
    ROWING = "rowing"
    WALL_BALLS = "wall_balls"
    BURPEE_BROAD_JUMPS = "burpee_broad_jumps"
    FARMERS_CARRY = "farmers_carry"
    LUNGES = "lunges"
    SKI_ERG = "ski_erg"

    # Strength
    UPPER_BODY = "upper_body"
    LOWER_BODY = "lower_body"
    FULL_BODY = "full_body"
    CORE = "core"
    MOBILITY = "mobility"
    PLYOMETRICS = "plyometrics"

    # General
    REST = "rest"
    CROSS_TRAINING = "cross_training"


class IntensityZone(str, Enum):
    """Training intensity zones."""

    ZONE_1 = "zone_1"  # Recovery
    ZONE_2 = "zone_2"  # Aerobic/Easy
    ZONE_3 = "zone_3"  # Tempo
    ZONE_4 = "zone_4"  # Threshold
    ZONE_5 = "zone_5"  # VO2max/Anaerobic


class WorkoutStep(BaseModel):
    """A single step within a workout. Distances stored in km internally."""

    description: str
    duration_minutes: Optional[float] = None
    distance_km: Optional[float] = Field(default=None, description="Distance in km (converted to miles for imperial athletes)")
    target_pace: Optional[str] = Field(default=None, description="Target pace in min/km or min/mile based on athlete preference")
    target_hr_zone: Optional[IntensityZone] = None
    repetitions: Optional[int] = None
    rest_between: Optional[str] = None
    notes: Optional[str] = None


class Workout(BaseModel):
    """A single workout session. Distances stored in km internally."""

    id: str
    athlete_id: str
    date: date
    workout_type: WorkoutType
    title: str
    description: str
    warmup: Optional[list[WorkoutStep]] = None
    main_set: list[WorkoutStep]
    cooldown: Optional[list[WorkoutStep]] = None
    total_duration_minutes: int
    total_distance_km: Optional[float] = Field(default=None, description="Total distance in km (converted at display time)")
    primary_zone: IntensityZone
    rpe_target: int = Field(ge=1, le=10, description="Target RPE 1-10")
    notes: Optional[str] = None
    completed: bool = False
    synced_to_strava: bool = False
    synced_to_trainingpeaks: bool = False
    synced_to_garmin: bool = False


class PerceivedEffort(str, Enum):
    """Athlete's perceived effort after a workout."""

    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"
    MAXIMAL = "maximal"


class WorkoutFeedback(BaseModel):
    """Athlete feedback after completing a workout."""

    workout_id: str
    athlete_id: str
    perceived_effort: PerceivedEffort
    actual_pace: Optional[str] = Field(default=None, description="Actual pace in athlete's preferred unit (min/km or min/mile)")
    actual_distance_km: Optional[float] = Field(default=None, description="Actual distance in km (accepts miles input, converts internally)")
    actual_duration_minutes: Optional[float] = None
    average_hr: Optional[int] = None
    felt_good: bool = True
    pain_or_discomfort: Optional[str] = None
    sleep_quality_last_night: Optional[int] = Field(default=None, ge=1, le=10)
    stress_level: Optional[int] = Field(default=None, ge=1, le=10)
    notes: Optional[str] = None
    date: date = Field(default_factory=date.today)


class WeeklyPlan(BaseModel):
    """A week of training."""

    athlete_id: str
    week_number: int
    start_date: date
    end_date: date
    workouts: list[Workout]
    weekly_volume_km: Optional[float] = Field(default=None, description="Total volume in km (displayed as miles for imperial)")
    weekly_duration_hours: Optional[float] = None
    focus: str = Field(description="Primary focus for this week")
    notes: Optional[str] = None


class TrainingPhase(str, Enum):
    """Periodization phases."""

    BASE = "base"
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"
    RECOVERY = "recovery"
    RACE = "race"


class TrainingBlock(BaseModel):
    """A multi-week training block."""

    athlete_id: str
    phase: TrainingPhase
    start_date: date
    end_date: date
    weeks: list[WeeklyPlan]
    block_goal: str
    total_weeks: int
    current_week: int = 1
