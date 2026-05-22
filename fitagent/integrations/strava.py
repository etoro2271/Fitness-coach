"""Strava integration for syncing workouts and activities."""

import httpx
from typing import Any, Optional

from fitagent.config import settings


class StravaIntegration:
    """Handles Strava OAuth and API interactions.

    Supports:
    - OAuth2 authentication flow
    - Activity upload (planned workouts as descriptions)
    - Activity retrieval (completed workouts)
    - Athlete profile sync
    """

    BASE_URL = "https://www.strava.com/api/v3"
    AUTH_URL = "https://www.strava.com/oauth/authorize"
    TOKEN_URL = "https://www.strava.com/oauth/token"

    def __init__(self, access_token: Optional[str] = None):
        """Initialize Strava integration.

        Args:
            access_token: OAuth2 access token for authenticated requests.
        """
        self.access_token = access_token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {access_token}"} if access_token else {},
        )

    def get_authorization_url(self, state: str = "") -> str:
        """Generate the OAuth2 authorization URL for Strava.

        Args:
            state: Optional state parameter for CSRF protection.

        Returns:
            The authorization URL to redirect the user to.
        """
        params = {
            "client_id": settings.STRAVA_CLIENT_ID,
            "redirect_uri": settings.STRAVA_REDIRECT_URI,
            "response_type": "code",
            "scope": "read,activity:read_all,activity:write",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_token(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: The authorization code from the OAuth callback.

        Returns:
            Dictionary containing access_token, refresh_token, and athlete info.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.STRAVA_CLIENT_ID,
                    "client_secret": settings.STRAVA_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
            return data

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token.

        Args:
            refresh_token: The refresh token from initial authorization.

        Returns:
            Dictionary containing new access_token and refresh_token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.STRAVA_CLIENT_ID,
                    "client_secret": settings.STRAVA_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
            return data

    async def get_athlete(self) -> dict[str, Any]:
        """Get the authenticated athlete's profile.

        Returns:
            Athlete profile data from Strava.
        """
        response = await self.client.get("/athlete")
        response.raise_for_status()
        return response.json()

    async def get_activities(self, page: int = 1, per_page: int = 30) -> list[dict[str, Any]]:
        """Get recent activities for the authenticated athlete.

        Args:
            page: Page number for pagination.
            per_page: Number of activities per page.

        Returns:
            List of activity summaries.
        """
        response = await self.client.get(
            "/athlete/activities",
            params={"page": page, "per_page": per_page},
        )
        response.raise_for_status()
        return response.json()

    async def get_activity(self, activity_id: int) -> dict[str, Any]:
        """Get detailed information about a specific activity.

        Args:
            activity_id: The Strava activity ID.

        Returns:
            Detailed activity data.
        """
        response = await self.client.get(f"/activities/{activity_id}")
        response.raise_for_status()
        return response.json()

    async def create_activity(
        self,
        name: str,
        sport_type: str,
        start_date: str,
        elapsed_time: int,
        description: str = "",
        distance: float = None,
        trainer: bool = False,
    ) -> dict[str, Any]:
        """Create a manual activity on Strava (for logging planned workouts).

        Args:
            name: Activity name/title.
            sport_type: Strava sport type (Run, Ride, Swim, etc.).
            start_date: ISO 8601 date string.
            elapsed_time: Duration in seconds.
            description: Workout description with details.
            distance: Distance in meters.
            trainer: Whether this was an indoor/trainer activity.

        Returns:
            Created activity data.
        """
        data = {
            "name": name,
            "sport_type": sport_type,
            "start_date_local": start_date,
            "elapsed_time": elapsed_time,
            "description": description,
            "trainer": int(trainer),
        }
        if distance:
            data["distance"] = distance

        response = await self.client.post("/activities", data=data)
        response.raise_for_status()
        return response.json()

    async def update_activity_description(
        self, activity_id: int, description: str
    ) -> dict[str, Any]:
        """Update an activity's description (useful for adding workout notes).

        Args:
            activity_id: The Strava activity ID.
            description: New description text.

        Returns:
            Updated activity data.
        """
        response = await self.client.put(
            f"/activities/{activity_id}",
            json={"description": description},
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
