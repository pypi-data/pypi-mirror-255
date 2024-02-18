"""
mlx: A framework for machine learning on Apple silicon.
"""
from __future__ import annotations
import typing
from . import fft
from . import linalg
from . import metal
from . import random
__all__ = ['Device', 'DeviceType', 'Dtype', 'Inf', 'Infinity', 'NAN', 'NINF', 'NZERO', 'NaN', 'PINF', 'PZERO', 'Stream', 'abs', 'add', 'addmm', 'all', 'allclose', 'any', 'arange', 'arccos', 'arccosh', 'arcsin', 'arcsinh', 'arctan', 'arctanh', 'argmax', 'argmin', 'argpartition', 'argsort', 'array', 'array_equal', 'as_strided', 'bfloat16', 'bool_', 'broadcast_to', 'ceil', 'checkpoint', 'clip', 'compile', 'complex64', 'concatenate', 'conv1d', 'conv2d', 'convolve', 'cos', 'cosh', 'cpu', 'cummax', 'cummin', 'cumprod', 'cumsum', 'default_device', 'default_stream', 'dequantize', 'diag', 'diagonal', 'disable_compile', 'divide', 'divmod', 'e', 'enable_compile', 'equal', 'erf', 'erfinv', 'euler_gamma', 'eval', 'exp', 'expand_dims', 'export_to_dot', 'eye', 'fft', 'flatten', 'float16', 'float32', 'floor', 'floor_divide', 'full', 'gpu', 'grad', 'greater', 'greater_equal', 'identity', 'inf', 'infty', 'inner', 'int16', 'int32', 'int64', 'int8', 'isclose', 'isinf', 'isnan', 'isneginf', 'isposinf', 'jvp', 'less', 'less_equal', 'linalg', 'linspace', 'load', 'log', 'log10', 'log1p', 'log2', 'logaddexp', 'logical_and', 'logical_not', 'logical_or', 'logsumexp', 'matmul', 'max', 'maximum', 'mean', 'metal', 'min', 'minimum', 'moveaxis', 'multiply', 'nan', 'negative', 'new_stream', 'newaxis', 'not_equal', 'ones', 'ones_like', 'outer', 'pad', 'partition', 'pi', 'power', 'prod', 'quantize', 'quantized_matmul', 'random', 'reciprocal', 'remainder', 'repeat', 'reshape', 'round', 'rsqrt', 'save', 'save_gguf', 'save_safetensors', 'savez', 'savez_compressed', 'set_default_device', 'set_default_stream', 'sigmoid', 'sign', 'sin', 'sinh', 'softmax', 'sort', 'split', 'sqrt', 'square', 'squeeze', 'stack', 'stop_gradient', 'subtract', 'sum', 'swapaxes', 'take', 'take_along_axis', 'tan', 'tanh', 'tensordot', 'tile', 'topk', 'transpose', 'tri', 'tril', 'triu', 'uint16', 'uint32', 'uint64', 'uint8', 'value_and_grad', 'var', 'vjp', 'vmap', 'where', 'zeros', 'zeros_like']
class Device:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Device) -> bool:
        ...
    def __init__(self, type: DeviceType, index: int = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def type(self) -> DeviceType:
        ...
class DeviceType:
    """
    Members:
    
      cpu
    
      gpu
    """
    __members__: typing.ClassVar[dict[str, DeviceType]]  # value = {'cpu': <DeviceType.cpu: 0>, 'gpu': <DeviceType.gpu: 1>}
    cpu: typing.ClassVar[DeviceType]  # value = <DeviceType.cpu: 0>
    gpu: typing.ClassVar[DeviceType]  # value = <DeviceType.gpu: 1>
    @typing.overload
    def __eq__(self, arg0: Device) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Dtype:
    """
    
          An object to hold the type of a :class:`array`.
    
          See the :ref:`list of types <data_types>` for more details
          on available data types.
          
    """
    def __eq__(self, arg0: Dtype) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def size(self) -> int:
        """
        Size of the type in bytes.
        """
class Stream:
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Stream) -> bool:
        ...
    def __init__(self, index: int, device: Device) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def device(self) -> Device:
        ...
class _ArrayAt:
    """
    
          A helper object to apply updates at specific indices.
          
    """
    def __getitem__(self, indices: typing.Any) -> _ArrayAt:
        ...
    def __init__(self, x: array) -> None:
        """
                  __init__(self, x: array)
        """
    def add(self, value: bool | int | float | complex | typing.Any) -> array:
        ...
    def divide(self, value: bool | int | float | complex | typing.Any) -> array:
        ...
    def maximum(self, value: bool | int | float | complex | typing.Any) -> array:
        ...
    def minimum(self, value: bool | int | float | complex | typing.Any) -> array:
        ...
    def multiply(self, value: bool | int | float | complex | typing.Any) -> array:
        ...
    def subtract(self, value: bool | int | float | complex | typing.Any) -> array:
        ...
class _ArrayIterator:
    """
    
          A helper object to iterate over the 1st dimension of an array.
          
    """
    def __init__(self, x: array) -> None:
        """
                  __init__(self, x: array)
        """
    def __iter__(self) -> _ArrayIterator:
        ...
    def __next__(self) -> array:
        ...
