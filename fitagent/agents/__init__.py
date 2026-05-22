"""FitAgent coaching agents."""

from fitagent.agents.running_coach import RunningCoachAgent
from fitagent.agents.triathlon_coach import TriathlonCoachAgent
from fitagent.agents.hyrox_coach import HyroxCoachAgent
from fitagent.agents.strength_coach import StrengthCoachAgent
from fitagent.agents.nutritionist import NutritionistAgent

__all__ = [
    "RunningCoachAgent",
    "TriathlonCoachAgent",
    "HyroxCoachAgent",
    "StrengthCoachAgent",
    "NutritionistAgent",
]
