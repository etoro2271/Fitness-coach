"""Third-party integrations for FitAgent."""

from fitagent.integrations.strava import StravaIntegration
from fitagent.integrations.trainingpeaks import TrainingPeaksIntegration
from fitagent.integrations.garmin import GarminIntegration

__all__ = [
    "StravaIntegration",
    "TrainingPeaksIntegration",
    "GarminIntegration",
]
