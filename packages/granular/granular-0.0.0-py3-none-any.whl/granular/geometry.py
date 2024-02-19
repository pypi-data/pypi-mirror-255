"""
# geometry.py

This module contains definitions that can be used to generate and process
grain shapes that are supported by `granular`, i.e., star domains.


## Sampling
A sampling-process (useful for generating different representations of
grains) can be performed using the `SamplingStrategy`-classes. These,
again, require a `SamplingContext` storing information like number of
samples.

Generate an array of equidistantly distributed samples for the
function x**2 by entering
```
>>> from granular.geometry import EquidistantSampling, SamplingContext
>>> samples = EquidistantSampling.sample(shape=lambda x: x**2, context=SamplingContext())
>>> np.shape(samples)
(50, 2)
```

## Shape generating functions
This module provides functions that can be used to generate `Shape`s,
i.e., functions which themselves represent closed, planar curves. For
example, using the factory `shape_superformula`, a star-like `Shape` can
be created by
```
>>> from granular.geometry import shape_superformula
>>> shape = shape_superformula((2, 9, 9), 5, 1.0)
>>> shape([1, 2, 3])
array([0.37628812, 0.77859841, 0.7103601])
```
"""

from typing import TypeAlias, Callable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import cos, sin
import numpy as np
from numpy.typing import NDArray
from scipy import optimize

Shape: TypeAlias = Callable[[float | NDArray], float | NDArray]


@dataclass
class SamplingContext:
    """
    Record class representing information on a sampling context.

    Keyword arguments:
    domain -- domain over which the sampling should be done
              (default corresponds to an interval [0:1])
    num -- total number of samples
           (default 50)
    endpoint -- if `True`, the first and last sample are identical
                (default `False`)
    """

    domain: list = field(default_factory=lambda: [0.0, 1.0])
    num: int = 50
    endpoint: bool = False


class SamplingStrategy(ABC):
    """
    Interface for sampling strategies.
    """

    @staticmethod
    @abstractmethod
    def samples(
        shape: Shape,
        context: Optional[SamplingContext] = None
    ) -> NDArray:
        """
        Returns an array of `num` sample locations based on `shape`.

        Keyword arguments:
        shape -- callable function generating a shape to be sampled
        context -- sampling context
                   (default uses a `SamplingContext` with default
                   values)
        """
        raise NotImplementedError

    @classmethod
    def sample(
        cls,
        shape: Shape,
        context: Optional[SamplingContext] = None,
        values_only: bool = False
    ) -> NDArray:
        """
        Returns an array of `num` sampled locations based on `shape`
        as pairs of sample position and sampled value (shape=(num, 2)).

        Keyword arguments:
        shape -- callable function generating a shape to be sampled
        context -- sampling context
                   (default uses a `SamplingContext` with default
                   values)
        values_only -- if `True`, the returned array only contains the
                       sampled values (shape=(num,))
        """

        x = cls.samples(shape, context=context)
        y = shape(x)

        if values_only:
            return y
        return np.stack((x, y), axis=-1)


class EquidistantSampling(SamplingStrategy):
    """
    Samples for equidistant sampling.
    """

    @staticmethod
    def samples(
        shape: Shape,
        context: Optional[SamplingContext] = None
    ) -> NDArray:
        return np.linspace(
            *(context.domain or [0.0, 1.0]),
            num=context.num,
            endpoint=context.endpoint
        )


class FavorCurvatureSampling(SamplingStrategy):
    """
    Samples with higher frequency in regions of greater curvature.
    """

    @staticmethod
    def samples(
        shape: Shape,
        context: Optional[SamplingContext] = None
    ) -> NDArray:

        raise NotImplementedError


def shape_superformula(
    n: tuple[int, int, int],
    m: int, r: float,
    vectorize: bool = True
) -> Shape:
    """
    Returns a callable function that generates a planar and closed
    curve based on the superformula.

    r(p) ~ r * [|cos(mp/4)|**n2 + |sin(mp/4)|**n3]**(-1/n1)

    Keyword arguments:
    n -- three-tuple containing the interger values `n1`, `n2`, `n3`
    m -- angular frequency `m`
    r -- radius of the bounding sphere
    vectorize -- if `True`, use `np.vectorize` to make compatible with
                 `NDArray`
                 (default `True`)
    """

    def _generate_super(_r):
        def __r(p):
            return _r * (
                (abs(cos((_p := 0.25*m*p))))**n[1]
                + (abs(sin(_p)))**n[2]
            )**(-1.0/n[0])
        if vectorize:
            return np.vectorize(__r)
        return __r

    # rescale to precisely fit bounding volume into requested size r
    return _generate_super(
        r/_generate_super(r)(
            optimize.fminbound(_generate_super(-r), 0.0, 2.0*np.pi)
        )
    )


def shape_fourier(
    d: tuple[float, ...],
    r: float,
    vectorize: bool = True
) -> Shape:
    """
    Returns a callable function that generates an irregular, planar and
    closed curve based on the a Fourier expansion.

    Keyword arguments:
    d -- tuple of Fourier descriptors
    r -- radius of the bounding sphere
    vectorize -- if `True`, use `np.vectorize` to make compatible with
                 `NDArray`
                 (default `True`)
    """

    raise NotImplementedError
