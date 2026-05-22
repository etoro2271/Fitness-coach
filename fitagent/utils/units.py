"""Unit conversion utilities for metric and imperial systems."""

from enum import Enum


class UnitSystem(str, Enum):
    """Supported unit systems."""

    METRIC = "metric"      # km, kg, cm, min/km
    IMPERIAL = "imperial"  # miles, lbs, inches, min/mile


# Conversion constants
KM_TO_MILES = 0.621371
MILES_TO_KM = 1.60934
KG_TO_LBS = 2.20462
LBS_TO_KG = 0.453592
CM_TO_INCHES = 0.393701
INCHES_TO_CM = 2.54
CM_TO_FEET_INCHES = None  # Handled by function
METERS_TO_FEET = 3.28084
FEET_TO_METERS = 0.3048


def convert_distance(value: float, from_unit: str, to_unit: str) -> float:
    """Convert distance between metric and imperial.

    Args:
        value: The distance value to convert.
        from_unit: Source unit ('km', 'miles', 'm', 'feet', 'yards').
        to_unit: Target unit ('km', 'miles', 'm', 'feet', 'yards').

    Returns:
        Converted distance value.
    """
    # Normalize to meters first
    to_meters = {
        "km": 1000.0,
        "miles": 1609.34,
        "m": 1.0,
        "feet": 0.3048,
        "yards": 0.9144,
    }

    from_meters = {
        "km": 0.001,
        "miles": 0.000621371,
        "m": 1.0,
        "feet": 3.28084,
        "yards": 1.09361,
    }

    meters = value * to_meters[from_unit]
    return round(meters * from_meters[to_unit], 2)


def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    """Convert weight between metric and imperial.

    Args:
        value: The weight value to convert.
        from_unit: Source unit ('kg', 'lbs', 'g', 'oz').
        to_unit: Target unit ('kg', 'lbs', 'g', 'oz').

    Returns:
        Converted weight value.
    """
    # Normalize to grams first
    to_grams = {
        "kg": 1000.0,
        "lbs": 453.592,
        "g": 1.0,
        "oz": 28.3495,
    }

    from_grams = {
        "kg": 0.001,
        "lbs": 0.00220462,
        "g": 1.0,
        "oz": 0.035274,
    }

    grams = value * to_grams[from_unit]
    return round(grams * from_grams[to_unit], 1)


