import tensorflow as tf
from tensorflow.python.framework import composite_tensor
from tensorflow.python.framework import type_spec
from tensorflow.experimental import ExtensionType
from tensorflow.experimental import BatchableExtensionType
import collections
import numpy as np

from typing import Optional
from typing import Mapping
from typing import List
from typing import Tuple
from typing import Union
from typing import Any


_allowable_input_types = (
    tf.Tensor,
    tf.RaggedTensor,
    np.ndarray,
    list,
    tuple
)
_required_fields = ['edge_dst', 'edge_src', 'node_feature']

_non_updatable_fields = ['edge_dst', 'edge_src']

TensorLike = Union[
    tf.Tensor,
    tf.RaggedTensor,
    np.ndarray,
    list,
    tuple
]




class BaseGraphTensor(tf.experimental.BatchableExtensionType):
    'Base class for the graph tensors (GraphTensor and RaggedGraphTensor)'

    def update(
        self,
        new_data: Mapping[str, TensorLike],
    ) -> Union['GraphTensor', 'RaggedGraphTensor']:
        '''Updates existing data fields or adds new data fields.

        Constraints are put on the update method: new data needs to
        match the size of existing data (e.g., same number of nodes or edges).
        '''
        new_data = _convert_to_tensors(new_data, check_values=True)

        def convert_tensor(
            a: Union[tf.Tensor, tf.RaggedTensor],
            b: Union[tf.Tensor, tf.RaggedTensor]
        ) -> Union[tf.Tensor, tf.RaggedTensor]:
            if isinstance(a, tf.RaggedTensor) and isinstance(b, tf.Tensor):
                return a.flat_values
            elif isinstance(a, tf.Tensor) and isinstance(b, tf.RaggedTensor):
                return b.with_flat_values(a)
            else:
                return a

        data = dict(self.data) # data to be modified

        for k in list(new_data.keys()):

            if k == 'graph_indicator':
                continue # graph indicator not be added manually

            new_value = new_data.pop(k)

            _assert_compatible_size(
                new_value, data['node_feature'], data['edge_dst'])

            if k in data:
                data[k] = convert_tensor(new_value, data[k])
            elif _compatible_size(new_value, data['node_feature']):
                data[k] = convert_tensor(new_value, data['node_feature'])
            else:
                data[k] = convert_tensor(new_value, data['edge_dst'])

        return self.__class__(data)

    def remove(
        self,
        fields: Union[str, List[str]]
    ) -> Union['GraphTensor', 'RaggedGraphTensor']:
        'Removes data fields'
        data = dict(self.data) # data to be modified
        if isinstance(fields, str):
            fields = [fields]
        for field in fields:
            data.pop(field)
        return self.__class__(data)

    def __getattr__(self, name: str) -> Any:
        'Access different data fields as attributes ".name_of_attribute"'
        if name in object.__getattribute__(self, 'data'):
            return self.data[name]
        return object.__getattribute__(self, name)

    def __getitem__(
        self,
        index: Union[str, int, List[int]]
    ) -> Union[tf.RaggedTensor, tf.Tensor, 'GraphTensor', 'RaggedGraphTensor']:
        'Access data fields or subgraphs via indexing "[]"'
        if isinstance(index, str):
            return self.data[index]
        if isinstance(index, slice):
            index = _slice_to_tensor(
                index, _get_num_subgraphs(self))
        return tf.gather(self, index)

    def __iter__(self):
        'Allows graph tensor to be iterated'
        if not tf.executing_eagerly():
            raise ValueError(
                'Can only iterate over `GraphTensor` in eager mode.')
        limit = _get_num_subgraphs(self)
        return _Iterator(self, limit)

    def __repr__(self):
        fields = []
        for key, value in self.spec.data.items():
            if isinstance(self, RaggedGraphTensor):
                fields.append(
                    "{}=<tf.RaggedTensor: ".format(key) +
                    "shape={}, ".format(value.shape) +
                    "dtype={}, ".format(value.dtype.name) +
                    "ragged_rank={}, ".format(value.ragged_rank) +
                    "row_splits_dtype={}>".format(value.row_splits_dtype.name))
            elif isinstance(self, GraphTensor):
                fields.append(
                    "{}=<tf.Tensor: ".format(key) +
                    "shape={}, ".format(value.shape) +
                    "dtype={}>".format(value.dtype.name))
            else:
                fields.append("{}=<unknown>".format(key))
        return f"{self.__class__.__name__}({', '.join(fields)})"

    @property
    def shape(self) -> tf.TensorShape:
        'Partial shape of graph tensor (based on `node_feature`)'
        return self.spec.shape

    @property
    def dtype(self) -> tf.DType:
        'Partial dtype of graph tensor (based on `node_feature`)'
        return self.spec.dtype

    @property
    def rank(self) -> int:
        'Partial rank of graph tensor (based on `node_feature`)'
        return self.spec.rank

    @property
    def spec(self) -> Union['GraphTensor.Spec', 'RaggedGraphTensor.Spec']:
        'Spec of graph tensor'
        return self._type_spec

    @property
    def unspecific_spec(self) -> Union['GraphTensor.Spec', 'RaggedGraphTensor.Spec']:
        '''Unspecific spec of graph tensor.

        Specifically, the shape/size of the first dimension is set to None. This is
        necessary when loading and using saved models (as number of nodes and edges vary).
        '''
        def modify_spec(x):
            if isinstance(x, tf.RaggedTensorSpec):
                return tf.RaggedTensorSpec(
                    shape=tf.TensorShape([None]).concatenate(x.shape[1:]),
                    dtype=x.dtype,
                    row_splits_dtype=x.row_splits_dtype,
                    ragged_rank=x.ragged_rank,
                    flat_values_spec=x.flat_values_spec)
            return tf.TensorSpec(
                shape=tf.TensorShape([None]).concatenate(x.shape[1:]),
                dtype=x.dtype)

        return self.__class__.Spec(
            tf.nest.map_structure(modify_spec, self.spec.data))

