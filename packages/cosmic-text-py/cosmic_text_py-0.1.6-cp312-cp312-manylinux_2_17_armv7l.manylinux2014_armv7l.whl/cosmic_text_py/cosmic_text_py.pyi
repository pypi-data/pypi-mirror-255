from typing import TYPE_CHECKING, Optional
from cosmic_text_py.lib import Color

if TYPE_CHECKING:
    from PIL import Image


class Canvas:
    def __new__(self, width: int, height: int, color: Color) -> Canvas:
        """Create a new canvas.

        Args:
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            color (Color): The color of the canvas.

        Returns:
            Canvas: The canvas.
        """

    def save(self, path: str) -> None:
        """Save the canvas to a file.

        Args:
            path (str): The path to save the file to.
        """

    def to_bytes(self) -> tuple[tuple[int, int], bytes]:
        """Get the canvas as bytes.

        Returns:
            tuple[tuple[int, int], bytes]: The canvas dimensions and bytes.
        """

    def to_image(self) -> "Image.Image":
        """Get the canvas as a PIL image.

        Returns:
            The canvas as an image.
        """

    def to_buffer(self) -> list[int]:
        """Get the canvas as a buffer.

        Returns:
            list[int]: The canvas as a buffer.
        """

    @staticmethod
    def from_image(image: "Image.Image") -> Canvas:
        """Create a canvas from an image.

        Args:
            image (Image.Image): The image.

        Returns:
            Canvas: The canvas.
        """


class Font:
    def __new__(self, path: str, size: float, line_height: float, fallbacks: list[str]=None) -> Font:
        """Create a new font.

        Args:
            path (str): The path to the font.
            size (float): The font size
            line_height (float): The line height
            fallbacks (list[str], optional): The fallback fonts. Defaults to None.

        Returns:
            Font: The font.
        """


def draw_text(
    canvas: Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font: Font,
    font_color: Color
) -> None:
    ...


def draw_text_advance(
    canvas: Canvas,
    text: tuple[tuple[str, Color], ...],
    x: float,
    y: float,
    width: float,
    height: float,
    font: Font,
) -> None:
    ...