class array:
    """
    An N-dimensional array object.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def __init__(*args, **kwargs):
        """
        
                    __init__(self: array, val: Union[scalar, list, tuple, numpy.ndarray, array], dtype: Optional[Dtype] = None)
                  
        """
    def __abs__(self) -> array:
        """
        See :func:`abs`.
        """
    def __add__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __and__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __bool__(self) -> bool:
        ...
    def __div__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __eq__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __floordiv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __ge__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __getitem__(self, arg0: typing.Any) -> array:
        ...
    def __gt__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __iadd__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __iand__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __ifloordiv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __imatmul__(self, other: array) -> array:
        ...
    def __imod__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __imul__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __invert__(self) -> array:
        ...
    def __ior__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __ipow__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __isub__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __iter__(self) -> _ArrayIterator:
        ...
    def __itruediv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __le__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __len__(self) -> int:
        ...
    def __lt__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __matmul__(self, other: array) -> array:
        ...
    def __mod__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __mul__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __ne__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __neg__(self) -> array:
        ...
    def __or__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __pow__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __radd__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __rdiv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __repr__(self) -> str:
        ...
    def __rfloordiv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __rmod__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __rmul__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __rsub__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __rtruediv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __setitem__(self, arg0: typing.Any, arg1: bool | int | float | complex | typing.Any) -> None:
        ...
    def __sub__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def __truediv__(self, other: bool | int | float | complex | typing.Any) -> array:
        ...
    def abs(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`abs`.
        """
    def all(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`all`.
        """
    def any(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`any`.
        """
    def argmax(self, axis: int | None = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`argmax`.
        """
    def argmin(self, axis: int | None = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`argmin`.
        """
    def astype(self, dtype: Dtype, stream: None | Stream | Device = None) -> array:
        """
                    Cast the array to a specified type.
        
                    Args:
                        dtype (Dtype): Type to which the array is cast.
                        stream (Stream): Stream (or device) for the operation.
        
                    Returns:
                        array: The array with type ``dtype``.
        """
    def cos(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`cos`.
        """
    def cummax(self, axis: int | None = None, *, reverse: bool = False, inclusive: bool = True, stream: None | Stream | Device = None) -> array:
        """
        See :func:`cummax`.
        """
    def cummin(self, axis: int | None = None, *, reverse: bool = False, inclusive: bool = True, stream: None | Stream | Device = None) -> array:
        """
        See :func:`cummin`.
        """
    def cumprod(self, axis: int | None = None, *, reverse: bool = False, inclusive: bool = True, stream: None | Stream | Device = None) -> array:
        """
        See :func:`cumprod`.
        """
    def cumsum(self, axis: int | None = None, *, reverse: bool = False, inclusive: bool = True, stream: None | Stream | Device = None) -> array:
        """
        See :func:`cumsum`.
        """
    def diag(self, k: int = 0, *, stream: None | Stream | Device = None) -> array:
        """
                    Extract a diagonal or construct a diagonal matrix.
        """
    def diagonal(self, offset: int = 0, axis1: int = 0, axis2: int = 1, stream: None | Stream | Device = None) -> array:
        """
        See :func:`diagonal`.
        """
    def exp(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`exp`.
        """
    def flatten(self, start_axis: int = 0, end_axis: int = -1, *, stream: None | Stream | Device = None) -> array:
        """
                    See :func:`flatten`.
        """
    def item(self) -> typing.Any:
        """
                    Access the value of a scalar array.
        
                    Returns:
                        Standard Python scalar.
        """
    def log(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`log`.
        """
    def log10(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`log10`.
        """
    def log1p(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`log1p`.
        """
    def log2(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`log2`.
        """
    def logsumexp(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`logsumexp`.
        """
    def max(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`max`.
        """
    def mean(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`mean`.
        """
    def min(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`min`.
        """
    def moveaxis(self, source: int, destination: int, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`moveaxis`.
        """
    def prod(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`prod`.
        """
    def reciprocal(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`reciprocal`.
        """
    def reshape(self, *args, stream: None | Stream | Device = None) -> array:
        """
                    Equivalent to :func:`reshape` but the shape can be passed either as a
                    tuple or as separate arguments.
        
                    See :func:`reshape` for full documentation.
        """
    def round(self, /, decimals: int = 0, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`round`.
        """
    def rsqrt(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`rsqrt`.
        """
    def sin(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`sin`.
        """
    def split(self, indices_or_sections: int | list[int], axis: int = 0, *, stream: None | Stream | Device = None) -> list[array]:
        """
        See :func:`split`.
        """
    def sqrt(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`sqrt`.
        """
    def square(self, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`square`.
        """
    def squeeze(self, axis: None | int | list[int] = None, *, stream: None | Stream | Device = None) -> array:
        """
                    See :func:`squeeze`.
        """
    def sum(self, axis: None | int | list[int] = None, keepdims: bool = False, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`sum`.
        """
    def swapaxes(self, axis1: int, axis2: int, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`swapaxes`.
        """
    def tolist(self) -> typing.Any:
        """
                    Convert the array to a Python :class:`list`.
        
                    Returns:
                        list: The Python list.
        
                        If the array is a scalar then a standard Python scalar is returned.
        
                        If the array has more than one dimension then the result is a nested
                        list of lists.
        
                        The value type of the list corresponding to the last dimension is either
                        ``bool``, ``int`` or ``float`` depending on the ``dtype`` of the array.
        """
    def transpose(self, *args, stream: None | Stream | Device = None) -> array:
        """
                    Equivalent to :func:`transpose` but the axes can be passed either as
                    a tuple or as separate arguments.
        
                    See :func:`transpose` for full documentation.
        """
    def var(self, axis: None | int | list[int] = None, keepdims: bool = False, ddof: int = 0, *, stream: None | Stream | Device = None) -> array:
        """
        See :func:`var`.
        """
    @property
    def T(self) -> array:
        """
        Equivalent to calling ``self.transpose()`` with no arguments.
        """
    @property
    def at(self) -> _ArrayAt:
        """
                    Used to apply updates at the given indices.
        
                    .. note::
        
                       Python in place updates for all array frameworks map to
                       assignment. For instance ``x[idx] += y`` maps to ``x[idx] =
                       x[idx] + y``. As a result, assigning to the same index ignores
                       all but one updates. Using ``x.at[idx].add(y)`` will correctly
                       apply all the updates to all indices.
        
                    .. list-table::
                       :header-rows: 1
        
                       * - array.at syntax
                         - In-place syntax
                       * - ``x = x.at[idx].add(y)``
                         - ``x[idx] += y``
                       * - ``x = x.at[idx].subtract(y)``
                         - ``x[idx] -= y``
                       * - ``x = x.at[idx].multiply(y)``
                         - ``x[idx] *= y``
                       * - ``x = x.at[idx].divide(y)``
                         - ``x[idx] /= y``
                       * - ``x = x.at[idx].maximum(y)``
                         - ``x[idx] = mx.maximum(x[idx], y)``
                       * - ``x = x.at[idx].minimum(y)``
                        - ``x[idx] = mx.minimum(x[idx], y)``
        """
    @property
    def dtype(self) -> Dtype:
        """
                    The array's :class:`Dtype`.
        """
    @property
    def itemsize(self) -> int:
        """
        The size of the array's datatype in bytes.
        """
    @property
    def nbytes(self) -> int:
        """
        The number of bytes in the array.
        """
    @property
    def ndim(self) -> int:
        """
        The array's dimension.
        """
    @property
    def shape(self) -> tuple:
        """
                  The shape of the array as a Python tuple.
        
                  Returns:
                    tuple(int): A tuple containing the sizes of each dimension.
        """
    @property
    def size(self) -> int:
        """
        Number of elements in the array.
        """
def abs(*args, **kwargs):
    """
    
            abs(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise absolute value.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The absolute value of ``a``.
          
    """
def add(*args, **kwargs):
    """
    
            add(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise addition.
    
            Add two arrays with numpy-style broadcasting semantics. Either or both input arrays
            can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The sum of ``a`` and ``b``.
          
    """
def addmm(*args, **kwargs):
    """
    
            addmm(c: array, a: array, b: array, /, alpha: float = 1.0, beta: float = 1.0,  *, stream: Union[None, Stream, Device] = None) -> array
    
            Matrix multiplication with addition and optional scaling.
    
            Perform the (possibly batched) matrix multiplication of two arrays and add to the result
            with optional scaling factors.
    
            Args:
                c (array): Input array or scalar.
                a (array): Input array or scalar.
                b (array): Input array or scalar.
                alpha (float, optional): Scaling factor for the
                    matrix product of ``a`` and ``b`` (default: ``1``)
                beta (float, optional): Scaling factor for ``c`` (default: ``1``)
    
            Returns:
                array: ``alpha * (a @ b)  + beta * c``
          
    """
def all(*args, **kwargs):
    """
    
            all(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            An `and` reduction over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def allclose(*args, **kwargs):
    """
    
            allclose(a: array, b: array, /, rtol: float = 1e-05, atol: float = 1e-08, *, equal_nan: bool = False, stream: Union[None, Stream, Device] = None) -> array
    
            Approximate comparison of two arrays.
    
            Infinite values are considered equal if they have the same sign, NaN values are not equal unless ``equal_nan`` is ``True``.
    
            The arrays are considered equal if:
    
            .. code-block::
    
             all(abs(a - b) <= (atol + rtol * abs(b)))
    
            Note unlike :func:`array_equal`, this function supports numpy-style
            broadcasting.
    
            Args:
                a (array): Input array.
                b (array): Input array.
                rtol (float): Relative tolerance.
                atol (float): Absolute tolerance.
                equal_nan (bool): If ``True``, NaNs are considered equal.
                  Defaults to ``False``.
    
            Returns:
                array: The boolean output scalar indicating if the arrays are close.
          
    """
def any(*args, **kwargs):
    """
    
            any(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            An `or` reduction over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def arange(*args, **kwargs):
    """
    
          arange(start, stop, step, dtype: Optional[Dtype] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
          Generates ranges of numbers.
    
          Generate numbers in the half-open interval ``[start, stop)`` in
          increments of ``step``.
    
          Args:
              start (float or int, optional): Starting value which defaults to ``0``.
              stop (float or int): Stopping value.
              step (float or int, optional): Increment which defaults to ``1``.
              dtype (Dtype, optional): Specifies the data type of the output.
                If unspecified will default to ``float32`` if any of ``start``,
                ``stop``, or ``step`` are ``float``. Otherwise will default to
                ``int32``.
    
          Returns:
              array: The range of values.
    
          Note:
            Following the Numpy convention the actual increment used to
            generate numbers is ``dtype(start + step) - dtype(start)``.
            This can lead to unexpected results for example if `start + step`
            is a fractional value and the `dtype` is integral.
          
    """
def arccos(*args, **kwargs):
    """
    
            arccos(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse cosine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse cosine of ``a``.
          
    """
def arccosh(*args, **kwargs):
    """
    
            arccosh(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse hyperbolic cosine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse hyperbolic cosine of ``a``.
          
    """
def arcsin(*args, **kwargs):
    """
    
            arcsin(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse sine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse sine of ``a``.
          
    """
def arcsinh(*args, **kwargs):
    """
    
            arcsinh(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse hyperbolic sine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse hyperbolic sine of ``a``.
          
    """
def arctan(*args, **kwargs):
    """
    
            arctan(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse tangent.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse tangent of ``a``.
          
    """
def arctanh(*args, **kwargs):
    """
    
            arctanh(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse hyperbolic tangent.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse hyperbolic tangent of ``a``.
          
    """
def argmax(*args, **kwargs):
    """
    
            argmax(a: array, /, axis: Union[None, int] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            Indices of the maximum values along the axis.
    
            Args:
                a (array): Input array.
                axis (int, optional): Optional axis to reduce over. If unspecified
                  this defaults to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The ``uint32`` array with the indices of the maximum values.
          
    """
def argmin(*args, **kwargs):
    """
    
            argmin(a: array, /, axis: Union[None, int] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            Indices of the minimum values along the axis.
    
            Args:
                a (array): Input array.
                axis (int, optional): Optional axis to reduce over. If unspecified
                  this defaults to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The ``uint32`` array with the indices of the minimum values.
          
    """
def argpartition(*args, **kwargs):
    """
    
            argpartition(a: array, /, kth: int, axis: Union[None, int] = -1, *, stream: Union[None, Stream, Device] = None) -> array
    
            Returns the indices that partition the array.
    
            The ordering of the elements within a partition in given by the indices
            is undefined.
    
            Args:
                a (array): Input array.
                kth (int): Element index at the ``kth`` position in the output will
                  give the sorted position. All indices before the ``kth`` position
                  will be of elements less or equal to the element at the ``kth``
                  index and all indices after will be of elements greater or equal
                  to the element at the ``kth`` index.
                axis (int or None, optional): Optional axis to partition over.
                  If ``None``, this partitions over the flattened array.
                  If unspecified, it defaults to ``-1``.
    
            Returns:
                array: The `uint32`` array containing indices that partition the input.
          
    """
def argsort(*args, **kwargs):
    """
    
            argsort(a: array, /, axis: Union[None, int] = -1, *, stream: Union[None, Stream, Device] = None) -> array
    
            Returns the indices that sort the array.
    
            Args:
                a (array): Input array.
                axis (int or None, optional): Optional axis to sort over.
                  If ``None``, this sorts over the flattened array.
                  If unspecified, it defaults to -1 (sorting over the last axis).
    
            Returns:
                array: The ``uint32`` array containing indices that sort the input.
          
    """
def array_equal(*args, **kwargs):
    """
    
            array_equal(a: Union[scalar, array], b: Union[scalar, array], equal_nan: bool = False, stream: Union[None, Stream, Device] = None) -> array
    
            Array equality check.
    
            Compare two arrays for equality. Returns ``True`` if and only if the arrays
            have the same shape and their values are equal. The arrays need not have
            the same type to be considered equal.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
                equal_nan (bool): If ``True``, NaNs are considered equal.
                  Defaults to ``False``.
    
            Returns:
                array: A scalar boolean array.
          
    """
def as_strided(*args, **kwargs):
    """
    
            as_strided(a: array, /, shape: Optional[List[int]] = None, strides: Optional[List[int]] = None, offset: int = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
            Create a view into the array with the given shape and strides.
    
            The resulting array will always be as if the provided array was row
            contiguous regardless of the provided arrays storage order and current
            strides.
    
            .. note::
               Note that this function should be used with caution as it changes
               the shape and strides of the array directly. This can lead to the
               resulting array pointing to invalid memory locations which can
               result into crashes.
    
            Args:
              a (array): Input array
              shape (list(int), optional): The shape of the resulting array. If
                None it defaults to ``a.shape()``.
              strides (list(int), optional): The strides of the resulting array. If
                None it defaults to the reverse exclusive cumulative product of
                ``a.shape()``.
              offset (int): Skip that many elements from the beginning of the input
                array.
    
            Returns:
              array: The output array which is the strided view of the input.
          
    """
def broadcast_to(*args, **kwargs):
    """
    
            broadcast_to(a: Union[scalar, array], /, shape: List[int], *, stream: Union[None, Stream, Device] = None) -> array
    
            Broadcast an array to the given shape.
    
            The broadcasting semantics are the same as Numpy.
    
            Args:
                a (array): Input array.
                shape (list(int)): The shape to broadcast to.
    
            Returns:
                array: The output array with the new shape.
          
    """
def ceil(*args, **kwargs):
    """
    
            ceil(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise ceil.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The ceil of ``a``.
          
    """
def checkpoint(*args, **kwargs):
    ...
def clip(*args, **kwargs):
    """
    
          clip(a: array, /, a_min: Union[scalar, array, None], a_max: Union[scalar, array, None], *, stream: Union[None, Stream, Device] = None) -> array
    
          Clip the values of the array between the given minimum and maximum.
    
          If either ``a_min`` or ``a_max`` are ``None``, then corresponding edge
          is ignored. At least one of ``a_min`` and ``a_max`` cannot be ``None``.
          The input ``a`` and the limits must broadcast with one another.
    
          Args:
              a (array): Input array.
              a_min (scalar or array or None): Minimum value to clip to.
              a_max (scalar or array or None): Maximum value to clip to.
    
          Returns:
              array: The clipped array.
        
    """
def compile(*args, **kwargs):
    """
    
            compile(fun: function) -> function
    
            Returns a compiled function which produces the same output as ``fun``.
    
            Args:
                fun (function): A function which takes a variable number of
                  :class:`array` or trees of :class:`array` and returns
                  a variable number of :class:`array` or trees of :class:`array`.
                inputs (list or dict, optional): These inputs will be captured during
                  the function compilation along with the inputs to ``fun``. The ``inputs``
                  can be a :obj:`list` or a :obj:`dict` containing arbitrarily nested
                  lists, dictionaries, or arrays. Leaf nodes that are not
                  :obj:`array` are ignored. Default: ``None``
                outputs (list or dict, optional): These outputs will be captured and
                  updated in a compiled function. The ``outputs`` can be a
                  :obj:`list` or a :obj:`dict` containing arbitrarily nested lists,
                  dictionaries, or arrays. Leaf nodes that are not :obj:`array` are ignored.
                  Default: ``None``
    
            Returns:
                function: A compiled function which has the same input arguments
                as ``fun`` and returns the the same output(s).
          
    """
def concatenate(*args, **kwargs):
    """
    
            concatenate(arrays: List[array], axis: Optional[int] = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
            Concatenate the arrays along the given axis.
    
            Args:
                arrays (list(array)): Input :obj:`list` or :obj:`tuple` of arrays.
                axis (int, optional): Optional axis to concatenate along. If
                  unspecified defaults to ``0``.
    
            Returns:
                array: The concatenated array.
          
    """
def conv1d(*args, **kwargs):
    """
    
            conv1d(input: array, weight: array, /, stride: int = 1, padding: int = 0, dilation: int = 1, groups: int = 1, *, stream: Union[None, Stream, Device] = None) -> array
    
            1D convolution over an input with several channels
    
            Note: Only the default ``groups=1`` is currently supported.
    
            Args:
                input (array): input array of shape (``N``, ``H``, ``C_in``)
                weight (array): weight array of shape (``C_out``, ``H``, ``C_in``)
                stride (int, optional): kernel stride. Default: ``1``.
                padding (int, optional): input padding. Default: ``0``.
                dilation (int, optional): kernel dilation. Default: ``1``.
                groups (int, optional): input feature groups. Default: ``1``.
    
            Returns:
                array: The convolved array.
          
    """
def conv2d(*args, **kwargs):
    """
    
            conv2d(input: array, weight: array, /, stride: Union[int, Tuple[int, int]] = 1, padding: Union[int, Tuple[int, int]] = 0, dilation: Union[int, Tuple[int, int]] = 1, groups: Union[int, Tuple[int, int]] = 1, *, stream: Union[None, Stream, Device] = None) -> array
    
            2D convolution over an input with several channels
    
            Note: Only the default ``groups=1`` is currently supported.
    
            Args:
                input (array): input array of shape ``(N, H, W, C_in)``
                weight (array): weight array of shape ``(C_out, H, W, C_in)``
                stride (int or tuple(int), optional): :obj:`tuple` of size 2 with
                    kernel strides. All spatial dimensions get the same stride if
                    only one number is specified. Default: ``1``.
                padding (int or tuple(int), optional): :obj:`tuple` of size 2 with
                    symmetric input padding. All spatial dimensions get the same
                    padding if only one number is specified. Default: ``0``.
                dilation (int or tuple(int), optional): :obj:`tuple` of size 2 with
                    kernel dilation. All spatial dimensions get the same dilation
                    if only one number is specified. Default: ``1``
                groups (int, optional): input feature groups. Default: ``1``.
    
            Returns:
                array: The convolved array.
          
    """
def convolve(*args, **kwargs):
    """
    
            convolve(a: array, v: array, /, mode: str = "full", *, stream: Union[None, Stream, Device] = None) -> array
    
            The discrete convolution of 1D arrays.
    
            If ``v`` is longer than ``a``, then they are swapped.
            The conv filter is flipped following signal processing convention.
    
            Args:
                a (array): 1D Input array.
                v (array): 1D Input array.
                mode (str, optional): {'full', 'valid', 'same'}
    
            Returns:
                array: The convolved array.
          
    """
def cos(*args, **kwargs):
    """
    
            cos(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise cosine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The cosine of ``a``.
          
    """
def cosh(*args, **kwargs):
    """
    
            cosh(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise hyperbolic cosine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The hyperbolic cosine of ``a``.
          
    """
def cummax(*args, **kwargs):
    """
    
            cummax(a: array, /, axis: Optional[int] = None, *, reverse: bool = False, inclusive: bool = True, stream: Union[None, Stream, Device] = None) -> array
    
            Return the cumulative maximum of the elements along the given axis.
    
            Args:
              a (array): Input array
              axis (int, optional): Optional axis to compute the cumulative maximum
                over. If unspecified the cumulative maximum of the flattened array is
                returned.
              reverse (bool): Perform the cumulative maximum in reverse.
              inclusive (bool): The i-th element of the output includes the i-th
                element of the input.
          
    """
def cummin(*args, **kwargs):
    """
    
            cummin(a: array, /, axis: Optional[int] = None, *, reverse: bool = False, inclusive: bool = True, stream: Union[None, Stream, Device] = None) -> array
    
            Return the cumulative minimum of the elements along the given axis.
    
            Args:
              a (array): Input array
              axis (int, optional): Optional axis to compute the cumulative minimum
                over. If unspecified the cumulative minimum of the flattened array is
                returned.
              reverse (bool): Perform the cumulative minimum in reverse.
              inclusive (bool): The i-th element of the output includes the i-th
                element of the input.
          
    """
def cumprod(*args, **kwargs):
    """
    
            cumprod(a: array, /, axis: Optional[int] = None, *, reverse: bool = False, inclusive: bool = True, stream: Union[None, Stream, Device] = None) -> array
    
            Return the cumulative product of the elements along the given axis.
    
            Args:
              a (array): Input array
              axis (int, optional): Optional axis to compute the cumulative product
                over. If unspecified the cumulative product of the flattened array is
                returned.
              reverse (bool): Perform the cumulative product in reverse.
              inclusive (bool): The i-th element of the output includes the i-th
                element of the input.
          
    """
def cumsum(*args, **kwargs):
    """
    
            cumsum(a: array, /, axis: Optional[int] = None, *, reverse: bool = False, inclusive: bool = True, stream: Union[None, Stream, Device] = None) -> array
    
            Return the cumulative sum of the elements along the given axis.
    
            Args:
              a (array): Input array
              axis (int, optional): Optional axis to compute the cumulative sum
                over. If unspecified the cumulative sum of the flattened array is
                returned.
              reverse (bool): Perform the cumulative sum in reverse.
              inclusive (bool): The i-th element of the output includes the i-th
                element of the input.
          
    """
def default_device() -> Device:
    ...
def default_stream(device: Device) -> Stream:
    ...
def dequantize(*args, **kwargs):
    """
    
            dequantize(w: array, /, scales: array, biases: array, group_size: int = 64, bits: int = 4, *, stream: Union[None, Stream, Device] = None) -> array
    
            Dequantize the matrix ``w`` using the provided ``scales`` and
            ``biases`` and the ``group_size`` and ``bits`` configuration.
    
            Formally, given the notation in :func:`quantize`, we compute
            :math:`w_i` from :math:`\hat{w_i}` and corresponding :math:`s` and
            :math:`\beta` as follows
    
            .. math::
    
              w_i = s \hat{w_i} - \beta
    
            Args:
              w (array): Matrix to be quantized
              scales (array): The scales to use per ``group_size`` elements of ``w``
              biases (array): The biases to use per ``group_size`` elements of ``w``
              group_size (int, optional): The size of the group in ``w`` that shares a
                scale and bias. (default: ``64``)
              bits (int, optional): The number of bits occupied by each element in
                ``w``. (default: ``4``)
    
            Returns:
              result (array): The dequantized version of ``w``
          
    """
def diag(*args, **kwargs):
    """
    
            diag(a: array, /, k: int = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
            Extract a diagonal or construct a diagonal matrix.
            If ``a`` is 1-D then a diagonal matrix is constructed with ``a`` on the
            :math:`k`-th diagonal. If ``a`` is 2-D then the :math:`k`-th diagonal is
            returned.
    
            Args:
                a (array): 1-D or 2-D input array.
                k (int, optional): The diagonal to extract or construct.
                    Default: ``0``.
    
            Returns:
                array: The extracted diagonal or the constructed diagonal matrix.
            
    """
def diagonal(*args, **kwargs):
    """
    
            diagonal(a: array, offset: int = 0, axis1: int = 0, axis2: int = 1, stream: Union[None, Stream, Device] = None) -> array
    
            Return specified diagonals.
    
            If ``a`` is 2-D, then a 1-D array containing the diagonal at the given
            ``offset`` is returned.
    
            If ``a`` has more than two dimensions, then ``axis1`` and ``axis2``
            determine the 2D subarrays from which diagonals are extracted. The new
            shape is the original shape with ``axis1`` and ``axis2`` removed and a
            new dimension inserted at the end corresponding to the diagonal.
    
            Args:
              a (array): Input array
              offset (int, optional): Offset of the diagonal from the main diagonal.
                Can be positive or negative. Default: ``0``.
              axis1 (int, optional): The first axis of the 2-D sub-arrays from which
                  the diagonals should be taken. Default: ``0``.
              axis2 (int, optional): The second axis of the 2-D sub-arrays from which
                  the diagonals should be taken. Default: ``1``.
    
            Returns:
                array: The diagonals of the array.
          
    """
def disable_compile(*args, **kwargs):
    """
    
            disable_compile() -> None
    
            Globally disable compilation. Setting the environment variable
            ``MLX_DISABLE_COMPILE`` can also be used to disable compilation.
          
    """
def divide(*args, **kwargs):
    """
    
            divide(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise division.
    
            Divide two arrays with numpy-style broadcasting semantics. Either or both
            input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The quotient ``a / b``.
          
    """
def divmod(*args, **kwargs):
    """
    
            divmod(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise quotient and remainder.
    
            The fuction ``divmod(a, b)`` is equivalent to but faster than
            ``(a // b, a % b)``. The function uses numpy-style broadcasting
            semantics. Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                tuple(array, array): The quotient ``a // b`` and remainder ``a % b``.
          
    """
def enable_compile(*args, **kwargs):
    """
    
            enable_compile() -> None
    
            Globally enable compilation. This will override the environment
            variable ``MLX_DISABLE_COMPILE`` if set.
          
    """
def equal(*args, **kwargs):
    """
    
            equal(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise equality.
    
            Equality comparison on two arrays with numpy-style broadcasting semantics.
            Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The element-wise comparison ``a == b``.
          
    """
def erf(*args, **kwargs):
    """
    
            erf(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise error function.
    
            .. math::
              \mathrm{erf}(x) = \frac{2}{\sqrt{\pi}} \int_0^x e^{-t^2} \, dt
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The error function of ``a``.
          
    """
def erfinv(*args, **kwargs):
    """
    
            erfinv(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise inverse of :func:`erf`.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The inverse error function of ``a``.
          
    """
def eval(*args, **kwargs):
    """
    
            eval(*args) -> None
    
            Evaluate an :class:`array` or tree of :class:`array`.
    
            Args:
                *args (arrays or trees of arrays): Each argument can be a single array
                  or a tree of arrays. If a tree is given the nodes can be a Python
                  :class:`list`, :class:`tuple` or :class:`dict`. Leaves which are not
                  arrays are ignored.
          
    """
def exp(*args, **kwargs):
    """
    
            exp(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise exponential.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The exponential of ``a``.
          
    """
def expand_dims(*args, **kwargs):
    """
    
            expand_dims(a: array, /, axis: Union[int, List[int]], *, stream: Union[None, Stream, Device] = None) -> array
    
            Add a size one dimension at the given axis.
    
            Args:
                a (array): Input array.
                axes (int or tuple(int)): The index of the inserted dimensions.
    
            Returns:
                array: The array with inserted dimensions.
          
    """
def export_to_dot(*args, **kwargs):
    ...
def eye(*args, **kwargs):
    """
    
          eye(n: int, m: Optional[int] = None, k: int = 0, dtype: Optional[Dtype] = float32, *, stream: Union[None, Stream, Device] = None) -> array
    
          Create an identity matrix or a general diagonal matrix.
    
          Args:
              n (int): The number of rows in the output.
              m (int, optional): The number of columns in the output. Defaults to n.
              k (int, optional): Index of the diagonal. Defaults to 0 (main diagonal).
              dtype (Dtype, optional): Data type of the output array. Defaults to float32.
              stream (Stream, optional): Stream or device. Defaults to None.
    
          Returns:
              array: An array where all elements are equal to zero, except for the k-th diagonal, whose values are equal to one.
          
    """
def flatten(*args, **kwargs):
    """
    
          flatten(a: array, /, start_axis: int = 0, end_axis: int = -1, *, stream: Union[None, Stream, Device] = None) -> array
    
          Flatten an array.
    
          The axes flattened will be between ``start_axis`` and ``end_axis``,
          inclusive. Negative axes are supported. After converting negative axis to
          positive, axes outside the valid range will be clamped to a valid value,
          ``start_axis`` to ``0`` and ``end_axis`` to ``ndim - 1``.
    
          Args:
              a (array): Input array.
              start_axis (int, optional): The first dimension to flatten. Defaults to ``0``.
              end_axis (int, optional): The last dimension to flatten. Defaults to ``-1``.
              stream (Stream, optional): Stream or device. Defaults to ``None``
                in which case the default stream of the default device is used.
    
          Returns:
              array: The flattened array.
    
          Example:
              >>> a = mx.array([[1, 2], [3, 4]])
              >>> mx.flatten(a)
              array([1, 2, 3, 4], dtype=int32)
              >>>
              >>> mx.flatten(a, start_axis=0, end_axis=-1)
              array([1, 2, 3, 4], dtype=int32)
      
    """
def floor(*args, **kwargs):
    """
    
            floor(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise floor.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The floor of ``a``.
          
    """
def floor_divide(*args, **kwargs):
    """
    
            floor_divide(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise integer division.
    
            If either array is a floating point type then it is equivalent to
            calling :func:`floor` after :func:`divide`.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The quotient ``a // b``.
          
    """
def full(*args, **kwargs):
    """
    
            full(shape: Union[int, List[int]], vals: Union[scalar, array], dtype: Optional[Dtype] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            Construct an array with the given value.
    
            Constructs an array of size ``shape`` filled with ``vals``. If ``vals``
            is an :obj:`array` it must be broadcastable to the given ``shape``.
    
            Args:
                shape (int or list(int)): The shape of the output array.
                vals (float or int or array): Values to fill the array with.
                dtype (Dtype, optional): Data type of the output array. If
                  unspecified the output type is inferred from ``vals``.
    
            Returns:
                array: The output array with the specified shape and values.
          
    """
def grad(*args, **kwargs):
    """
    
            grad(fun: function, argnums: Optional[Union[int, List[int]]] = None, argnames: Union[str, List[str]] = []) -> function
    
            Returns a function which computes the gradient of ``fun``.
    
            Args:
                fun (function): A function which takes a variable number of
                  :class:`array` or trees of :class:`array` and returns
                  a scalar output :class:`array`.
                argnums (int or list(int), optional): Specify the index (or indices)
                  of the positional arguments of ``fun`` to compute the gradient
                  with respect to. If neither ``argnums`` nor ``argnames`` are
                  provided ``argnums`` defaults to ``0`` indicating ``fun``'s first
                  argument.
                argnames (str or list(str), optional): Specify keyword arguments of
                  ``fun`` to compute gradients with respect to. It defaults to [] so
                  no gradients for keyword arguments by default.
    
            Returns:
                function: A function which has the same input arguments as ``fun`` and
                returns the gradient(s).
          
    """
def greater(*args, **kwargs):
    """
    
            greater(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise greater than.
    
            Strict greater than on two arrays with numpy-style broadcasting semantics.
            Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The element-wise comparison ``a > b``.
          
    """
def greater_equal(*args, **kwargs):
    """
    
            greater_equal(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise greater or equal.
    
            Greater than or equal on two arrays with numpy-style broadcasting semantics.
            Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The element-wise comparison ``a >= b``.
          
    """
def identity(*args, **kwargs):
    """
    
          identity(n: int, dtype: Optional[Dtype] = float32, *, stream: Union[None, Stream, Device] = None) -> array
    
          Create a square identity matrix.
    
          Args:
              n (int): The number of rows and columns in the output.
              dtype (Dtype, optional): Data type of the output array. Defaults to float32.
              stream (Stream, optional): Stream or device. Defaults to None.
    
          Returns:
              array: An identity matrix of size n x n.
          
    """
def inner(*args, **kwargs):
    """
    
          inner(a: array, b: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
          Ordinary inner product of vectors for 1-D arrays, in higher dimensions a sum product over the last axes.
    
          Args:
            a (array): Input array
            b (array): Input array
    
          Returns:
            result (array): The inner product.
        
    """
def isclose(*args, **kwargs):
    """
    
            isclose(a: array, b: array, /, rtol: float = 1e-05, atol: float = 1e-08, *, equal_nan: bool = False, stream: Union[None, Stream, Device] = None) -> array
    
            Returns a boolean array where two arrays are element-wise equal within a tolerance.
    
            Infinite values are considered equal if they have the same sign, NaN values are
            not equal unless ``equal_nan`` is ``True``.
    
            Two values are considered equal if:
    
            .. code-block::
    
             abs(a - b) <= (atol + rtol * abs(b))
    
            Note unlike :func:`array_equal`, this function supports numpy-style
            broadcasting.
    
            Args:
                a (array): Input array.
                b (array): Input array.
                rtol (float): Relative tolerance.
                atol (float): Absolute tolerance.
                equal_nan (bool): If ``True``, NaNs are considered equal.
                  Defaults to ``False``.
    
            Returns:
                array: The boolean output scalar indicating if the arrays are close.
          
    """
def isinf(*args, **kwargs):
    """
    
            isinf(a: array, stream: Union[None, Stream, Device] = None) -> array
    
            Return a boolean array indicating which elements are +/- inifnity.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The boolean array indicating which elements are +/- infinity.
          
    """
def isnan(*args, **kwargs):
    """
    
            isnan(a: array, stream: Union[None, Stream, Device] = None) -> array
    
            Return a boolean array indicating which elements are NaN.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The boolean array indicating which elements are NaN.
          
    """
def isneginf(*args, **kwargs):
    """
    
            isneginf(a: array, stream: Union[None, Stream, Device] = None) -> array
    
            Return a boolean array indicating which elements are negative infinity.
    
            Args:
                a (array): Input array.
                stream (Union[None, Stream, Device]): Optional stream or device.
    
            Returns:
                array: The boolean array indicating which elements are negative infinity.
          
    """
def isposinf(*args, **kwargs):
    """
    
            isposinf(a: array, stream: Union[None, Stream, Device] = None) -> array
    
            Return a boolean array indicating which elements are positive infinity.
    
            Args:
                a (array): Input array.
                stream (Union[None, Stream, Device]): Optional stream or device.
    
            Returns:
                array: The boolean array indicating which elements are positive infinity.
          
    """
def jvp(*args, **kwargs):
    """
    
            jvp(fun: function, primals: List[array], tangents: List[array]) -> Tuple[List[array], List[array]]
    
    
            Compute the Jacobian-vector product.
    
            This computes the product of the Jacobian of a function ``fun`` evaluated
            at ``primals`` with the ``tangents``.
    
            Args:
                fun (function): A function which takes a variable number of :class:`array`
                  and returns a single :class:`array` or list of :class:`array`.
                primals (list(array)): A list of :class:`array` at which to
                  evaluate the Jacobian.
                tangents (list(array)): A list of :class:`array` which are the
                  "vector" in the Jacobian-vector product. The ``tangents`` should be the
                  same in number, shape, and type as the inputs of ``fun`` (i.e. the ``primals``).
    
            Returns:
                list(array): A list of the Jacobian-vector products which
                is the same in number, shape, and type of the inputs to ``fun``.
          
    """
def less(*args, **kwargs):
    """
    
            less(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise less than.
    
            Strict less than on two arrays with numpy-style broadcasting semantics.
            Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The element-wise comparison ``a < b``.
          
    """
def less_equal(*args, **kwargs):
    """
    
            less_equal(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise less than or equal.
    
            Less than or equal on two arrays with numpy-style broadcasting semantics.
            Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The element-wise comparison ``a <= b``.
          
    """
def linspace(*args, **kwargs):
    """
    
          linspace(start, stop, num: Optional[int] = 50, dtype: Optional[Dtype] = float32, stream: Union[None, Stream, Device] = None) -> array
    
          Generate ``num`` evenly spaced numbers over interval ``[start, stop]``.
    
          Args:
              start (scalar): Starting value.
              stop (scalar): Stopping value.
              num (int, optional): Number of samples, defaults to ``50``.
              dtype (Dtype, optional): Specifies the data type of the output,
              default to ``float32``.
    
          Returns:
              array: The range of values.
          
    """
def load(*args, **kwargs):
    """
    
            load(file: str, /, format: Optional[str] = None, return_metadata: bool = False, *, stream: Union[None, Stream, Device] = None) -> Union[array, Dict[str, array]]
    
            Load array(s) from a binary file.
    
            The supported formats are ``.npy``, ``.npz``, ``.safetensors``, and ``.gguf``.
    
            Args:
                file (file, str): File in which the array is saved.
                format (str, optional): Format of the file. If ``None``, the format
                  is inferred from the file extension. Supported formats: ``npy``,
                  ``npz``, and ``safetensors``. Default: ``None``.
                return_metadata (bool, optional): Load the metadata for formats which
                  support matadata. The metadata will be returned as an additional
                  dictionary.
            Returns:
                result (array, dict):
                    A single array if loading from a ``.npy`` file or a dict mapping
                    names to arrays if loading from a ``.npz`` or ``.safetensors`` file.
                    If ``return_metadata` is ``True`` an additional dictionary of metadata
                    will be returned.
    
            Warning:
    
              When loading unsupported quantization formats from GGUF, tensors will
              automatically cast to ``mx.float16``
    
          
    """
def log(*args, **kwargs):
    """
    
            log(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise natural logarithm.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The natural logarithm of ``a``.
          
    """
def log10(*args, **kwargs):
    """
    
            log10(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise base-10 logarithm.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The base-10 logarithm of ``a``.
          
    """
def log1p(*args, **kwargs):
    """
    
            log1p(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise natural log of one plus the array.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The natural logarithm of one plus ``a``.
          
    """
def log2(*args, **kwargs):
    """
    
            log2(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise base-2 logarithm.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The base-2 logarithm of ``a``.
          
    """
def logaddexp(*args, **kwargs):
    """
    
            logaddexp(a: Union[scalar, array], b: Union[scalar, array], /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise log-add-exp.
    
            This is a numerically stable log-add-exp of two arrays with numpy-style
            broadcasting semantics. Either or both input arrays can also be scalars.
    
            The computation is is a numerically stable version of ``log(exp(a) + exp(b))``.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The log-add-exp of ``a`` and ``b``.
          
    """
def logical_and(*args, **kwargs):
    """
    
            logical_and(a: array, b: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise logical and.
    
            Args:
                a (array): First input array or scalar.
                b (array): Second input array or scalar.
    
            Returns:
                array: The boolean array containing the logical and of ``a`` and ``b``.
        
    """
def logical_not(*args, **kwargs):
    """
    
            logical_not(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise logical not.
    
            Args:
                a (array): Input array or scalar.
    
            Returns:
                array: The boolean array containing the logical not of ``a``.
          
    """
def logical_or(*args, **kwargs):
    """
    
            logical_or(a: array, b: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise logical or.
    
            Args:
                a (array): First input array or scalar.
                b (array): Second input array or scalar.
    
            Returns:
                array: The boolean array containing the logical or of ``a`` and ``b``.
        
    """
def logsumexp(*args, **kwargs):
    """
    
            logsumexp(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            A `log-sum-exp` reduction over the given axes.
    
            The log-sum-exp reduction is a numerically stable version of:
    
            .. code-block::
    
              log(sum(exp(a), axis))
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def matmul(*args, **kwargs):
    """
    
            matmul(a: array, b: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Matrix multiplication.
    
            Perform the (possibly batched) matrix multiplication of two arrays. This function supports
            broadcasting for arrays with more than two dimensions.
    
            - If the first array is 1-D then a 1 is prepended to its shape to make it
              a matrix. Similarly if the second array is 1-D then a 1 is appended to its
              shape to make it a matrix. In either case the singleton dimension is removed
              from the result.
            - A batched matrix multiplication is performed if the arrays have more than
              2 dimensions.  The matrix dimensions for the matrix product are the last
              two dimensions of each input.
            - All but the last two dimensions of each input are broadcast with one another using
              standard numpy-style broadcasting semantics.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The matrix product of ``a`` and ``b``.
          
    """
def max(*args, **kwargs):
    """
    
            max(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            An `max` reduction over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def maximum(*args, **kwargs):
    """
    
            maximum(a: Union[scalar, array], b: Union[scalar, array], /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise maximum.
    
            Take the element-wise max of two arrays with numpy-style broadcasting
            semantics. Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The max of ``a`` and ``b``.
          
    """
def mean(*args, **kwargs):
    """
    
            mean(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            Compute the mean(s) over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array of means.
          
    """
def min(*args, **kwargs):
    """
    
            min(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            An `min` reduction over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def minimum(*args, **kwargs):
    """
    
            minimum(a: Union[scalar, array], b: Union[scalar, array], /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise minimum.
    
            Take the element-wise min of two arrays with numpy-style broadcasting
            semantics. Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The min of ``a`` and ``b``.
          
    """
def moveaxis(*args, **kwargs):
    """
    
            moveaxis(a: array, /, source: int, destination: int, *, stream: Union[None, Stream, Device] = None) -> array
    
            Move an axis to a new position.
    
            Args:
                a (array): Input array.
                source (int): Specifies the source axis.
                destination (int): Specifies the destination axis.
    
            Returns:
                array: The array with the axis moved.
          
    """
def multiply(*args, **kwargs):
    """
    
            multiply(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise multiplication.
    
            Multiply two arrays with numpy-style broadcasting semantics. Either or both
            input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The multiplication ``a * b``.
          
    """
def negative(*args, **kwargs):
    """
    
            negative(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise negation.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The negative of ``a``.
          
    """
def new_stream(device: Device) -> Stream:
    ...
def not_equal(*args, **kwargs):
    """
    
            not_equal(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise not equal.
    
            Not equal comparison on two arrays with numpy-style broadcasting semantics.
            Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The element-wise comparison ``a != b``.
          
    """
def ones(*args, **kwargs):
    """
    
            ones(shape: Union[int, List[int]], dtype: Optional[Dtype] = float32, *, stream: Union[None, Stream, Device] = None) -> array
    
            Construct an array of ones.
    
            Args:
                shape (int or list(int)): The shape of the output array.
                dtype (Dtype, optional): Data type of the output array. If
                  unspecified the output type defaults to ``float32``.
    
            Returns:
                array: The array of ones with the specified shape.
          
    """
def ones_like(*args, **kwargs):
    """
    
            ones_like(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            An array of ones like the input.
    
            Args:
                a (array): The input to take the shape and type from.
    
            Returns:
                array: The output array filled with ones.
          
    """
def outer(*args, **kwargs):
    """
    
          outer(a: array, b: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
          Compute the outer product of two 1-D arrays, if the array's passed are not 1-D a flatten op will be run beforehand.
    
          Args:
            a (array): Input array
            b (array): Input array
    
          Returns:
            result (array): The outer product.
        
    """
def pad(*args, **kwargs):
    """
    
            pad(a: array, pad_with: Union[int, Tuple[int], Tuple[int, int], List[Tuple[int, int]]], constant_values: Union[scalar, array] = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
            Pad an array with a constant value
    
            Args:
                a (array): Input array.
                pad_width (int, tuple(int), tuple(int, int) or list(tuple(int, int))): Number of padded
                  values to add to the edges of each axis:``((before_1, after_1),
                  (before_2, after_2), ..., (before_N, after_N))``. If a single pair
                  of integers is passed then ``(before_i, after_i)`` are all the same.
                  If a single integer or tuple with a single integer is passed then
                  all axes are extended by the same number on each side.
                constant_value (array or scalar, optional): Optional constant value
                  to pad the edges of the array with.
    
            Returns:
                array: The padded array.
          
    """
def partition(*args, **kwargs):
    """
    
            partition(a: array, /, kth: int, axis: Union[None, int] = -1, *, stream: Union[None, Stream, Device] = None) -> array
    
            Returns a partitioned copy of the array such that the smaller ``kth``
            elements are first.
    
            The ordering of the elements in partitions is undefined.
    
            Args:
                a (array): Input array.
                kth (int): Element at the ``kth`` index will be in its sorted
                  position in the output. All elements before the kth index will
                  be less or equal to the ``kth`` element and all elements after
                  will be greater or equal to the ``kth`` element in the output.
                axis (int or None, optional): Optional axis to partition over.
                  If ``None``, this partitions over the flattened array.
                  If unspecified, it defaults to ``-1``.
    
            Returns:
                array: The partitioned array.
          
    """
def power(*args, **kwargs):
    """
    
            power(a: Union[scalar, array], b: Union[scalar, array], /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise power operation.
    
            Raise the elements of a to the powers in elements of b with numpy-style
            broadcasting semantics. Either or both input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: Bases of ``a`` raised to powers in ``b``.
          
    """
def prod(*args, **kwargs):
    """
    
            prod(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            An product reduction over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def quantize(*args, **kwargs):
    """
    
            quantize(w: array, /, group_size: int = 64, bits : int = 4, *, stream: Union[None, Stream, Device] = None) -> Tuple[array, array, array]
    
            Quantize the matrix ``w`` using ``bits`` bits per element.
    
            Note, every ``group_size`` elements in a row of ``w`` are quantized
            together. Hence, number of columns of ``w`` should be divisible by
            ``group_size``. In particular, the rows of ``w`` are divided into groups of
            size ``group_size`` which are quantized together.
    
            .. warning::
    
              ``quantize`` currently only supports 2D inputs with dimensions which are multiples of 32
    
            Formally, for a group of :math:`g` consecutive elements :math:`w_1` to
            :math:`w_g` in a row of ``w`` we compute the quantized representation
            of each element :math:`\hat{w_i}` as follows
    
            .. math::
    
              \begin{aligned}
                \alpha &= \max_i w_i \\
                \beta &= \min_i w_i \\
                s &= \frac{\alpha - \beta}{2^b - 1} \\
                \hat{w_i} &= \textrm{round}\left( \frac{w_i - \beta}{s}\right).
              \end{aligned}
    
            After the above computation, :math:`\hat{w_i}` fits in :math:`b` bits
            and is packed in an unsigned 32-bit integer from the lower to upper
            bits. For instance, for 4-bit quantization we fit 8 elements in an
            unsigned 32 bit integer where the 1st element occupies the 4 least
            significant bits, the 2nd bits 4-7 etc.
    
            In order to be able to dequantize the elements of ``w`` we also need to
            save :math:`s` and :math:`\beta` which are the returned ``scales`` and
            ``biases`` respectively.
    
            Args:
              w (array): Matrix to be quantized
              group_size (int, optional): The size of the group in ``w`` that shares a
                scale and bias. (default: ``64``)
              bits (int, optional): The number of bits occupied by each element of
                ``w`` in the returned quantized matrix. (default: ``4``)
    
            Returns:
              (tuple): A tuple containing
    
                - w_q (array): The quantized version of ``w``
                - scales (array): The scale to multiply each element with, namely :math:`s`
                - biases (array): The biases to add to each element, namely :math:`\beta`
          
    """
def quantized_matmul(*args, **kwargs):
    """
    
            quantized_matmul(x: array, w: array, /, scales: array, biases: array, transpose: bool = True, group_size: int = 64, bits: int = 4, *, stream: Union[None, Stream, Device] = None) -> array
    
            Perform the matrix multiplication with the quantized matrix ``w``. The
            quantization uses one floating point scale and bias per ``group_size`` of
            elements. Each element in ``w`` takes ``bits`` bits and is packed in an
            unsigned 32 bit integer.
    
            Args:
              x (array): Input array
              w (array): Quantized matrix packed in unsigned integers
              scales (array): The scales to use per ``group_size`` elements of ``w``
              biases (array): The biases to use per ``group_size`` elements of ``w``
              transpose (bool, optional): Defines whether to multiply with the
                transposed ``w`` or not, namely whether we are performing
                ``x @ w.T`` or ``x @ w``. (default: ``True``)
              group_size (int, optional): The size of the group in ``w`` that
                shares a scale and bias. (default: ``64``)
              bits (int, optional): The number of bits occupied by each element in
                ``w``. (default: ``4``)
    
            Returns:
              result (array): The result of the multiplication of ``x`` with ``w``.
          
    """
def reciprocal(*args, **kwargs):
    """
    
            reciprocal(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise reciprocal.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The reciprocal of ``a``.
          
    """
def remainder(*args, **kwargs):
    """
    
            remainder(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise remainder of division.
    
            Computes the remainder of dividing a with b with numpy-style
            broadcasting semantics. Either or both input arrays can also be
            scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The remainder of ``a // b``.
          
    """
def repeat(*args, **kwargs):
    """
    
          repeat(array: array, repeats: int, axis: Optional[int] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
          Repeat an array along a specified axis.
    
          Args:
              array (array): Input array.
              repeats (int): The number of repetitions for each element.
              axis (int, optional): The axis in which to repeat the array along. If
                unspecified it uses the flattened array of the input and repeats
                along axis 0.
              stream (Stream, optional): Stream or device. Defaults to ``None``.
    
          Returns:
              array: The resulting repeated array.
        
    """
def reshape(*args, **kwargs):
    """
    
            reshape(a: array, /, shape: List[int], *, stream: Union[None, Stream, Device] = None) -> array
    
            Reshape an array while preserving the size.
    
            Args:
                a (array): Input array.
                shape (tuple(int)): New shape.
                stream (Stream, optional): Stream or device. Defaults to ``None``
                  in which case the default stream of the default device is used.
    
            Returns:
                array: The reshaped array.
          
    """
def round(*args, **kwargs):
    """
    
            round(a: array, /, decimals: int = 0, stream: Union[None, Stream, Device] = None) -> array
    
            Round to the given number of decimals.
    
            Basically performs:
    
            .. code-block:: python
    
              s = 10**decimals
              x = round(x * s) / s
    
            Args:
              a (array): Input array
              decimals (int): Number of decimal places to round to. (default: 0)
    
            Returns:
              result (array): An array of the same type as ``a`` rounded to the given number of decimals.
          
    """
def rsqrt(*args, **kwargs):
    """
    
            rsqrt(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise reciprocal and square root.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: One over the square root of ``a``.
          
    """
def save(*args, **kwargs):
    """
    
            save(file: str, arr: array)
    
            Save the array to a binary file in ``.npy`` format.
    
            Args:
                file (str): File to which the array is saved
                arr (array): Array to be saved.
          
    """
def save_gguf(*args, **kwargs):
    """
    
            save_gguf(file: str, arrays: Dict[str, array], metadata: Dict[str, Union[array, str, List[str]]])
    
            Save array(s) to a binary file in ``.gguf`` format.
    
            See the `GGUF documentation <https://github.com/ggerganov/ggml/blob/master/docs/gguf.md>`_ for
            more information on the format.
    
            Args:
                file (file, str): File in which the array is saved.
                arrays (dict(str, array)): The dictionary of names to arrays to be saved.
                metadata (dict(str, Union[array, str, list(str)])): The dictionary of
                   metadata to be saved. The values can be a scalar or 1D obj:`array`,
                   a :obj:`str`, or a :obj:`list` of :obj:`str`.
          
    """
def save_safetensors(*args, **kwargs):
    """
    
            save_safetensors(file: str, arrays: Dict[str, array])
    
            Save array(s) to a binary file in ``.safetensors`` format.
    
            See the `Safetensors documentation <https://huggingface.co/docs/safetensors/index>`_
            for more information on the format.
    
            Args:
                file (file, str): File in which the array is saved.
                arrays (dict(str, array)): The dictionary of names to arrays to be saved.
          
    """
def savez(*args, **kwargs):
    """
    
            savez(file: str, *args, **kwargs)
    
            Save several arrays to a binary file in uncompressed ``.npz`` format.
    
            .. code-block:: python
    
                import mlx.core as mx
    
                x = mx.ones((10, 10))
                mx.savez("my_path.npz", x=x)
    
                import mlx.nn as nn
                from mlx.utils import tree_flatten
    
                model = nn.TransformerEncoder(6, 128, 4)
                flat_params = tree_flatten(model.parameters())
                mx.savez("model.npz", **dict(flat_params))
    
            Args:
                file (file, str): Path to file to which the arrays are saved.
                args (arrays): Arrays to be saved.
                kwargs (arrays): Arrays to be saved. Each array will be saved
                  with the associated keyword as the output file name.
    
          
    """
def savez_compressed(*args, **kwargs):
    """
    
            savez_compressed(file: str, *args, **kwargs)
    
            Save several arrays to a binary file in compressed ``.npz`` format.
    
            Args:
                file (file, str): Path to file to which the arrays are saved.
                args (arrays): Arrays to be saved.
                kwargs (arrays): Arrays to be saved. Each array will be saved
                  with the associated keyword as the output file name.
    
          
    """
def set_default_device(device: Device) -> None:
    ...
def set_default_stream(stream: Stream) -> None:
    ...
def sigmoid(*args, **kwargs):
    """
    
            sigmoid(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise logistic sigmoid.
    
            The logistic sigmoid function is:
    
            .. math::
              \mathrm{sigmoid}(x) = \frac{1}{1 + e^{-x}}
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The logistic sigmoid of ``a``.
          
    """
def sign(*args, **kwargs):
    """
    
            sign(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise sign.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The sign of ``a``.
          
    """
def sin(*args, **kwargs):
    """
    
            sin(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise sine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The sine of ``a``.
          
    """
def sinh(*args, **kwargs):
    """
    
            sinh(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise hyperbolic sine.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The hyperbolic sine of ``a``.
          
    """
def softmax(*args, **kwargs):
    """
    
            softmax(a: array, /, axis: Union[None, int, List[int]] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            Perform the softmax along the given axis.
    
            This operation is a numerically stable version of:
    
            .. code-block::
    
              exp(a) / sum(exp(a), axis, keepdims=True)
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or axes to compute
                 the softmax over. If unspecified this performs the softmax over
                 the full array.
    
            Returns:
                array: The output of the softmax.
          
    """
def sort(*args, **kwargs):
    """
    
            sort(a: array, /, axis: Union[None, int] = -1, *, stream: Union[None, Stream, Device] = None) -> array
    
            Returns a sorted copy of the array.
    
            Args:
                a (array): Input array.
                axis (int or None, optional): Optional axis to sort over.
                  If ``None``, this sorts over the flattened array.
                  If unspecified, it defaults to -1 (sorting over the last axis).
    
            Returns:
                array: The sorted array.
          
    """
def split(*args, **kwargs):
    """
    
            split(a: array, /, indices_or_sections: Union[int, List[int]], axis: int = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
            Split an array along a given axis.
    
            Args:
                a (array): Input array.
                indices_or_sections (int or list(int)): If ``indices_or_sections``
                  is an integer the array is split into that many sections of equal
                  size. An error is raised if this is not possible. If ``indices_or_sections``
                  is a list, the list contains the indices of the start of each subarray
                  along the given axis.
                axis (int, optional): Axis to split along, defaults to `0`.
    
            Returns:
                list(array): A list of split arrays.
          
    """
def sqrt(*args, **kwargs):
    """
    
            sqrt(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise square root.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The square root of ``a``.
          
    """
def square(*args, **kwargs):
    """
    
            square(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise square.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The square of ``a``.
          
    """
def squeeze(*args, **kwargs):
    """
    
            squeeze(a: array, /, axis: Union[None, int, List[int]] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            Remove length one axes from an array.
    
            Args:
                a (array): Input array.
                axis (int or tuple(int), optional): Axes to remove. Defaults
                to ``None`` in which case all size one axes are removed.
    
            Returns:
                array: The output array with size one axes removed.
          
    """
def stack(*args, **kwargs):
    """
    
          stack(arrays: List[array], axis: Optional[int] = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
          Stacks the arrays along a new axis.
    
          Args:
              arrays (list(array)): A list of arrays to stack.
              axis (int, optional): The axis in the result array along which the
                input arrays are stacked. Defaults to ``0``.
              stream (Stream, optional): Stream or device. Defaults to ``None``.
    
          Returns:
              array: The resulting stacked array.
        
    """
def stop_gradient(*args, **kwargs):
    """
    
            stop_gradient(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Stop gradients from being computed.
    
            The operation is the identity but it prevents gradients from flowing
            through the array.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The unchanged input ``a`` but without gradient flowing
                  through it.
          
    """
def subtract(*args, **kwargs):
    """
    
            subtract(a: Union[scalar, array], b: Union[scalar, array], stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise subtraction.
    
            Subtract one array from another with numpy-style broadcasting semantics. Either or both
            input arrays can also be scalars.
    
            Args:
                a (array): Input array or scalar.
                b (array): Input array or scalar.
    
            Returns:
                array: The difference ``a - b``.
          
    """
def sum(*args, **kwargs):
    """
    
            sum(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, *, stream: Union[None, Stream, Device] = None) -> array
    
            Sum reduce the array over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
    
            Returns:
                array: The output array with the corresponding axes reduced.
          
    """
def swapaxes(*args, **kwargs):
    """
    
            swapaxes(a: array, /, axis1 : int, axis2: int, *, stream: Union[None, Stream, Device] = None) -> array
    
            Swap two axes of an array.
    
            Args:
                a (array): Input array.
                axis1 (int): Specifies the first axis.
                axis2 (int): Specifies the second axis.
    
            Returns:
                array: The array with swapped axes.
          
    """
def take(*args, **kwargs):
    """
    
            take(a: array, /, indices: array, axis: Optional[int] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            Take elements along an axis.
    
            The elements are taken from ``indices`` along the specified axis.
            If the axis is not specified the array is treated as a flattened
            1-D array prior to performing the take.
    
            As an example, if the ``axis=1`` this is equivalent to ``a[:, indices, ...]``.
    
            Args:
                a (array): Input array.
                indices (array): Input array with integral type.
                axis (int, optional): Axis along which to perform the take. If unspecified
                  the array is treated as a flattened 1-D vector.
    
            Returns:
                array: The indexed values of ``a``.
          
    """
def take_along_axis(*args, **kwargs):
    """
    
            take_along_axis(a: array, /, indices: array, axis: Optional[int] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            Take values along an axis at the specified indices.
    
            Args:
                a (array): Input array.
                indices (array): Indices array. These should be broadcastable with
                  the input array excluding the `axis` dimension.
                axis (int or None): Axis in the input to take the values from. If
                  ``axis == None`` the array is flattened to 1D prior to the indexing
                  operation.
    
            Returns:
                array: The output array with the specified shape and values.
          
    """
def tan(*args, **kwargs):
    """
    
            tan(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise tangent.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The tangent of ``a``.
          
    """
def tanh(*args, **kwargs):
    """
    
            tanh(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Element-wise hyperbolic tangent.
    
            Args:
                a (array): Input array.
    
            Returns:
                array: The hyperbolic tangent of ``a``.
          
    """
def tensordot(*args, **kwargs):
    """
    
            tensordot(a: array, b: array, /, axes: Union[int, List[List[int]]] = 2, *, stream: Union[None, Stream, Device] = None) -> array
    
            Compute the tensor dot product along the specified axes.
    
            Args:
              a (array): Input array
              b (array): Input array
              axes (int or list(list(int)), optional): The number of dimensions to
                sum over. If an integer is provided, then sum over the last
                ``axes`` dimensions of ``a`` and the first ``axes`` dimensions of
                ``b``. If a list of lists is provided, then sum over the
                corresponding dimensions of ``a`` and ``b``. (default: 2)
    
            Returns:
              result (array): The tensor dot product.
          
    """
def tile(*args, **kwargs):
    """
    
          tile(a: array, reps: Union[int, List[int]], /, *, stream: Union[None, Stream, Device] = None) -> array
    
          Construct an array by repeating ``a`` the number of times given by ``reps``.
    
          Args:
            a (array): Input array
            reps (int or list(int)): The number of times to repeat ``a`` along each axis.
    
          Returns:
            result (array): The tiled array.
        
    """
def topk(*args, **kwargs):
    """
    
            topk(a: array, /, k: int, axis: Union[None, int] = -1, *, stream: Union[None, Stream, Device] = None) -> array
    
            Returns the ``k`` largest elements from the input along a given axis.
    
            The elements will not necessarily be in sorted order.
    
            Args:
                a (array): Input array.
                k (int): ``k`` top elements to be returned
                axis (int or None, optional): Optional axis to select over.
                  If ``None``, this selects the top ``k`` elements over the
                  flattened array. If unspecified, it defaults to ``-1``.
    
            Returns:
                array: The top ``k`` elements from the input.
          
    """
def transpose(*args, **kwargs):
    """
    
            transpose(a: array, /, axes: Optional[List[int]] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            Transpose the dimensions of the array.
    
            Args:
                a (array): Input array.
                axes (list(int), optional): Specifies the source axis for each axis
                  in the new array. The default is to reverse the axes.
    
            Returns:
                array: The transposed array.
          
    """
def tri(*args, **kwargs):
    """
    
            tri(n: int, m: int, k: int, dtype: Optional[Dtype] = None, *, stream: Union[None, Stream, Device] = None) -> array
    
            An array with ones at and below the given diagonal and zeros elsewhere.
    
            Args:
              n (int): The number of rows in the output.
              m (int, optional): The number of cols in the output. Defaults to ``None``.
              k (int, optional): The diagonal of the 2-D array. Defaults to ``0``.
              dtype (Dtype, optional): Data type of the output array. Defaults to ``float32``.
              stream (Stream, optional): Stream or device. Defaults to ``None``.
    
            Returns:
              array: Array with its lower triangle filled with ones and zeros elsewhere
          
    """
def tril(*args, **kwargs):
    """
    
          tril(x: array, k: int, *, stream: Union[None, Stream, Device] = None) -> array
    
            Zeros the array above the given diagonal.
    
            Args:
              x (array): input array.
              k (int, optional): The diagonal of the 2-D array. Defaults to ``0``.
              stream (Stream, optional): Stream or device. Defaults to ``None``.
    
            Returns:
              array: Array zeroed above the given diagonal
        
    """
def triu(*args, **kwargs):
    """
    
          triu(x: array, k: int, *, stream: Union[None, Stream, Device] = None) -> array
    
            Zeros the array below the given diagonal.
    
            Args:
              x (array): input array.
              k (int, optional): The diagonal of the 2-D array. Defaults to ``0``.
              stream (Stream, optional): Stream or device. Defaults to ``None``.
    
            Returns:
              array: Array zeroed below the given diagonal
        
    """
def value_and_grad(*args, **kwargs):
    """
    
            value_and_grad(fun: function, argnums: Optional[Union[int, List[int]]] = None, argnames: Union[str, List[str]] = []) -> function
    
            Returns a function which computes the value and gradient of ``fun``.
    
            The function passed to :func:`value_and_grad` should return either
            a scalar loss or a tuple in which the first element is a scalar
            loss and the remaining elements can be anything.
    
            .. code-block:: python
    
                import mlx.core as mx
    
                def mse(params, inputs, targets):
                    outputs = forward(params, inputs)
                    lvalue = (outputs - targets).square().mean()
                    return lvalue
    
                # Returns lvalue, dlvalue/dparams
                lvalue, grads = mx.value_and_grad(mse)(params, inputs, targets)
    
                def lasso(params, inputs, targets, a=1.0, b=1.0):
                    outputs = forward(params, inputs)
                    mse = (outputs - targets).square().mean()
                    l1 = mx.abs(outputs - targets).mean()
    
                    loss = a*mse + b*l1
    
                    return loss, mse, l1
    
                (loss, mse, l1), grads = mx.value_and_grad(lasso)(params, inputs, targets)
    
            Args:
                fun (function): A function which takes a variable number of
                  :class:`array` or trees of :class:`array` and returns
                  a scalar output :class:`array` or a tuple the first element
                  of which should be a scalar :class:`array`.
                argnums (int or list(int), optional): Specify the index (or indices)
                  of the positional arguments of ``fun`` to compute the gradient
                  with respect to. If neither ``argnums`` nor ``argnames`` are
                  provided ``argnums`` defaults to ``0`` indicating ``fun``'s first
                  argument.
                argnames (str or list(str), optional): Specify keyword arguments of
                  ``fun`` to compute gradients with respect to. It defaults to [] so
                  no gradients for keyword arguments by default.
    
            Returns:
                function: A function which returns a tuple where the first element
                is the output of `fun` and the second element is the gradients w.r.t.
                the loss.
          
    """
def var(*args, **kwargs):
    """
    
            var(a: array, /, axis: Union[None, int, List[int]] = None, keepdims: bool = False, ddof: int = 0, *, stream: Union[None, Stream, Device] = None) -> array
    
            Compute the variance(s) over the given axes.
    
            Args:
                a (array): Input array.
                axis (int or list(int), optional): Optional axis or
                  axes to reduce over. If unspecified this defaults
                  to reducing over the entire array.
                keepdims (bool, optional): Keep reduced axes as
                  singleton dimensions, defaults to `False`.
                ddof (int, optional): The divisor to compute the variance
                  is ``N - ddof``, defaults to 0.
    
            Returns:
                array: The output array of variances.
          
    """
def vjp(*args, **kwargs):
    """
    
            vjp(fun: function, primals: List[array], cotangents: List[array]) -> Tuple[List[array], List[array]]
    
            Compute the vector-Jacobian product.
    
            Computes the product of the ``cotangents`` with the Jacobian of a
            function ``fun`` evaluated at ``primals``.
    
            Args:
              fun (function): A function which takes a variable number of :class:`array`
                and returns a single :class:`array` or list of :class:`array`.
              primals (list(array)): A list of :class:`array` at which to
                evaluate the Jacobian.
              cotangents (list(array)): A list of :class:`array` which are the
                "vector" in the vector-Jacobian product. The ``cotangents`` should be the
                same in number, shape, and type as the outputs of ``fun``.
    
            Returns:
                list(array): A list of the vector-Jacobian products which
                is the same in number, shape, and type of the outputs of ``fun``.
          
    """
def vmap(*args, **kwargs):
    """
    
            vmap(fun: function, in_axes: object = 0, out_axes: object = 0) -> function
    
            Returns a vectorized version of ``fun``.
    
            Args:
                fun (function): A function which takes a variable number of
                  :class:`array` or a tree of :class:`array` and returns
                  a variable number of :class:`array` or a tree of :class:`array`.
                in_axes (int, optional): An integer or a valid prefix tree of the
                  inputs to ``fun`` where each node specifies the vmapped axis. If
                  the value is ``None`` then the corresponding input(s) are not vmapped.
                  Defaults to ``0``.
                out_axes (int, optional): An integer or a valid prefix tree of the
                  outputs of ``fun`` where each node specifies the vmapped axis. If
                  the value is ``None`` then the corresponding outputs(s) are not vmapped.
                  Defaults to ``0``.
    
            Returns:
                function: The vectorized function.
          
    """
def where(*args, **kwargs):
    """
    
            where(condition: Union[scalar, array], x: Union[scalar, array], y: Union[scalar, array], /, *, stream: Union[None, Stream, Device] = None) -> array
    
            Select from ``x`` or ``y`` according to ``condition``.
    
            The condition and input arrays must be the same shape or broadcastable
            with each another.
    
            Args:
              condition (array): The condition array.
              x (array): The input selected from where condition is ``True``.
              y (array): The input selected from where condition is ``False``.
    
            Returns:
                result (array): The output containing elements selected from ``x`` and ``y``.
          
    """
def zeros(*args, **kwargs):
    """
    
            zeros(shape: Union[int, List[int]], dtype: Optional[Dtype] = float32, *, stream: Union[None, Stream, Device] = None) -> array
    
            Construct an array of zeros.
    
            Args:
                shape (int or list(int)): The shape of the output array.
                dtype (Dtype, optional): Data type of the output array. If
                  unspecified the output type defaults to ``float32``.
    
            Returns:
                array: The array of zeros with the specified shape.
          
    """
def zeros_like(*args, **kwargs):
    """
    
            zeros_like(a: array, /, *, stream: Union[None, Stream, Device] = None) -> array
    
            An array of zeros like the input.
    
            Args:
                a (array): The input to take the shape and type from.
    
            Returns:
                array: The output array filled with zeros.
          
    """
Inf: float  # value = inf
Infinity: float  # value = inf
NAN: float  # value = nan
NINF: float  # value = -inf
NZERO: float = -0.0
NaN: float  # value = nan
PINF: float  # value = inf
PZERO: float = 0.0
__version__: str = '0.2.0.dev20240208'
bfloat16: Dtype  # value = mlx.core.bfloat16
bool_: Dtype  # value = mlx.core.bool
complex64: Dtype  # value = mlx.core.complex64
cpu: DeviceType  # value = <DeviceType.cpu: 0>
e: float = 2.718281828459045
euler_gamma: float = 0.5772156649015329
float16: Dtype  # value = mlx.core.float16
float32: Dtype  # value = mlx.core.float32
gpu: DeviceType  # value = <DeviceType.gpu: 1>
inf: float  # value = inf
infty: float  # value = inf
int16: Dtype  # value = mlx.core.int16
int32: Dtype  # value = mlx.core.int32
int64: Dtype  # value = mlx.core.int64
int8: Dtype  # value = mlx.core.int8
nan: float  # value = nan
newaxis = None
pi: float = 3.141592653589793
uint16: Dtype  # value = mlx.core.uint16
uint32: Dtype  # value = mlx.core.uint32
uint64: Dtype  # value = mlx.core.uint64
uint8: Dtype  # value = mlx.core.uint8
