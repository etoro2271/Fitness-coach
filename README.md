# FitAgent - Multi-Agent Fitness Coaching Platform

An AI-powered fitness coaching platform with specialized agents for running, triathlon, hyrox, and strength training, plus a dedicated nutritionist agent.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FitAgent Platform                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Running Coach│  │Triathlon Coach│  │ Hyrox Coach  │  │
│  │  (25+ yrs)   │  │  (25+ yrs)   │  │  (25+ yrs)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │Strength Coach│  │ Nutritionist │                     │
│  │  (25+ yrs)   │  │  (30+ yrs)   │                     │
│  └──────────────┘  └──────────────┘                     │
│                                                          │
├─────────────────────────────────────────────────────────┤
│              Integration Layer                            │
│  ┌──────────┐  ┌──────────────┐  ┌────────┐            │
│  │  Strava  │  │TrainingPeaks │  │ Garmin │            │
│  └──────────┘  └──────────────┘  └────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Agents

### Running Coach
- 25+ years of coaching experience
- Expert in all distances (5K, 10K, half marathon, marathon, ultra)
- Builds plans based on athlete perception and feedback
- Adjusts weekly based on athlete feedback and available training days
- Initial assessment: easy pace, race pace, goal marathon pace

### Triathlon Coach
- 25+ years of coaching experience
- Expert in sprint, Olympic, 70.3, and Ironman distances
- Manages swim/bike/run periodization
- Brick workout programming

### Hyrox Coach
- 25+ years of coaching experience
- Expert in Hyrox race preparation
- Combines running with functional fitness stations
- Periodized approach to race-specific training

### Strength Coach
- 25+ years of coaching experience
- Complements endurance training with strength work
- Injury prevention and performance optimization

### Nutritionist
- 30+ years of experience
- Addresses goals: fat reduction, muscle gain, performance optimization
- Tailored nutrition plans based on training load and goals

## Integrations

- **Strava** - Activity sync, workout upload
- **TrainingPeaks** - Structured workout plans, performance metrics
- **Garmin Connect** - Device sync, workout push to watch

## Tech Stack

- **Backend**: Python (FastAPI)
- **AI Framework**: Strands Agents SDK
- **Database**: SQLite (local) / PostgreSQL (production)
- **Integrations**: OAuth2 for all third-party services

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run the application
python -m fitagent.main
```

## Project Structure

```
fitagent/
├── agents/              # AI coaching agents
│   ├── running_coach.py
│   ├── triathlon_coach.py
│   ├── hyrox_coach.py
│   ├── strength_coach.py
│   └── nutritionist.py
├── integrations/        # Third-party service integrations
│   ├── strava.py
│   ├── trainingpeaks.py
│   └── garmin.py
├── models/              # Data models
│   ├── athlete.py
│   ├── workout.py
│   └── nutrition.py
├── tools/               # Agent tools
│   ├── workout_tools.py
│   └── nutrition_tools.py
├── api/                 # FastAPI routes
│   ├── routes.py
│   └── auth.py
├── config.py
└── main.py
```
