from typing import Self

from cosmic_text_py.cosmic_text_py import *

try:
    from PIL import Image
except:
    pass


class Color(tuple):
    def __new__(cls, r: int, g: int, b: int, a: int = 255) -> Self:
        """Create a new color.

        Args:
            r (int): The red value of the color.
            g (int): The green value of the color.
            b (int): The blue value of the color.
            a (int, optional): The alpha value of the color. Defaults to 255.
        """
        return super().__new__(cls, (r, g, b, a))

    @staticmethod
    def from_hex(hex: str) -> Self:
        """Create a color from a hex string.

        Args:
            hex (str): The hex string.

        Returns:
            Color: The color.
        """
        return Color(*bytes.fromhex(hex))

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"

    @property
    def r(self) -> int:
        """The red value of the color."""
        return self[0]

    @property
    def g(self) -> int:
        """The green value of the color."""
        return self[1]

    @property
    def b(self) -> int:
        """The blue value of the color."""
        return self[2]

    @property
    def a(self) -> int:
        """The alpha value of the color."""
        return self[3]


class Writer:
    def __init__(self, image: "Image.Image") -> None:
        """Create a new draw object.

        Args:
            image (Image.Image): The image to draw on.
        """
        self.image = image
        self.__canvas = None

    def __enter__(self) -> Self:
        assert self.image.mode == "RGBA", "The image must be in RGBA mode."
        self.__canvas = Canvas.from_image(self.image)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.image.frombytes(self.__canvas.to_bytes()[1])
        self.__canvas = None

    @property
    def _canvas(self) -> Canvas:
        assert self.__canvas is not None, "You must use the Writer as a context manager."
        return self.__canvas

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        font: Font,
        font_color: Color
    ) -> None:
        draw_text(self._canvas, text, x, y, width, height, font, font_color)