def _create_object_from_type_and_dict(cls, obj_dict):
  """Creates an object, bypassing the constructor.
  Creates an object of type `cls`, whose `__dict__` is updated to contain
  `obj_dict`.
  Args:
    cls: The type of the new object.
    obj_dict: A `Mapping` that should be used to initialize the new object's
      `__dict__`.
  Returns:
    An object of type `cls`.
  """
  value = object.__new__(cls)
  value.__dict__.update(obj_dict)
  return value

def _batch(self, batch_size: Optional[None]) -> 'GraphTensorSpec':
    """BatchableExtensionType API"""
    batched_data_spec = tf.nest.map_structure(
        lambda spec: spec._batch(batch_size), self._data_spec)
    shape = tf.TensorShape([batch_size]).concatenate(self._shape)
    return self.__class__(batched_data_spec, shape, self._dtype)


class CustomBatchEncoder(tf.experimental.ExtensionTypeBatchEncoder):

    def batch(self, spec, batch_size):
        """Returns the TypeSpec representing a batch of values described by `spec`.
        The default definition returns a `TypeSpec` that is equal to `spec`, except
        that an outer axis with size `batch_size` is added to every nested
        `TypeSpec` and `TensorShape` field.  Subclasses may override this default
        definition, when necessary.
        Args:
          spec: The `TypeSpec` for an individual value.
          batch_size: An `int` indicating the number of values that are batched
            together, or `None` if the batch size is not known.
        Returns:
          A `TypeSpec` for a batch of values.
        """

        def batch_field(f):
          print(f)
          tf.print(f)
          if isinstance(f, type_spec.BatchableTypeSpec):
            return f.__batch_encoder__.batch(f, batch_size)
          elif isinstance(f, tf.TensorShape):
            print('foo')
            tf.print('foo')
            return [batch_size] + f
          else:
            return f

        fields = tuple(spec.__dict__.items())
        batched_fields = tf.nest.map_structure(batch_field, fields)
        return _create_object_from_type_and_dict(type(spec), batched_fields)

class RaggedGraphTensor(BaseGraphTensor):
    '''Ragged version of the graph tensor.

    The RaggedGraphTensor makes the graph tensor batchable, which is
    important for the Keras API (.fit, .predict) and tf.data.Dataset (.batch)
    '''

    # __name__ needs to be set for tf.SavedModel API to work properly
    __name__ = 'graph_tensor.RaggedGraphTensor'

    data: Mapping[str, tf.RaggedTensor]
    __batch_encoder__ = CustomBatchEncoder()

    def __init__(self, data, **data_kwargs):
        data.update(data_kwargs)
        self.data = _convert_to_tensors(
            data, check_values=True, check_keys=True)

    def merge(self):
        'Merges subgraphs into a single disjoint graph'

        data = dict(self.data) # data to be modified

        def to_tensor(tensor):
            return tensor.flat_values

        graph_indicator = data['node_feature'].value_rowids()

        increment = data['node_feature'].row_starts()
        indices = data['edge_dst'].value_rowids()
        increment = tf.cast(increment, dtype=data['edge_dst'].dtype)
        data = tf.nest.map_structure(to_tensor, data)
        # increment edges
        data['edge_dst'] += tf.gather(increment, indices)
        data['edge_src'] += tf.gather(increment, indices)

        data['graph_indicator'] = graph_indicator

        # return GraphTensor as we now have nested tensors
        return GraphTensor(data)

    class Spec:
        'Spec for RaggedGraphTensor'

        def with_shape(self, shape):
            return RaggedGraphTensor.Spec(self.data)

        @property
        def shape(self) -> tf.TensorShape:
            'Partial shape of Spec'
            return self.data['node_feature'].shape

        @property
        def dtype(self) -> tf.DType:
            'Partial dtype of Spec'
            return self.data['node_feature'].dtype

        @property
        def rank(self) -> int:
            'Partial rank of Spec'
            return self.shape.rank


