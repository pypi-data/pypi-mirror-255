"""
mlx.core.random: functionality related to random number generation
"""
from __future__ import annotations
import mlx.core
import typing
__all__ = ['bernoulli', 'categorical', 'gumbel', 'key', 'normal', 'randint', 'seed', 'split', 'truncated_normal', 'uniform']
def bernoulli(p: bool | int | float | complex | typing.Any = 0.5, shape: list[int] | None = None, key: mlx.core.array | None = None, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Generate Bernoulli random values.
    
            The values are sampled from the bernoulli distribution with parameter
            ``p``. The parameter ``p`` can be a :obj:`float` or :obj:`array` and
            must be broadcastable to ``shape``.
    
            Args:
                p (float or array, optional): Parameter of the Bernoulli
                  distribution. Default is 0.5.
                shape (list(int), optional): Shape of the output. The default
                  shape is ``p.shape``.
                key (array, optional): A PRNG key. Default: None.
    
            Returns:
                array: The array of random integers.
    """
def categorical(logits: mlx.core.array, axis: int = -1, shape: list[int] | None = None, num_samples: int | None = None, key: mlx.core.array | None = None, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Sample from a categorical distribution.
    
            The values are sampled from the categorical distribution specified by
            the unnormalized values in ``logits``. Note, at most one of ``shape``
            or ``num_samples`` can be specified. If both are ``None``, the output
            has the same shape as ``logits`` with the ``axis`` dimension removed.
    
            Args:
                logits (array): The *unnormalized* categorical distribution(s).
                axis (int, optional): The axis which specifies the distribution.
                   Default is ``-1``.
                shape (list(int), optional): The shape of the output. This must
                   be broadcast compatable with ``logits.shape`` with the ``axis``
                   dimension removed. Default: ``None``
                num_samples (int, optional): The number of samples to draw from each
                  of the categorical distributions in ``logits``. The output will have
                  ``num_samples`` in the last dimension. Default: ``None``.
                key (array, optional): A PRNG key. Default: None.
    
            Returns:
                array: The ``shape``-sized output array with type ``uint32``.
    """
def gumbel(shape: list[int] = [], dtype: mlx.core.Dtype | None = ..., stream: mlx.core.array | None = None, key: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Sample from the standard Gumbel distribution.
    
            The values are sampled from a standard Gumbel distribution
            which CDF ``exp(-exp(-x))``.
    
            Args:
                shape (list(int)): The shape of the output.
                key (array, optional): A PRNG key. Default: None.
    
            Returns:
                array: The :class:`array` with shape ``shape`` and
                       distributed according to the Gumbel distribution
    """
def key(seed: int) -> mlx.core.array:
    """
            Get a PRNG key from a seed.
    
            Args:
                seed (int): Seed for the PRNG.
    
            Returns:
                array: The PRNG key array.
    """
def normal(shape: list[int] = [], dtype: mlx.core.Dtype | None = ..., key: mlx.core.array | None = None, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Generate normally distributed random numbers.
    
            Args:
                shape (list(int), optional): Shape of the output. Default is ``()``.
                dtype (Dtype, optional): Type of the output. Default is ``float32``.
                key (array, optional): A PRNG key. Default: None.
    
            Returns:
                array: The output array of random values.
    """
def randint(low: bool | int | float | complex | typing.Any, high: bool | int | float | complex | typing.Any, shape: list[int] = [], dtype: mlx.core.Dtype | None = ..., key: mlx.core.array | None = None, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Generate random integers from the given interval.
    
            The values are sampled with equal probability from the integers in
            half-open interval ``[low, high)``. The lower and upper bound can be
            scalars or arrays and must be roadcastable to ``shape``.
    
            Args:
                low (scalar or array): Lower bound of the interval.
                high (scalar or array): Upper bound of the interval.
                shape (list(int), optional): Shape of the output. Defaults to ``()``.
                dtype (Dtype, optional): Type of the output. Defaults to ``int32``.
                key (array, optional): A PRNG key. Default: None.
    
            Returns:
                array: The array of random integers.
    """
def seed(seed: int) -> None:
    """
            Seed the global PRNG.
    
            Args:
                seed (int): Seed for the global PRNG.
    """
def split(key: mlx.core.array, num: int = 2, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Split a PRNG key into sub keys.
    
            Args:
                key (array): Input key to split.
                num (int, optional): Number of sub keys. Default is 2.
    
            Returns:
                array: The array of sub keys with ``num`` as its first dimension.
    """
def truncated_normal(lower: bool | int | float | complex | typing.Any, upper: bool | int | float | complex | typing.Any, shape: list[int] | None = None, dtype: mlx.core.Dtype | None = ..., key: mlx.core.array | None = None, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Generate values from a truncated normal distribution.
    
            The values are sampled from the truncated normal distribution
            on the domain ``(lower, upper)``. The bounds ``lower`` and ``upper``
            can be scalars or arrays and must be broadcastable to ``shape``.
    
            Args:
                lower (scalar or array): Lower bound of the domain.
                upper (scalar or array): Upper bound of the domain.
                shape (list(int), optional): The shape of the output.
                  Default is ``()``.
                dtype (Dtype, optional): The data type of the output.
                  Default is ``float32``.
                key (array, optional): A PRNG key. Default: None.
    
            Returns:
                array: The output array of random values.
    """
def uniform(low: bool | int | float | complex | typing.Any = 0, high: bool | int | float | complex | typing.Any = 1, shape: list[int] = [], dtype: mlx.core.Dtype | None = ..., key: mlx.core.array | None = None, stream: None | mlx.core.Stream | mlx.core.Device = None) -> mlx.core.array:
    """
            Generate uniformly distributed random numbers.
    
            The values are sampled uniformly in the half-open interval ``[low, high)``.
            The lower and upper bound can be scalars or arrays and must be
            broadcastable to ``shape``.
    
            Args:
                low (scalar or array, optional): Lower bound of the distribution. Default is ``0``.
                high (scalar or array, optional): Upper bound of the distribution. Default is ``1``.
                shape (list(int), optional): Shape of the output. Default is ``()``.
                key (array, optional): A PRNG key. Default: None.
                dtype (Dtype, optional): Type of the output. Default is ``float32``.
    
            Returns:
                array: The output array random values.
    """
