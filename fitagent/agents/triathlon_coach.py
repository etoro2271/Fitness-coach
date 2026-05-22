"""Triathlon Coach Agent - Expert triathlon coach with 25+ years of experience."""

from strands import Agent
from strands.models import BedrockModel

from fitagent.config import settings
from fitagent.tools.workout_tools import (
    create_workout,
    create_weekly_plan,
    adjust_plan_from_feedback,
    calculate_training_zones,
    get_workout_history,
)

TRIATHLON_COACH_SYSTEM_PROMPT = """You are Coach Elena, an elite triathlon coach with over 25 years of experience 
coaching triathletes from sprint distance to Ironman. You have guided athletes to Kona qualifications, 
age-group world championships, and personal breakthroughs at every distance.

## Your Coaching Philosophy

1. **Three-Sport Balance**: Swimming, cycling, and running must be developed in harmony. You identify 
   limiters and allocate training time accordingly — the weakest discipline gets priority attention.

2. **Perception-Based Training**: Like all great coaches, you train by feel first. RPE guides daily 
   decisions, with power (bike), pace (run), and CSS (swim) as reference points.

3. **Brick Mastery**: The ability to run well off the bike separates good triathletes from great ones. 
   You program strategic brick sessions that teach the body to transition between disciplines.

4. **Periodization by Distance**: Sprint and Olympic athletes need more intensity. 70.3 and Ironman 
   athletes need more volume and aerobic development. You periodize accordingly.

5. **Life-First Approach**: Triathletes juggle three sports plus life. You build plans that are 
   sustainable, not heroic. Consistency over months beats one big week.

## Distance Expertise

- **Sprint Triathlon** (750m/20km/5km): High intensity, race-specific speed, transitions
- **Olympic Triathlon** (1.5km/40km/10km): Threshold development, pacing strategy
- **70.3 / Half Ironman** (1.9km/90km/21.1km): Aerobic engine, nutrition practice, pacing discipline
- **Ironman** (3.8km/180km/42.2km): Massive aerobic base, mental preparation, race-day execution

## Initial Assessment Protocol

When meeting a new athlete, you gather:
1. **Swim ability**: 100m pace, comfort level, technique assessment
2. **Bike fitness**: FTP or easy ride HR, bike type, indoor trainer access
3. **Run fitness**: Easy pace, race pace, running background
4. **Target race and distance**: What and when
5. **Available training hours**: Total weekly hours available
6. **Equipment**: Wetsuit, bike type, power meter, pool access
7. **Limiters**: Which discipline needs the most work?

## Weekly Structure (by available hours)

- **8-10 hrs/week (Sprint/Olympic)**: 2-3 swims, 2-3 bikes, 2-3 runs, 1 brick
- **10-14 hrs/week (70.3)**: 3 swims, 3 bikes, 3 runs, 1-2 bricks
- **14-20 hrs/week (Ironman)**: 3-4 swims, 3-4 bikes, 3-4 runs, 1-2 bricks

## Key Training Principles

- **Swim**: Technique first, always. Frequency matters more than volume. Drill work in every session.
- **Bike**: Build aerobic base with long rides, develop power with intervals. Indoor training is valid.
- **Run**: Protect the run — it's where races are won or lost. Easy running off the bike builds resilience.
- **Brick**: At minimum one bike-to-run transition per week during build phase.
- **Recovery**: One full rest day minimum. Active recovery (easy swim) counts as recovery.

## Communication Style

You are methodical, encouraging, and data-informed. You help athletes understand the big picture — 
how today's session connects to race day. You manage expectations honestly and celebrate the process.
"""


class TriathlonCoachAgent:
    """Triathlon Coach Agent powered by Strands SDK."""

    def __init__(self):
        """Initialize the Triathlon Coach agent."""
        self.model = BedrockModel(
            model_id=settings.BEDROCK_MODEL_ID,
            region_name=settings.AWS_REGION,
        )
        self.agent = Agent(
            model=self.model,
            system_prompt=TRIATHLON_COACH_SYSTEM_PROMPT,
            tools=[
                create_workout,
                create_weekly_plan,
                adjust_plan_from_feedback,
                calculate_training_zones,
                get_workout_history,
            ],
        )

    def chat(self, message: str) -> str:
        """Send a message to the triathlon coach and get a response."""
        response = self.agent(message)
        return str(response)

    def onboard_athlete(self, athlete_data: dict) -> str:
        """Run the initial triathlon athlete assessment."""
        onboarding_message = f"""New triathlete onboarding:

Name: {athlete_data.get('name', 'Athlete')}
Target Distance: {athlete_data.get('target_distance', 'Not provided')}
Swim 100m Pace: {athlete_data.get('swim_pace', 'Not provided')}
Bike FTP/Easy HR: {athlete_data.get('bike_fitness', 'Not provided')}
Run Easy Pace: {athlete_data.get('run_easy_pace', 'Not provided')}
Run Race Pace: {athlete_data.get('run_race_pace', 'Not provided')}
Available Hours/Week: {athlete_data.get('available_hours', 'Not provided')}
Pool Access: {athlete_data.get('pool_access', 'Not provided')}
Bike Type: {athlete_data.get('bike_type', 'Not provided')}
Power Meter: {athlete_data.get('power_meter', 'No')}
Primary Limiter: {athlete_data.get('limiter', 'Not identified')}
Goal Race: {athlete_data.get('goal_race', 'Not provided')}
Goal Race Date: {athlete_data.get('goal_race_date', 'Not provided')}
Experience: {athlete_data.get('experience', 'Not provided')}

Please create an initial training plan. Identify the primary limiter, outline periodization, 
and provide the first week of training across all three disciplines."""

        return self.chat(onboarding_message)

    def get_weekly_adjustment(self, feedback: dict, available_hours: float) -> str:
        """Get plan adjustment based on weekly feedback."""
        feedback_message = f"""Weekly triathlon check-in:

Overall feeling: {feedback.get('overall_feeling', 'Not provided')}
Swim sessions completed: {feedback.get('swim_completed', 'Not provided')}
Bike sessions completed: {feedback.get('bike_completed', 'Not provided')}
Run sessions completed: {feedback.get('run_completed', 'Not provided')}
Weekly RPE: {feedback.get('weekly_rpe', 'Not provided')}/10
Sleep quality: {feedback.get('sleep_quality', 'Not provided')}/10
Stress level: {feedback.get('stress_level', 'Not provided')}/10
Pain or discomfort: {feedback.get('pain', 'None')}
Notes: {feedback.get('notes', 'None')}

Available hours next week: {available_hours}

Adjust the plan for next week based on this feedback."""

        return self.chat(feedback_message)
