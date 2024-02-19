"""
# grain.py

This module defines the `Grain`-base class as well as more specialized
classes and supplemental helper-functions for an efficient generation of
`Grain`s.

## Grain
A `Grain` stores information on shape (including preprocessed
information that is being used in the simulation afterwards). It also
gets assigned a unique identifier via the uuid-module (uuid4).
Furthermore, `Grain`-type classes provide a `sample`-method that can be
issued to generate a sampled representation in the form of a `numpy`-
`NDArray`.

"""

from typing import Optional
from dataclasses import dataclass
import uuid
import numpy as np
from numpy.typing import NDArray
from scipy import optimize
from granular.geometry \
    import Shape, SamplingStrategy, EquidistantSampling, SamplingContext


@dataclass
class Representations:
    """
    Record class defining the storage-format of different
    representations of `Grain`s.

    Keyword arguments:
    ground_truth -- ground truth for the shape of a `Grain`
    sampled -- list of `NDArray`s for the sampled `Shape` at different
               levels of detail; `sampled[0]` represents the lowest lod
               (default `None`)
    bounding_box -- (UNUSED) bounding box representation
                    (default `None`)
    bounding_sphere -- `float` characterizing size of the bounding
                       sphere with a point of reference located at the
                       reference point for the shape-generating function
                       (default `None`)
    """

    ground_truth: Shape
    sampled: Optional[list[NDArray]] = None
    bounding_box: Optional = None
    bounding_sphere: Optional[float] = None


class Grain:
    """
    `Grain`s represent the granular units of a simulation.

    Keyword arguments:
    shape -- grain shape
    """

    def __init__(self, shape: Shape) -> None:
        self._identifier = uuid.uuid4()
        self._default_sampling_strategy = EquidistantSampling
        self._default_sampling_context = SamplingContext(
            domain=[0, np.pi],
            num=50,
            endpoint=False
        )

        # preprocess/analyze shape
        self._representations = Representations(
            ground_truth=shape,
            sampled=[
                self._default_sampling_strategy.sample(
                    shape,
                    self._default_sampling_context
                )
            ],
            bounding_sphere=shape(
                optimize.fminbound(
                    lambda x: -shape(x), 0.0, 2.0*np.pi, xtol=1e-10
                )
            )
        )

    def sample(
        self,
        strategy: SamplingStrategy = None,
        context: Optional[SamplingContext] = None
    ) -> NDArray:
        """
        Returns an `NDArray` as returned by the provided
        `SamplingStrategy`. The default `SamplingStrategy` corresponds
        to `EquidistantSampling`. The default `SamplingContext` is
        passed into the provided strategy uses a domain of `[0, np.pi]`
        and otherwise the context's default values.

        Keyword arguments:
        strategy -- a `SamplingStrategy` used to sample the shape
                    (default `None`)
        context -- a `SamplingContext` passed to the provided
                   `SamplingStrategy`
                   (default `None`)
        """

        if strategy is None and context is None:
            return self._representations.sampled[0]

        return (strategy or self._default_sampling_strategy).sample(
            self._representations.ground_truth,
            context=context or self._default_sampling_context
        )

    @property
    def identifier(self) -> str:
        """Getter for property `identifier`."""
        return str(self._identifier)

    @property
    def shape(self) -> Shape:
        """Getter for property `shape`."""
        return self._representations.ground_truth

    @property
    def lod0(self) -> NDArray:
        """Getter for property `lod0`."""
        return self._representations.sampled[0]

    @property
    def radius(self) -> str:
        """Getter for property `radius` (bounding sphere)."""
        return self._representations.bounding_sphere

    @property
    def diameter(self) -> str:
        """Getter for property `diameter` (bounding sphere)."""
        return 2*self._representations.bounding_sphere

    def __str__(self):
        return f"<grain {self._identifier}>"


# TODO: derived classes for different types: spherical, super, fourier
class SphericalGrain(Grain):
    ...


class SuperGrain(Grain):
    ...


class FourierGrain(Grain):
    ...


def duplicate_grain(grain: Grain) -> Grain:
    ...


def generate_batch(grain: Grain) -> list[Grain]:
    ...