class GraphTensor(BaseGraphTensor):

    '''Non-ragged version of the graph tensor.

    The GraphTensor makes graph neural networks (GNNs) more efficient, as
    they can now operate on one large (disjoint) graph. The GNN layers of
    MolGraph internally, temporarily, converts RaggedGraphTensor to GraphTensor
    when necessary.
    '''

    # __name__ needs to be set for tf.SavedModel API to work properly
    __name__ = 'graph_tensor.GraphTensor'

    data: Mapping[str, tf.Tensor]

    def __init__(self, data, **data_kwargs):
        data.update(data_kwargs)
        self.data = _convert_to_tensors(
            data, check_values=True, check_keys=True)


    def unmerge(self) -> 'GraphTensor':
        'Unmerges single (disjoint) graph into its components (subgraphs)'

        data = dict(self.data) # data to be modified

        graph_indicator = data.pop('graph_indicator')
        edge_dst = data.pop('edge_dst')
        edge_src = data.pop('edge_src')

        graph_indicator_edges = tf.gather(graph_indicator, edge_dst)

        num_subgraphs = _get_num_subgraphs(self)

        def to_ragged_tensor(
            tensor: Union[tf.Tensor, tf.RaggedTensor],
            num_subgraphs: tf.Tensor,
        ) -> tf.RaggedTensor:

            if isinstance(tensor, tf.RaggedTensor):
                return tensor

            if _compatible_size(tensor, graph_indicator):
                value_rowids = graph_indicator
            elif _compatible_size(tensor, graph_indicator_edges):
                value_rowids = graph_indicator_edges
            else:
                value_rowids = tf.zeros(
                    tf.shape(tensor)[0], dtype=graph_indicator.dtype)
                num_subgraphs = tf.constant(1, dtype=num_subgraphs.dtype)

            return tf.RaggedTensor.from_value_rowids(
                tensor, value_rowids, num_subgraphs)

        # decrement edges
        data = tf.nest.map_structure(
            lambda x: to_ragged_tensor(x, num_subgraphs), data)
        decrement = tf.gather(
            data['node_feature'].row_starts(), graph_indicator_edges)
        decrement = tf.cast(decrement, dtype=edge_dst.dtype)
        data['edge_dst'] = tf.RaggedTensor.from_value_rowids(
            edge_dst - decrement, graph_indicator_edges, num_subgraphs)
        data['edge_src'] = tf.RaggedTensor.from_value_rowids(
            edge_src - decrement, graph_indicator_edges, num_subgraphs)

        return RaggedGraphTensor(data)

    class Spec:

        'Spec for GraphTensor'

        def with_shape(self, shape):
            return GraphTensor.Spec(self.data)

        @property
        def shape(self) -> tf.TensorShape:
            'Partial shape of Spec'
            return self.data['node_feature'].shape

        @property
        def dtype(self) -> tf.DType:
            'Partial dtype of Spec'
            return self.data['node_feature'].dtype

        @property
        def rank(self) -> int:
            'Partial rank of Spec'
            return self.shape.rank


def _get_num_subgraphs(x: GraphTensor) -> tf.Tensor:
    'Get number of subgraphs of graph `x`'
    if 'graph_indicator' in x.data:
        return tf.math.reduce_max(x.data['graph_indicator']) + 1
    return x.data['node_feature'].nrows()

def _compatible_size(
    a: Union[tf.Tensor, tf.RaggedTensor],
    b: Union[tf.Tensor, tf.RaggedTensor],
) -> bool:
    'Checks if `a` and `b` have the same number of nodes or edges'

    def _get_size(x):
        'Get number of nodes or edges'
        if isinstance(x, tf.RaggedTensor):
            x = x.flat_values
        return tf.shape(x)[0]
    return _get_size(a) == _get_size(b)

