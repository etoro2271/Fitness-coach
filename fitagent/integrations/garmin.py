"""Garmin Connect integration for syncing workouts to Garmin devices."""

import httpx
from typing import Any, Optional
from datetime import date

from fitagent.config import settings
from fitagent.models.workout import Workout, WorkoutStep, WorkoutType, IntensityZone


class GarminIntegration:
    """Handles Garmin Connect interactions for workout sync.

    Supports:
    - Authentication via Garmin Connect credentials
    - Structured workout push to Garmin devices
    - Activity retrieval from completed workouts
    - Training status and metrics
    """

    BASE_URL = "https://connect.garmin.com"

    def __init__(self):
        """Initialize Garmin Connect integration."""
        self._session = None
        self._authenticated = False

    async def authenticate(self, email: str = None, password: str = None) -> bool:
        """Authenticate with Garmin Connect.

        Args:
            email: Garmin Connect email (uses config if not provided).
            password: Garmin Connect password (uses config if not provided).

        Returns:
            True if authentication was successful.
        """
        email = email or settings.GARMIN_CONNECT_EMAIL
        password = password or settings.GARMIN_CONNECT_PASSWORD

        try:
            from garminconnect import Garmin

            self._session = Garmin(email, password)
            self._session.login()
            self._authenticated = True
            return True
        except Exception:
            self._authenticated = False
            return False

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._authenticated

    async def get_activities(self, start: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent activities from Garmin Connect.

        Args:
            start: Starting index for pagination.
            limit: Number of activities to retrieve.

        Returns:
            List of activity summaries.
        """
        if not self._authenticated:
            raise RuntimeError("Not authenticated with Garmin Connect")

        return self._session.get_activities(start, limit)

    async def get_activity_details(self, activity_id: int) -> dict[str, Any]:
        """Get detailed data for a specific activity.

        Args:
            activity_id: The Garmin activity ID.

        Returns:
            Detailed activity data including splits, HR, pace.
        """
        if not self._authenticated:
            raise RuntimeError("Not authenticated with Garmin Connect")

        return self._session.get_activity(activity_id)

    async def push_workout(self, workout: Workout) -> dict[str, Any]:
        """Push a structured workout to Garmin Connect (syncs to watch).

        Args:
            workout: The workout to push to the device.

        Returns:
            Confirmation of workout creation.
        """
        if not self._authenticated:
            raise RuntimeError("Not authenticated with Garmin Connect")

        garmin_workout = self._convert_to_garmin_format(workout)

        # Use Garmin Connect API to create workout
        # This will sync to the athlete's Garmin watch
        result = self._session.add_workout(garmin_workout)
        return {"status": "success", "workout_id": result, "synced": True}

    async def push_weekly_plan(self, workouts: list[Workout]) -> list[dict[str, Any]]:
        """Push an entire week of workouts to Garmin Connect.

        Args:
            workouts: List of workouts to push.

        Returns:
            List of push results.
        """
        results = []
        for workout in workouts:
            if workout.workout_type != WorkoutType.REST:
                result = await self.push_workout(workout)
                results.append(result)
        return results

    async def get_training_status(self) -> dict[str, Any]:
        """Get current training status from Garmin.

        Returns:
            Training status including VO2max, training load, recovery time.
        """
        if not self._authenticated:
            raise RuntimeError("Not authenticated with Garmin Connect")

        # Retrieve various Garmin metrics
        stats = self._session.get_stats(date.today().isoformat())
        return {
            "date": date.today().isoformat(),
            "resting_hr": stats.get("restingHeartRate"),
            "stress_level": stats.get("averageStressLevel"),
            "body_battery": stats.get("bodyBatteryChargedValue"),
            "sleep_score": stats.get("sleepScore"),
            "steps": stats.get("totalSteps"),
        }

    async def get_heart_rate_zones(self) -> dict[str, Any]:
        """Get the athlete's configured heart rate zones from Garmin.

        Returns:
            Heart rate zone boundaries.
        """
        if not self._authenticated:
            raise RuntimeError("Not authenticated with Garmin Connect")

        return self._session.get_heart_rates(date.today().isoformat())

    def _convert_to_garmin_format(self, workout: Workout) -> dict[str, Any]:
        """Convert internal workout format to Garmin Connect workout format.

        Args:
            workout: Internal workout model.

        Returns:
            Garmin-compatible workout dictionary.
        """
        # Map to Garmin sport types
        sport_type_map = {
            "easy_run": "running",
            "long_run": "running",
            "tempo_run": "running",
            "interval": "running",
            "fartlek": "running",
            "hill_repeats": "running",
            "recovery_run": "running",
            "race_pace_run": "running",
            "progression_run": "running",
            "swim_endurance": "swimming",
            "swim_intervals": "swimming",
            "swim_technique": "swimming",
            "bike_endurance": "cycling",
            "bike_intervals": "cycling",
            "bike_tempo": "cycling",
            "upper_body": "strength_training",
            "lower_body": "strength_training",
            "full_body": "strength_training",
            "core": "strength_training",
        }

        sport = sport_type_map.get(workout.workout_type.value, "other")

        # Build workout steps for Garmin
        steps = []

        if workout.warmup:
            for step in workout.warmup:
                steps.append(self._step_to_garmin(step, "warmup"))

        for step in workout.main_set:
            steps.append(self._step_to_garmin(step, "active"))

        if workout.cooldown:
            for step in workout.cooldown:
                steps.append(self._step_to_garmin(step, "cooldown"))

        return {
            "workoutName": workout.title,
            "description": workout.description,
            "sport": sport,
            "estimatedDuration": workout.total_duration_minutes * 60,
            "estimatedDistance": (workout.total_distance_km or 0) * 1000,
            "steps": steps,
            "scheduledDate": workout.date.isoformat(),
        }

    def _step_to_garmin(self, step: WorkoutStep, step_type: str) -> dict[str, Any]:
        """Convert a workout step to Garmin format.

        Args:
            step: The workout step.
            step_type: Type (warmup, active, cooldown, rest).

        Returns:
            Garmin-compatible step dictionary.
        """
        garmin_step = {
            "type": step_type,
            "description": step.description,
        }

        if step.duration_minutes:
            garmin_step["durationType"] = "time"
            garmin_step["durationValue"] = int(step.duration_minutes * 60 * 1000)  # milliseconds

        if step.distance_km:
            garmin_step["durationType"] = "distance"
            garmin_step["durationValue"] = int(step.distance_km * 1000)  # meters

        if step.target_pace:
            garmin_step["targetType"] = "pace"
            garmin_step["targetValue"] = step.target_pace

        if step.target_hr_zone:
            zone_map = {
                IntensityZone.ZONE_1: 1,
                IntensityZone.ZONE_2: 2,
                IntensityZone.ZONE_3: 3,
                IntensityZone.ZONE_4: 4,
                IntensityZone.ZONE_5: 5,
            }
            garmin_step["targetType"] = "heart_rate_zone"
            garmin_step["targetValue"] = zone_map.get(step.target_hr_zone, 2)

        if step.repetitions:
            garmin_step["repeatCount"] = step.repetitions

        return garmin_step

    async def close(self):
        """Close the Garmin session."""
        self._session = None
        self._authenticated = False
