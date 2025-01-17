"""
Layout dimensions are used to give the minimum, maximum and preferred
dimensions for containers and controls.
"""
from __future__ import unicode_literals

from prompt_toolkit2.utils import test_callable_args

__all__ = [
    'Dimension',
    'D',
    'sum_layout_dimensions',
    'max_layout_dimensions',
    'to_dimension',
    'is_dimension',
]


class Dimension(object):
    """
    Specified dimension (width/height) of a user control or window.

    The layout engine tries to honor the preferred size. If that is not
    possible, because the terminal is larger or smaller, it tries to keep in
    between min and max.

    :param min: Minimum size.
    :param max: Maximum size.
    :param weight: For a VSplit/HSplit, the actual size will be determined
                   by taking the proportion of weights from all the children.
                   E.g. When there are two children, one width a weight of 1,
                   and the other with a weight of 2. The second will always be
                   twice as big as the first, if the min/max values allow it.
    :param preferred: Preferred size.
    """
    def __init__(self, min=None, max=None, weight=None, preferred=None):
        assert weight is None or (isinstance(weight, int) and weight >= 0)   # Cannot be a float.
        assert min is None or min >= 0
        assert max is None or max >= 0
        assert preferred is None or preferred >= 0

        self.min_specified = min is not None
        self.max_specified = max is not None
        self.preferred_specified = preferred is not None
        self.weight_specified = weight is not None

        if min is None:
            min = 0  # Smallest possible value.
        if max is None:  # 0-values are allowed, so use "is None"
            max = 1000 ** 10  # Something huge.
        if preferred is None:
            preferred = min
        if weight is None:
            weight = 1

        self.min = min
        self.max = max
        self.preferred = preferred
        self.weight = weight

        # Don't allow situations where max < min. (This would be a bug.)
        if max < min:
            raise ValueError('Invalid Dimension: max < min.')

        # Make sure that the 'preferred' size is always in the min..max range.
        if self.preferred < self.min:
            self.preferred = self.min

        if self.preferred > self.max:
            self.preferred = self.max

    @classmethod
    def exact(cls, amount):
        """
        Return a :class:`.Dimension` with an exact size. (min, max and
        preferred set to ``amount``).
        """
        return cls(min=amount, max=amount, preferred=amount)

    @classmethod
    def zero(cls):
        """
        Create a dimension that represents a zero size. (Used for 'invisible'
        controls.)
        """
        return cls.exact(amount=0)

    def is_zero(self):
        " True if this `Dimension` represents a zero size. "
        return self.preferred == 0 or self.max == 0

    def __repr__(self):
        fields = []
        if self.min_specified:
            fields.append('min=%r' % self.min)
        if self.max_specified:
            fields.append('max=%r' % self.max)
        if self.preferred_specified:
            fields.append('preferred=%r' % self.preferred)
        if self.weight_specified:
            fields.append('weight=%r' % self.weight)

        return 'Dimension(%s)' % ', '.join(fields)


def sum_layout_dimensions(dimensions):
    """
    Sum a list of :class:`.Dimension` instances.
    """
    min = sum(d.min for d in dimensions)
    max = sum(d.max for d in dimensions)
    preferred = sum(d.preferred for d in dimensions)

    return Dimension(min=min, max=max, preferred=preferred)


def max_layout_dimensions(dimensions):
    """
    Take the maximum of a list of :class:`.Dimension` instances.
    Used when we have a HSplit/VSplit, and we want to get the best width/height.)
    """
    if not len(dimensions):
        return Dimension.zero()

    # If all dimensions are size zero. Return zero.
    # (This is important for HSplit/VSplit, to report the right values to their
    # parent when all children are invisible.)
    if all(d.is_zero() for d in dimensions):
        return dimensions[0]

    # Ignore empty dimensions. (They should not reduce the size of others.)
    dimensions = [d for d in dimensions if not d.is_zero()]

    if dimensions:
        # Take the highest minimum dimension.
        min_ = max(d.min for d in dimensions)

        # For the maximum, we would prefer not to go larger than then smallest
        # 'max' value, unless other dimensions have a bigger preferred value.
        # This seems to work best:
        #  - We don't want that a widget with a small height in a VSplit would
        #    shrink other widgets in the split.
        # If it doesn't work well enough, then it's up to the UI designer to
        # explicitly pass dimensions.
        max_ = min(d.max for d in dimensions)
        max_ = max(max_, max(d.preferred for d in dimensions))

        # Make sure that min>=max. In some scenarios, when certain min..max
        # ranges don't have any overlap, we can end up in such an impossible
        # situation. In that case, give priority to the max value.
        # E.g. taking (1..5) and (8..9) would return (8..5). Instead take (8..8).
        if min_ > max_:
            max_ = min_

        preferred = max(d.preferred for d in dimensions)

        return Dimension(min=min_, max=max_, preferred=preferred)
    else:
        return Dimension()


def to_dimension(value):
    """
    Turn the given object into a `Dimension` object.
    """
    if value is None:
        return Dimension()
    if isinstance(value, int):
        return Dimension.exact(value)
    if isinstance(value, Dimension):
        return value
    if callable(value):
        return to_dimension(value())

    raise ValueError('Not an integer or Dimension object.')


def is_dimension(value):
    """
    Test whether the given value could be a valid dimension.
    (For usage in an assertion. It's not guaranteed in case of a callable.)
    """
    if value is None:
        return True
    if callable(value):
        return test_callable_args(value, [])
    if isinstance(value, (int, Dimension)):
        return True
    return False


# Common alias.
D = Dimension

# For backward-compatibility.
LayoutDimension = Dimension