def _assert_compatible_size(target, *comparators):
    return tf.Assert(
        tf.math.reduce_any(
            tf.nest.map_structure(
                lambda comparator: _compatible_size(target, comparator),
                comparators
            )
        ), [
            'At least one of the added fields does not match ' +
            'the size of existing fields. Namely, one of the ' +
            'added fields did not have the same numeber of ' +
            'nodes or edges as the existig fields'
        ]
    )

def _convert_to_tensors(
    data: Mapping[str, TensorLike],
    check_values: bool = False,
    check_keys: bool = False,
) -> Mapping[str, Union[tf.Tensor, tf.RaggedTensor]]:
    'Converts data values to tensors'

    # Make checks if so desired
    if check_values:
        _check_data_values(data)

    if check_keys:
        _check_data_keys(data)

    def _is_rectangular(x):
        'Checks if tensor is rectangular (non-ragged)'
        lengths = set()
        for xi in x:
            if not isinstance(xi, (np.ndarray, list, tuple)):
                lengths.add(0)
            else:
                lengths.add(len(xi))
        return len(lengths) == 1

    def maybe_convert(x):
        'Convert to tensor or ragged tensor if needed'
        if tf.is_tensor(x):
            return x
        if _is_rectangular(x):
            return tf.convert_to_tensor(x)
        return tf.ragged.constant(x)

    return {k: maybe_convert(v) for (k, v) in data.items()}

def _check_data_keys(data: Mapping[str, Any]):
    'Asserts that necessary fields exist in the graph (tensor)'
    return [
        tf.Assert(
            req_field in data, [f'`data` requires `{req_field}` field']
        )
        for req_field in _required_fields
    ]

def _check_data_values(data: Mapping[str, Any]):
    'Asserts that the values of the data fields are of correct type'
    return [
        tf.Assert(
            isinstance(v, _allowable_input_types),
            [
                f'Field `{k}` is needs to be a `tf.Tensor`, ' +
                '`tf.RaggedTensor`, `np.ndarray`, `list` or `tuple`'
            ]
        )
        for (k, v) in data.items()
    ]

def _slice_to_tensor(slice_obj: slice, limit: tf.Tensor) -> tf.Tensor:
    '''Converts slice to a tf.range,

    tf.range can subsequently be used with tf.gather to gather subgraphs.
    '''
    start = slice_obj.start
    stop = slice_obj.stop
    step = slice_obj.step

    if stop is None:
        stop = limit
    elif stop < 0:
        stop = tf.maximum(limit + stop, 0)

    if start is None:
        start = tf.constant(0)
    elif start < 0:
        start = tf.maximum(limit + start, 0)

    if step is None:
        step = 1
    elif step < 0:
        raise ValueError('Slice step cannot be negative')
    elif step == 0:
        raise ValueError('Slice step cannot be zero')

    start = tf.cond(start > stop, lambda: stop, lambda: start)

    return tf.range(start, stop, step)


class _Iterator:
    'Iterator for the graph tensors'

    __slots__ = ["_iterable", "_index", "_limit"]

    def __init__(self, iterable: GraphTensor, limit: int) -> None:
        self._iterable = iterable
        self._limit = limit
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index == self._limit:
            raise StopIteration
        result = self._iterable[self._index]
        self._index += 1
        return result


@tf.experimental.dispatch_for_api(tf.gather)
def tensor_graph_gather(
    params: Union[GraphTensor, RaggedGraphTensor],
    indices,
    validate_indices=None,
    axis=None,
    batch_dims=0,
    name=None
) -> GraphTensor:
    'Gathers components (subgraphs) from graph.'

    if axis is not None and axis != 0:
        raise ValueError(
            f'axis=0 is required for `{params.__class__.__name__}`.')

    ragged = isinstance(params, RaggedGraphTensor)

    if not ragged:
        params = params.unmerge()


    data = tf.nest.map_structure(
        lambda x: tf.gather(
            x, indices, validate_indices, axis, batch_dims, name),
        params.data)

    data = dict(data)

    if isinstance(data['node_feature'], tf.Tensor):
        params = GraphTensor(data)
    else:
        params = RaggedGraphTensor(data)
        if not ragged:
            params = params.merge()

    return params

