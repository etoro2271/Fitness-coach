"""Athlete data models."""

from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from fitagent.utils.units import UnitSystem


class SportType(str, Enum):
    """Supported sport types."""

    RUNNING = "running"
    TRIATHLON = "triathlon"
    HYROX = "hyrox"
    STRENGTH = "strength"


class ExperienceLevel(str, Enum):
    """Athlete experience level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"


class RunningPaces(BaseModel):
    """Running pace information — stored internally in min/km, displayed in athlete's preferred unit."""

    easy_pace: str = Field(description="Current easy/conversational pace, e.g. '5:30' (min/km) or '8:51' (min/mile)")
    race_pace: str = Field(description="Current race pace, e.g. '4:30' (min/km) or '7:14' (min/mile)")
    goal_marathon_pace: str = Field(description="Target marathon pace, e.g. '4:15' (min/km) or '6:50' (min/mile)")
    unit: str = Field(default="min/km", description="Pace unit: 'min/km' or 'min/mile'")


class TriathlonPaces(BaseModel):
    """Triathlon-specific pace/speed information."""

    swim_100m_pace: str = Field(description="Swim pace per 100m, e.g. '1:45'")
    bike_ftp: Optional[int] = Field(default=None, description="Functional Threshold Power in watts")
    bike_easy_hr: Optional[int] = Field(default=None, description="Easy bike heart rate")
    run_easy_pace: str = Field(description="Run easy pace off the bike")
    run_race_pace: str = Field(description="Run race pace off the bike")
    target_distance: str = Field(description="Target: sprint, olympic, 70.3, ironman")


class HyroxProfile(BaseModel):
    """Hyrox-specific athlete profile."""

    target_time: Optional[str] = Field(default=None, description="Target overall Hyrox time")
    run_1km_pace: str = Field(description="1km running pace between stations")
    sled_push_weight: Optional[float] = Field(default=None, description="Sled push weight (kg internally, displayed in athlete's unit)")
    sled_pull_weight: Optional[float] = Field(default=None, description="Sled pull weight (kg internally, displayed in athlete's unit)")
    wall_balls_weight: Optional[float] = Field(default=None, description="Wall ball weight (kg internally, displayed in athlete's unit)")
    category: str = Field(default="open", description="open, pro, doubles")


class TrainingPreferences(BaseModel):
    """Athlete training preferences and constraints."""

    unit_system: UnitSystem = Field(default=UnitSystem.METRIC, description="Preferred unit system: 'metric' (km/kg) or 'imperial' (miles/lbs)")
    available_days_per_week: int = Field(ge=1, le=7, description="Days available for training")
    preferred_days: list[str] = Field(default_factory=list, description="Preferred training days")
    max_session_duration_minutes: int = Field(default=90, description="Max session length")
    has_gym_access: bool = Field(default=False)
    has_pool_access: bool = Field(default=False)
    has_bike: bool = Field(default=False)
    injuries_or_limitations: list[str] = Field(default_factory=list)
    preferred_long_run_day: Optional[str] = Field(default=None)


class AthleteProfile(BaseModel):
    """Complete athlete profile for onboarding.

    Internal storage uses metric (kg, cm, km). Display converts to athlete's preferred unit system.
    """

    sport_type: SportType
    experience_level: ExperienceLevel
    age: Optional[int] = None
    weight_kg: Optional[float] = Field(default=None, description="Weight stored in kg internally")
    height_cm: Optional[float] = Field(default=None, description="Height stored in cm internally")
    resting_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    running_paces: Optional[RunningPaces] = None
    triathlon_paces: Optional[TriathlonPaces] = None
    hyrox_profile: Optional[HyroxProfile] = None
    training_preferences: TrainingPreferences
    goal_race_date: Optional[date] = None
    goal_description: str = Field(description="What the athlete wants to achieve")


class Athlete(BaseModel):
    """Core athlete entity."""

    id: str
    name: str
    email: str
    profile: AthleteProfile
    created_at: date = Field(default_factory=date.today)
    strava_connected: bool = False
    trainingpeaks_connected: bool = False
    garmin_connected: bool = False
    strava_token: Optional[str] = None
    trainingpeaks_token: Optional[str] = None
