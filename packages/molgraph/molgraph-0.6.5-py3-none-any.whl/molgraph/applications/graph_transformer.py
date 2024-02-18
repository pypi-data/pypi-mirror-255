import tensorflow as tf

import keras
from keras import initializers
from keras import regularizers
from keras import constraints

from typing import Optional
from typing import Union
from typing import Callable

from molgraph.tensors.graph_tensor import GraphTensor
from molgraph.tensors.graph_tensor import GraphTensorSpec

from molgraph import chemistry

from molgraph.layers.attentional.gt_conv import GTConv
from molgraph.layers.positional_encoding.laplacian import (
    LaplacianPositionalEncoding)


COMMON_KWARGS = {
    'positional_encoding_dim': 16,
    'merge_mode': 'concat',
    'self_projection': True,
    'normalization': True,
    'residual': True,
    'dropout': 0.15,
    'activation': 'relu',  
    'use_bias': True,
    'kernel_initializer': None,
    'bias_initializer': None,
    'kernel_regularizer': None,
    'bias_regularizer': None,
    'activity_regularizer': None,
    'kernel_constraint': None,
    'bias_constraint': None,
}

CONDITIONAL_KWARGS = {
    'LARGE': {
        'steps': 8,
        'units': 1024,
        'heads': 16,
    },
    'MEDIUM': {
        'steps': 6,
        'units': 256,
        'heads': 8,
    },
    'SMALL': {
        'steps': 4,
        'units': 64,
        'heads': 4,    
    }
}


molecule_encoder = chemistry.MolecularGraphEncoder(
    atom_encoder=chemistry.Tokenizer([

    ]),
    bond_encoder=chemistry.Tokenizer([

    ]),
    positional_encoding_dim=16,
)

# molecule_encoder.to_spec()

def GraphTransformer(
    mode: str,
):
    pass




class GraphTransformer(keras.Model):

    '''Graph transformer model.

    Implementation is based on Dwivedi et al. (2021) [#]_.

    Args:
        steps (int):
            Number of graph transformer conv layers. Default to 4.
        units (int, None):
            Number of output units.
        positional_encoding_dim (int):
            The dimension of the Laplacian positional encoding. Default to 16.
        use_edge_features (bool):
            Whether or not to use edge features. Default to True.
        num_heads (int):
            Number of attention heads. Default to 8.
        merge_mode (str):
            The strategy for merging the heads. Either of 'concat', 'sum',
            'mean' or None. If set to None, 'mean' is used. Default to 'concat'.
        self_projection (bool):
            Whether to apply self projection. Default to True.
        normalization (str, None):
            The type of normalization to use for the output. Either of
            'batch_norm', 'layer_norm' or None. Default to 'layer_norm'.
        residual: (bool)
            Whether to add skip connection to the output. Default to True.
        dropout: (float, None):
            Dropout applied to the output of the layer. Default to None.
        attention_activation (tf.keras.activations.Activation, callable, str, None):
            Activation function applied to the the attention scores. Default to None.
        activation (tf.keras.activations.Activation, callable, str, None):
            Activation function applied to the output of the layer. Default to 'relu'.
        use_bias (bool):
            Whether the layer should use biases. Default to True.
        kernel_initializer (tf.keras.initializers.Initializer, str):
            Initializer function for the kernels. Default to
            tf.keras.initializers.TruncatedNormal(stddev=0.005).
        bias_initializer (tf.keras.initializers.Initializer, str):
            Initializer function for the biases. Default to
            tf.keras.initializers.Constant(0.).
        kernel_regularizer (tf.keras.regularizers.Regularizer, None):
            Regularizer function applied to the kernels. Default to None.
        bias_regularizer (tf.keras.regularizers.Regularizer, None):
            Regularizer function applied to the biases. Default to None.
        activity_regularizer (tf.keras.regularizers.Regularizer, None):
            Regularizer function applied to the final output of the layer.
            Default to None.
        kernel_constraint (tf.keras.constraints.Constraint, None):
            Constraint function applied to the kernels. Default to None.
        bias_constraint (tf.keras.constraints.Constraint, None):
            Constraint function applied to the biases. Default to None.

    References:
        .. [#] https://arxiv.org/pdf/2012.09699.pdf
    '''

    def __init__(
        self,
        steps: int = 4,
        units: Optional[int] = 128,
        positional_encoding_dim: int = 16,
        use_edge_features: bool = True,
        num_heads: int = 8,
        merge_mode: Optional[str] = 'concat',
        self_projection: bool = True,
        normalization: Union[None, bool, str] = 'layer_norm',
        residual: bool = True,
        dropout: Optional[float] = None,
        activation: Union[None, str, Callable[[tf.Tensor], tf.Tensor]] = 'relu',
        use_bias: bool = True,
        kernel_initializer: Union[str, initializers.Initializer, None] = None,
        bias_initializer: Union[str, initializers.Initializer, None] = None,
        kernel_regularizer: Optional[regularizers.Regularizer] = None,
        bias_regularizer: Optional[regularizers.Regularizer] = None,
        activity_regularizer: Optional[regularizers.Regularizer] = None,
        kernel_constraint: Optional[constraints.Constraint] = None,
        bias_constraint: Optional[constraints.Constraint] = None,
        name: Optional[str] = 'GraphTransformer',
        **kwargs
    ):
        super().__init__(name=name, **kwargs)

        self.gt_conv_kwargs = dict(
            units=units,
            use_edge_features=use_edge_features,
            num_heads=num_heads,
            merge_mode=merge_mode,
            self_projection=self_projection,
            normalization=normalization,
            residual=residual,
            dropout=dropout,
            activation=activation,  
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
        )

        self.steps = steps
        self.positional_encoding_dim = positional_encoding_dim
        self.positional_encoding = LaplacianPositionalEncoding(
            dim=self.positional_encoding_dim,
            activation=None,
            use_bias=None,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
        )
        self.graph_transformer_layers = [
            GTConv(**self.gt_conv_kwargs) for _ in range(steps)]

    def call(self, tensor: GraphTensor) -> GraphTensor:
        tensor = self.positional_encoding(tensor)
        for gt_conv in self.graph_transformer_layers:
            tensor = gt_conv(tensor)
        return tensor
    
    def get_config(self) -> dict:
        config = super().get_config()
        config.update({
            'steps': self.steps,
            'positional_encoding_dim': self.positional_encoding_dim,
            'gt_conv_kwargs': self.gt_conv_kwargs,
        })
        return config
    
    @classmethod
    def from_config(cls, config: dict) -> 'GraphTransformer':
        # Unpack gt_conv_kwargs
        gt_conv_kwargs = config.pop('gt_conv_kwargs')
        config.update(gt_conv_kwargs)
        return cls(**config)
