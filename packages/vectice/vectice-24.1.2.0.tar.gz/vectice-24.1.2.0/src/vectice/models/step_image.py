from __future__ import annotations

import logging
from io import IOBase

from PIL.Image import Image

from vectice.api.json.step import StepType
from vectice.models.step import Step

_logger = logging.getLogger(__name__)


class StepImage(Step):
    """Model a Vectice step's image.

    A StepImage stores an image.
    """

    def __init__(self, step: Step, image: str | IOBase | Image | None = None):
        """Initialize a step's image.

        Parameters:
            step: The step
            image: The step's image.
        """
        super().__init__(
            id=step.id,
            iteration=step._iteration,
            name=step.name,
            index=step.index,
            slug=step.slug,
            description=step._description,
            step_type=StepType.StepImage,
            artifacts=step.artifacts,
        )
        self._image: str | IOBase | Image | None = image

    def __repr__(self):
        return f"StepImage(name='{self.name}', id={self.id}, description='{self._description}', image={self.image})"

    @property
    def image(self) -> str | IOBase | Image | None:
        """The step's image.

        Returns:
            The step's image.
        """
        return self._image
