"""TrainingPeaks integration for structured workout plan syncing."""

import httpx
from typing import Any, Optional
from datetime import date

from fitagent.config import settings
from fitagent.models.workout import Workout, WorkoutStep


class TrainingPeaksIntegration:
    """Handles TrainingPeaks OAuth and API interactions.

    Supports:
    - OAuth2 authentication flow
    - Structured workout upload (with intervals and targets)
    - Workout plan sync
    - Athlete metrics retrieval (TSS, CTL, ATL, TSB)
    """

    BASE_URL = "https://api.trainingpeaks.com/v1"
    AUTH_URL = "https://oauth.trainingpeaks.com/oauth/authorize"
    TOKEN_URL = "https://oauth.trainingpeaks.com/oauth/token"

    def __init__(self, access_token: Optional[str] = None):
        """Initialize TrainingPeaks integration.

        Args:
            access_token: OAuth2 access token for authenticated requests.
        """
        self.access_token = access_token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            if access_token
            else {},
        )

    def get_authorization_url(self, state: str = "") -> str:
        """Generate the OAuth2 authorization URL for TrainingPeaks.

        Args:
            state: Optional state parameter for CSRF protection.

        Returns:
            The authorization URL to redirect the user to.
        """
        params = {
            "client_id": settings.TRAININGPEAKS_CLIENT_ID,
            "redirect_uri": settings.TRAININGPEAKS_REDIRECT_URI,
            "response_type": "code",
            "scope": "workouts:read workouts:write athlete:read metrics:read",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_token(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: The authorization code from the OAuth callback.

        Returns:
            Dictionary containing access_token and refresh_token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.TRAININGPEAKS_CLIENT_ID,
                    "client_secret": settings.TRAININGPEAKS_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.TRAININGPEAKS_REDIRECT_URI,
                },
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
            return data

    async def get_athlete(self) -> dict[str, Any]:
        """Get the authenticated athlete's profile from TrainingPeaks.

        Returns:
            Athlete profile data.
        """
        response = await self.client.get("/athlete/profile")
        response.raise_for_status()
        return response.json()

    async def get_workouts(
        self, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        """Get planned workouts for a date range.

        Args:
            start_date: Start of date range.
            end_date: End of date range.

        Returns:
            List of planned workouts.
        """
        response = await self.client.get(
            "/workouts",
            params={
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
            },
        )
        response.raise_for_status()
        return response.json()

    async def create_workout(self, workout: Workout) -> dict[str, Any]:
        """Push a structured workout to TrainingPeaks.

        Args:
            workout: The workout to upload.

        Returns:
            Created workout data from TrainingPeaks.
        """
        tp_workout = self._convert_to_tp_format(workout)
        response = await self.client.post("/workouts", json=tp_workout)
        response.raise_for_status()
        return response.json()

    async def create_weekly_plan(self, workouts: list[Workout]) -> list[dict[str, Any]]:
        """Push an entire week of workouts to TrainingPeaks.

        Args:
            workouts: List of workouts for the week.

        Returns:
            List of created workout data.
        """
        results = []
        for workout in workouts:
            result = await self.create_workout(workout)
            results.append(result)
        return results

    async def get_fitness_metrics(self) -> dict[str, Any]:
        """Get current fitness metrics (CTL, ATL, TSB).

        Returns:
            Dictionary with fitness/fatigue/form metrics.
        """
        response = await self.client.get("/athlete/metrics")
        response.raise_for_status()
        return response.json()

    async def delete_workout(self, workout_id: str) -> bool:
        """Delete a workout from TrainingPeaks.

        Args:
            workout_id: The TrainingPeaks workout ID.

        Returns:
            True if deletion was successful.
        """
        response = await self.client.delete(f"/workouts/{workout_id}")
        return response.status_code == 204

    def _convert_to_tp_format(self, workout: Workout) -> dict[str, Any]:
        """Convert internal workout format to TrainingPeaks API format.

        Args:
            workout: Internal workout model.

        Returns:
            TrainingPeaks-compatible workout dictionary.
        """
        # Map workout types to TrainingPeaks workout types
        tp_type_map = {
            "easy_run": "Run",
            "long_run": "Run",
            "tempo_run": "Run",
            "interval": "Run",
            "fartlek": "Run",
            "hill_repeats": "Run",
            "recovery_run": "Run",
            "race_pace_run": "Run",
            "progression_run": "Run",
            "swim_endurance": "Swim",
            "swim_intervals": "Swim",
            "swim_technique": "Swim",
            "bike_endurance": "Bike",
            "bike_intervals": "Bike",
            "bike_tempo": "Bike",
            "brick_workout": "Brick",
            "upper_body": "Strength",
            "lower_body": "Strength",
            "full_body": "Strength",
            "core": "Strength",
            "mobility": "Strength",
            "plyometrics": "Strength",
        }

        workout_type = tp_type_map.get(workout.workout_type.value, "Other")

        # Build structured intervals
        intervals = []
        if workout.warmup:
            for step in workout.warmup:
                intervals.append(self._step_to_interval(step, "Warmup"))

        for step in workout.main_set:
            intervals.append(self._step_to_interval(step, "Active"))

        if workout.cooldown:
            for step in workout.cooldown:
                intervals.append(self._step_to_interval(step, "Cooldown"))

        return {
            "workoutDay": workout.date.isoformat(),
            "title": workout.title,
            "workoutType": workout_type,
            "description": workout.description,
            "totalTimePlanned": workout.total_duration_minutes * 60,  # seconds
            "distancePlanned": (workout.total_distance_km or 0) * 1000,  # meters
            "structure": intervals,
            "coachComments": workout.notes or "",
        }

    def _step_to_interval(
        self, step: WorkoutStep, interval_type: str
    ) -> dict[str, Any]:
        """Convert a workout step to a TrainingPeaks interval.

        Args:
            step: The workout step.
            interval_type: Type of interval (Warmup, Active, Cooldown, Rest).

        Returns:
            TrainingPeaks interval dictionary.
        """
        interval = {
            "type": interval_type,
            "name": step.description,
        }

        if step.duration_minutes:
            interval["duration"] = int(step.duration_minutes * 60)
        if step.distance_km:
            interval["distance"] = int(step.distance_km * 1000)
        if step.target_pace:
            interval["targetPace"] = step.target_pace
        if step.repetitions:
            interval["repetitions"] = step.repetitions

        return interval

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
