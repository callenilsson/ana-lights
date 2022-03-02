"""LED Strip wrapper class."""
from typing import List
from ..color import Color
from ..rpi_ws281x.python.neopixel import Adafruit_NeoPixel


class LEDStrip:
    """LED Strip wrapper class."""

    strip: Adafruit_NeoPixel

    def __init__(
        self,
        led_count: int,
        pin: int,
        freq_hz: int,
        dma: int,
        brightness: int,
        invert: bool,
        channel: int,
    ) -> None:  # noqa
        """Initialize the LEDStrip."""
        self.strip = Adafruit_NeoPixel(
            num=led_count,
            pin=pin,
            freq_hz=freq_hz,
            dma=dma,
            invert=invert,
            brightness=brightness,
            channel=channel,
        )
        self.strip.begin()

    def render(self, pixels: List[int]) -> None:
        """Render <pixels> on to the LED <strip>.

        Args:
            pixels: List of 24-bit int pixels to render on the strip.
        """
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(n=i, color=pixels[i])
        self.strip.show()

    def render_color(self, red: int, green: int, blue: int) -> None:
        """Render <pixels> on to the LED <strip>.

        Args:
            red:    Red channel color value to display.
            green:  Green channel color value to display.
            blue:   Blue channel color value to display.
        """
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(n=i, color=Color(red, green, blue))
        self.strip.show()

    def black(self) -> None:
        """Turn off the LED <strip>."""
        self.render_color(red=0, green=0, blue=0)

    def status(self, red: int, green: int, blue: int) -> None:
        """Display status via a few pixels on the strip with an RGB color.

        Args:
            red:    Red channel color value to display.
            green:  Green channel color value to display.
            blue:   Blue channel color value to display.
        """
        self.black()
        for i in range(10):
            self.strip.setPixelColor(
                n=int(i * self.strip.numPixels() / 10),
                color=Color(red=red, green=green, blue=blue),
            )
        self.strip.show()