@tf.experimental.dispatch_for_api(tf.concat)
def tensor_graph_concat(
    values: List[Union[GraphTensor, RaggedGraphTensor]],
    axis=0,
    name='concat'
) -> Union[GraphTensor, RaggedGraphTensor]:
    'Concatenates list of graph tensors into a single graph tensor.'

    if axis is not None and axis != 0:
        raise ValueError(
            f'axis=0 is required for `{values[0].__class__.__name__}`s.')

    def get_row_lengths(x, dtype):
        if hasattr(x, 'row_lengths'):
            return tf.cast(x.row_lengths(), dtype=dtype)
        return tf.cast(x.shape[:1], dtype=dtype)

    def from_row_lengths(x, num_nodes, num_edges, dtype):
        return tf.cond(
            tf.shape(x, dtype)[0] == tf.reduce_sum(num_nodes),
            lambda: tf.RaggedTensor.from_row_lengths(x, num_nodes),
            lambda: tf.cond(
                tf.shape(x, dtype)[0] == tf.reduce_sum(num_edges),
                lambda: tf.RaggedTensor.from_row_lengths(x, num_edges),
                lambda: tf.RaggedTensor.from_row_lengths(x, tf.shape(x)[:1])
            )
        )

    structure = values[0].data

    ragged = tf.nest.map_structure(
        lambda x: isinstance(x, RaggedGraphTensor), values)

    if 0 < sum(ragged) < len(ragged):
        raise ValueError(
            'The nested structure types of `values` are not the same. ' +
            'Found both `RaggedGraphTensor`s and `GraphTensor`s.')
    else:
        # If first element is ragged, the rest is also ragged, and vice versa
        ragged = ragged[0]

    flat_sequence = tf.nest.map_structure(
        lambda x: tf.nest.flatten(x, expand_composites=True), values)

    dtype = structure['edge_dst'].dtype

    num_nodes = tf.concat([
        get_row_lengths(x['node_feature'], dtype) for x in values], axis=0)

    num_edges = tf.concat([
        get_row_lengths(x['edge_dst'], dtype) for x in values], axis=0)

    if ragged:
        # Keep only values (resulting from tf.nest.flatten)
        flat_sequence = [f[::2] for f in flat_sequence]

    flat_sequence = list(zip(*flat_sequence))
    flat_sequence = [tf.concat(x, axis=0) for x in flat_sequence]
    values = tf.nest.pack_sequence_as(structure, flat_sequence)
    values = tf.nest.map_structure(
        lambda x: from_row_lengths(x, num_nodes, num_edges, dtype),
        values
    )
    values = dict(values)
    values = RaggedGraphTensor(values)

    if ragged:
        return values

    return values.merge()

@tf.experimental.dispatch_for_api(tf.matmul)
def tensor_graph_matmul(
    a: Union[GraphTensor, tf.Tensor],
    b: Union[GraphTensor, tf.Tensor],
    transpose_a=False,
    transpose_b=False,
    adjoint_a=False,
    adjoint_b=False,
    a_is_sparse=False,
    b_is_sparse=False,
    output_type=None
) -> tf.Tensor:
    '''Allows graph tensors to be matrix multiplied.

    Specifically, the `node_feature` field will be used for
    the matrix multiplication. This implementation makes it
    possible to pass graph tensors to `keras.layers.Dense`.
    '''

    if isinstance(a, (GraphTensor, RaggedGraphTensor)):
        a = a.node_feature
    if isinstance(b, (GraphTensor, RaggedGraphTensor)):
        b = b.node_feature
    return tf.matmul(
        a, b, transpose_a, transpose_b, adjoint_a,
        adjoint_b, a_is_sparse, b_is_sparse, output_type)

@tf.experimental.dispatch_for_unary_elementwise_apis(GraphTensor)
def tensor_graph_unary_elementwise_op_handler(
    api_func,
    x: GraphTensor
) -> Union[GraphTensor, RaggedGraphTensor]:
    '''Allows all unary elementwise operations (such as `tf.math.abs`)
    to handle graph tensors.
    '''
    return x.update({'node_feature': api_func(x.node_feature)})

@tf.experimental.dispatch_for_binary_elementwise_apis(
    Union[GraphTensor, tf.Tensor],
    Union[GraphTensor, tf.Tensor])
def tensor_graph_binary_elementwise_op_handler(
    api_func,
    x: Union[Any, GraphTensor, RaggedGraphTensor],
    y: Union[Any, GraphTensor, RaggedGraphTensor],
) -> Union[GraphTensor, RaggedGraphTensor]:
    '''Allows all binary elementwise operations (such as `tf.math.add`)
    to handle graph tensors.
    '''
    if isinstance(x, GraphTensor):
        x_values = x.node_feature
    else:
        x_values = x

    if isinstance(y, GraphTensor):
        y_values = y.node_feature
    else:
        y_values = y

    if isinstance(x, GraphTensor):
        return x.update({'node_feature': api_func(x_values, y_values)})
    elif isinstance(y, GraphTensor):
        return y.update({'node_feature': api_func(x_values, y_values)})

    return api_func(x_values, y_values)