def convert_height(value_cm: float) -> dict:
    """Convert height from cm to feet/inches and vice versa.

    Args:
        value_cm: Height in centimeters.

    Returns:
        Dictionary with both metric and imperial representations.
    """
    total_inches = value_cm * CM_TO_INCHES
    feet = int(total_inches // 12)
    inches = round(total_inches % 12, 1)

    return {
        "cm": round(value_cm, 1),
        "feet": feet,
        "inches": inches,
        "display_metric": f"{round(value_cm, 1)} cm",
        "display_imperial": f"{feet}'{inches}\"",
    }


def convert_height_from_imperial(feet: int, inches: float) -> float:
    """Convert height from feet/inches to centimeters.

    Args:
        feet: Height feet component.
        inches: Height inches component.

    Returns:
        Height in centimeters.
    """
    total_inches = (feet * 12) + inches
    return round(total_inches * INCHES_TO_CM, 1)


def convert_pace(pace_str: str, from_unit: str, to_unit: str) -> str:
    """Convert pace between min/km and min/mile.

    Args:
        pace_str: Pace string in 'M:SS' format (e.g., '5:30').
        from_unit: Source unit ('min/km' or 'min/mile').
        to_unit: Target unit ('min/km' or 'min/mile').

    Returns:
        Converted pace string in 'M:SS' format.
    """
    if from_unit == to_unit:
        return pace_str

    # Parse pace string
    parts = pace_str.split(":")
    total_seconds = int(parts[0]) * 60 + int(parts[1])

    if from_unit == "min/km" and to_unit == "min/mile":
        # min/km to min/mile: multiply by 1.60934
        converted_seconds = int(total_seconds * MILES_TO_KM)
    elif from_unit == "min/mile" and to_unit == "min/km":
        # min/mile to min/km: divide by 1.60934
        converted_seconds = int(total_seconds / MILES_TO_KM)
    else:
        return pace_str

    minutes = converted_seconds // 60
    seconds = converted_seconds % 60
    return f"{minutes}:{seconds:02d}"


def convert_speed(value: float, from_unit: str, to_unit: str) -> float:
    """Convert speed between units.

    Args:
        value: Speed value.
        from_unit: Source unit ('km/h', 'mph', 'm/s').
        to_unit: Target unit ('km/h', 'mph', 'm/s').

    Returns:
        Converted speed value.
    """
    # Normalize to m/s
    to_ms = {
        "km/h": 1 / 3.6,
        "mph": 0.44704,
        "m/s": 1.0,
    }

    from_ms = {
        "km/h": 3.6,
        "mph": 2.23694,
        "m/s": 1.0,
    }

    ms = value * to_ms[from_unit]
    return round(ms * from_ms[to_unit], 2)


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature between Celsius and Fahrenheit.

    Args:
        value: Temperature value.
        from_unit: Source unit ('celsius' or 'fahrenheit').
        to_unit: Target unit ('celsius' or 'fahrenheit').

    Returns:
        Converted temperature value.
    """
    if from_unit == to_unit:
        return value

    if from_unit == "celsius" and to_unit == "fahrenheit":
        return round((value * 9 / 5) + 32, 1)
    elif from_unit == "fahrenheit" and to_unit == "celsius":
        return round((value - 32) * 5 / 9, 1)

    return value


def convert_volume(value: float, from_unit: str, to_unit: str) -> float:
    """Convert volume between metric and imperial.

    Args:
        value: Volume value.
        from_unit: Source unit ('liters', 'ml', 'oz_fluid', 'gallons').
        to_unit: Target unit ('liters', 'ml', 'oz_fluid', 'gallons').

    Returns:
        Converted volume value.
    """
    # Normalize to ml
    to_ml = {
        "liters": 1000.0,
        "ml": 1.0,
        "oz_fluid": 29.5735,
        "gallons": 3785.41,
    }

    from_ml = {
        "liters": 0.001,
        "ml": 1.0,
        "oz_fluid": 0.033814,
        "gallons": 0.000264172,
    }

    ml = value * to_ml[from_unit]
    return round(ml * from_ml[to_unit], 2)


def format_distance(value_km: float, unit_system: UnitSystem) -> str:
    """Format a distance value for display in the athlete's preferred unit system.

    Args:
        value_km: Distance in kilometers (internal storage unit).
        unit_system: The athlete's preferred unit system.

    Returns:
        Formatted distance string with unit label.
    """
    if unit_system == UnitSystem.IMPERIAL:
        miles = convert_distance(value_km, "km", "miles")
        return f"{miles} mi"
    return f"{value_km} km"


def format_weight(value_kg: float, unit_system: UnitSystem) -> str:
    """Format a weight value for display in the athlete's preferred unit system.

    Args:
        value_kg: Weight in kilograms (internal storage unit).
        unit_system: The athlete's preferred unit system.

    Returns:
        Formatted weight string with unit label.
    """
    if unit_system == UnitSystem.IMPERIAL:
        lbs = convert_weight(value_kg, "kg", "lbs")
        return f"{lbs} lbs"
    return f"{value_kg} kg"


def format_pace(pace_min_per_km: str, unit_system: UnitSystem) -> str:
    """Format a pace value for display in the athlete's preferred unit system.

    Args:
        pace_min_per_km: Pace in min/km format (internal storage unit).
        unit_system: The athlete's preferred unit system.

    Returns:
        Formatted pace string with unit label.
    """
    if unit_system == UnitSystem.IMPERIAL:
        pace_imperial = convert_pace(pace_min_per_km, "min/km", "min/mile")
        return f"{pace_imperial}/mi"
    return f"{pace_min_per_km}/km"


def format_height(value_cm: float, unit_system: UnitSystem) -> str:
    """Format height for display in the athlete's preferred unit system.

    Args:
        value_cm: Height in centimeters (internal storage unit).
        unit_system: The athlete's preferred unit system.

    Returns:
        Formatted height string.
    """
    if unit_system == UnitSystem.IMPERIAL:
        height = convert_height(value_cm)
        return height["display_imperial"]
    return f"{value_cm} cm"


def format_volume(value_liters: float, unit_system: UnitSystem) -> str:
    """Format volume for display in the athlete's preferred unit system.

    Args:
        value_liters: Volume in liters (internal storage unit).
        unit_system: The athlete's preferred unit system.

    Returns:
        Formatted volume string with unit label.
    """
    if unit_system == UnitSystem.IMPERIAL:
        oz = convert_volume(value_liters, "liters", "oz_fluid")
        return f"{oz} fl oz"
    return f"{value_liters} L"


def format_temperature(value_celsius: float, unit_system: UnitSystem) -> str:
    """Format temperature for display in the athlete's preferred unit system.

    Args:
        value_celsius: Temperature in Celsius (internal storage unit).
        unit_system: The athlete's preferred unit system.

    Returns:
        Formatted temperature string with unit label.
    """
    if unit_system == UnitSystem.IMPERIAL:
        f_temp = convert_temperature(value_celsius, "celsius", "fahrenheit")
        return f"{f_temp}°F"
    return f"{value_celsius}°C"
