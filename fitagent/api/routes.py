"""FastAPI routes for the FitAgent application."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from fitagent.agents import (
    RunningCoachAgent,
    TriathlonCoachAgent,
    HyroxCoachAgent,
    StrengthCoachAgent,
    NutritionistAgent,
)

router = APIRouter()

# Agent instances (initialized on first use)
_agents: dict = {}


def get_agent(agent_type: str):
    """Get or create an agent instance.

    Args:
        agent_type: Type of agent to retrieve.

    Returns:
        The requested agent instance.
    """
    if agent_type not in _agents:
        agent_map = {
            "running": RunningCoachAgent,
            "triathlon": TriathlonCoachAgent,
            "hyrox": HyroxCoachAgent,
            "strength": StrengthCoachAgent,
            "nutrition": NutritionistAgent,
        }
        if agent_type not in agent_map:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        _agents[agent_type] = agent_map[agent_type]()
    return _agents[agent_type]


# --- Request/Response Models ---


class ChatRequest(BaseModel):
    """Chat message request."""

    message: str
    agent_type: str  # running, triathlon, hyrox, strength, nutrition


class ChatResponse(BaseModel):
    """Chat message response."""

    response: str
    agent_type: str


class OnboardingRequest(BaseModel):
    """Athlete onboarding request."""

    agent_type: str
    athlete_data: dict


class WeeklyFeedbackRequest(BaseModel):
    """Weekly feedback for plan adjustment."""

    agent_type: str
    feedback: dict
    available_days: int


class RaceFuelingRequest(BaseModel):
    """Race fueling plan request."""

    race_data: dict


# --- Chat Endpoints ---


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to a coaching agent.

    Args:
        request: Chat request with message and agent type.

    Returns:
        Agent's response.
    """
    agent = get_agent(request.agent_type)
    response = agent.chat(request.message)
    return ChatResponse(response=response, agent_type=request.agent_type)


# --- Onboarding Endpoints ---


@router.post("/onboard", response_model=ChatResponse)
async def onboard_athlete(request: OnboardingRequest):
    """Onboard a new athlete with a specific coach.

    Args:
        request: Onboarding request with athlete data.

    Returns:
        Coach's initial assessment and plan.
    """
    agent = get_agent(request.agent_type)
    response = agent.onboard_athlete(request.athlete_data)
    return ChatResponse(response=response, agent_type=request.agent_type)


# --- Weekly Adjustment Endpoints ---


@router.post("/weekly-adjustment", response_model=ChatResponse)
async def weekly_adjustment(request: WeeklyFeedbackRequest):
    """Get weekly plan adjustment based on athlete feedback.

    Args:
        request: Feedback request with weekly data.

    Returns:
        Adjusted plan for the upcoming week.
    """
    agent = get_agent(request.agent_type)

    if request.agent_type == "triathlon":
        response = agent.get_weekly_adjustment(request.feedback, float(request.available_days))
    else:
        response = agent.get_weekly_adjustment(request.feedback, request.available_days)

    return ChatResponse(response=response, agent_type=request.agent_type)


# --- Nutrition-Specific Endpoints ---


@router.post("/race-fueling", response_model=ChatResponse)
async def race_fueling(request: RaceFuelingRequest):
    """Get a race-specific fueling plan from the nutritionist.

    Args:
        request: Race data for fueling plan creation.

    Returns:
        Complete race-day nutrition strategy.
    """
    agent = get_agent("nutrition")
    response = agent.get_race_fueling_plan(request.race_data)
    return ChatResponse(response=response, agent_type="nutrition")


# --- Health Check ---


@router.get("/health")
async def health_check():
    """Application health check endpoint."""
    return {"status": "healthy", "service": "fitagent"}
