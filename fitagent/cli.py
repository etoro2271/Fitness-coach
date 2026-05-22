"""Interactive CLI for chatting with FitAgent coaches."""

import sys
from fitagent.agents import (
    RunningCoachAgent,
    TriathlonCoachAgent,
    HyroxCoachAgent,
    StrengthCoachAgent,
    NutritionistAgent,
)


def select_coach() -> tuple:
    """Display coach selection menu and return chosen agent.

    Returns:
        Tuple of (agent_instance, coach_name).
    """
    print("\n" + "=" * 60)
    print("  🏃 FitAgent - Your AI Coaching Team")
    print("=" * 60)
    print("\nSelect your coach:\n")
    print("  1. 🏃 Coach Marcus  - Running Coach (25+ yrs)")
    print("  2. 🏊 Coach Elena   - Triathlon Coach (25+ yrs)")
    print("  3. 💪 Coach Viktor  - Hyrox Coach (25+ yrs)")
    print("  4. 🏋️  Coach Dmitri  - Strength Coach (25+ yrs)")
    print("  5. 🥗 Dr. Sofia     - Nutritionist (30+ yrs)")
    print("  0. Exit")
    print()

    coaches = {
        "1": (RunningCoachAgent, "Coach Marcus (Running)"),
        "2": (TriathlonCoachAgent, "Coach Elena (Triathlon)"),
        "3": (HyroxCoachAgent, "Coach Viktor (Hyrox)"),
        "4": (StrengthCoachAgent, "Coach Dmitri (Strength)"),
        "5": (NutritionistAgent, "Dr. Sofia (Nutrition)"),
    }

    while True:
        choice = input("Enter choice (1-5, 0 to exit): ").strip()
        if choice == "0":
            print("\nGoodbye! Keep training! 💪\n")
            sys.exit(0)
        if choice in coaches:
            agent_class, name = coaches[choice]
            print(f"\n✅ Connected to {name}")
            print("   Type 'quit' to switch coaches, 'exit' to leave.\n")
            return agent_class(), name
        print("Invalid choice. Please try again.")


def run_chat(agent, coach_name: str):
    """Run interactive chat loop with a coach.

    Args:
        agent: The coaching agent instance.
        coach_name: Display name of the coach.
    """
    print(f"\n{'─' * 60}")
    print(f"  Chatting with {coach_name}")
    print(f"{'─' * 60}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("\nGoodbye! Keep training! 💪\n")
            sys.exit(0)
        if user_input.lower() == "quit":
            break

        print(f"\n{coach_name}: ", end="", flush=True)
        try:
            response = agent.chat(user_input)
            print(response)
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print("   Make sure your AWS credentials are configured for Bedrock access.\n")
        print()


def main():
    """Main CLI entry point."""
    print("\n🏃‍♂️ Welcome to FitAgent!")
    print("Your personal AI coaching team, powered by expert knowledge.\n")

    while True:
        agent, coach_name = select_coach()
        run_chat(agent, coach_name)


if __name__ == "__main__":
    main()
