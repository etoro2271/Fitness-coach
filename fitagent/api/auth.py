"""Authentication routes for third-party service OAuth flows."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from fitagent.integrations.strava import StravaIntegration
from fitagent.integrations.trainingpeaks import TrainingPeaksIntegration
from fitagent.integrations.garmin import GarminIntegration

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


class OAuthCallbackResponse(BaseModel):
    """Response after successful OAuth callback."""

    service: str
    status: str
    athlete_id: str = ""
    message: str


class GarminAuthRequest(BaseModel):
    """Garmin authentication request (credential-based)."""

    email: str
    password: str


# --- Strava OAuth ---


@auth_router.get("/strava/connect")
async def strava_connect():
    """Initiate Strava OAuth flow.

    Returns:
        Authorization URL to redirect the user to.
    """
    strava = StravaIntegration()
    auth_url = strava.get_authorization_url(state="strava_connect")
    return {"authorization_url": auth_url}


@auth_router.get("/strava/callback", response_model=OAuthCallbackResponse)
async def strava_callback(code: str = Query(...), state: str = Query("")):
    """Handle Strava OAuth callback.

    Args:
        code: Authorization code from Strava.
        state: State parameter for CSRF verification.

    Returns:
        Connection status and athlete info.
    """
    strava = StravaIntegration()
    try:
        token_data = await strava.exchange_token(code)
        athlete = token_data.get("athlete", {})
        return OAuthCallbackResponse(
            service="strava",
            status="connected",
            athlete_id=str(athlete.get("id", "")),
            message=f"Connected to Strava as {athlete.get('firstname', '')} {athlete.get('lastname', '')}",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Strava authentication failed: {str(e)}")
    finally:
        await strava.close()


# --- TrainingPeaks OAuth ---


@auth_router.get("/trainingpeaks/connect")
async def trainingpeaks_connect():
    """Initiate TrainingPeaks OAuth flow.

    Returns:
        Authorization URL to redirect the user to.
    """
    tp = TrainingPeaksIntegration()
    auth_url = tp.get_authorization_url(state="tp_connect")
    return {"authorization_url": auth_url}


@auth_router.get("/trainingpeaks/callback", response_model=OAuthCallbackResponse)
async def trainingpeaks_callback(code: str = Query(...), state: str = Query("")):
    """Handle TrainingPeaks OAuth callback.

    Args:
        code: Authorization code from TrainingPeaks.
        state: State parameter for CSRF verification.

    Returns:
        Connection status.
    """
    tp = TrainingPeaksIntegration()
    try:
        token_data = await tp.exchange_token(code)
        return OAuthCallbackResponse(
            service="trainingpeaks",
            status="connected",
            athlete_id="",
            message="Connected to TrainingPeaks successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"TrainingPeaks authentication failed: {str(e)}")
    finally:
        await tp.close()


# --- Garmin Connect ---


@auth_router.post("/garmin/connect", response_model=OAuthCallbackResponse)
async def garmin_connect(request: GarminAuthRequest):
    """Connect to Garmin using credentials.

    Args:
        request: Garmin email and password.

    Returns:
        Connection status.
    """
    garmin = GarminIntegration()
    success = await garmin.authenticate(request.email, request.password)

    if success:
        return OAuthCallbackResponse(
            service="garmin",
            status="connected",
            athlete_id="",
            message="Connected to Garmin Connect successfully",
        )
    else:
        raise HTTPException(status_code=401, detail="Garmin Connect authentication failed")


# --- Connection Status ---


@auth_router.get("/status")
async def connection_status():
    """Check connection status for all services.

    Returns:
        Dictionary with connection status for each service.
    """
    return {
        "strava": {"connected": False, "message": "Not connected"},
        "trainingpeaks": {"connected": False, "message": "Not connected"},
        "garmin": {"connected": False, "message": "Not connected"},
    }
