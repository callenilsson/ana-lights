"""Color convertion function for LED strip."""


def Color(red: int, green: int, blue: int, white: int = 0) -> int:
    """Convert the provided red, green, blue color to a 24-bit color value.

    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue
