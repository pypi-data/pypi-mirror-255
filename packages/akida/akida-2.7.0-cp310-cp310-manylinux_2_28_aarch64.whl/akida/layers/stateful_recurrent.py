from akida.core import (Layer, LayerType, LayerParams)


class StatefulRecurrent(Layer):
    """This represents the Akida StatefulRecurrent layer.

    To store the previous state of the layer, this time dependent layer has an
    internal state variable that is updated at each run.
    This main layer operation is preceded by a matmul projection and followed by
    another matmul projection followed by a bias addition.
    The layer outputs the following computed value only if counter % subsample_ratio == 0.
    Otherwise it outputs a vector of zeros.

    The StatefulRecurrent layer operations can be described as follows:

        >>> inputs = inputs << in_proj_in_shift
        >>> in_proj = matmul(inputs, in_proj_kernel)
        >>> in_proj_outputs = in_proj * in_proj_out_scale >> in_proj_out_shift
        >>> stateful_inputs = in_proj_outputs << stateful_in_shift
        >>> internal_state = internal_state * A + matmul(stateful_inputs, B)
        >>> stateful_outputs = matmul(real(internal_state), C)
        >>> stateful_outputs = stateful_outputs >> stateful_out_shift
        >>> out_proj_inputs = stateful_outputs << out_proj_in_shift
        >>> out_proj = matmul(out_proj_inputs, out_proj_kernel)
        >>> out_proj = out_proj + bias
        >>> out_proj_output = out_proj * output_scale >> output_shift
        >>> output = ReLU(out_proj_output) (optional)


    Note that A is noted as complex but its related operations are splited. Real part
    in one side, imaginary on the other.
    Note also that output values will be saturated on the range that can be represented
    with output_bits.

    Args:
        num_coeffs (int): number of embedding coefficients.
        repeat (int): number of times to repeat the embedding coefficients. The total
            hidden dimension (the internal state units) is given simply by num_coeffs x repeat.
        subsample_ratio (int): subsampling ratio that defines rate at which outputs are
            produced (zero otherwise).
        out_channels (int): number of output channels.
        activation (bool, optional): enable or disable activation function.
            Defaults to True.
        output_bits (int, optional): output bitwidth. Defaults to 8.
        dense_buffer_bits (int, optional): dense projections buffer bitwidth. Defaults to 32.
        buffer_bits (int, optional): buffer bitwidth. Defaults to 32.
        post_op_buffer_bits (int, optional): internal bitwidth for post operations. Defaults to 32.
        name (str, optional): name of the layer. Defaults to empty string.

    """

    def __init__(self,
                 num_coeffs,
                 repeat,
                 subsample_ratio,
                 out_channels,
                 activation=True,
                 output_bits=8,
                 dense_buffer_bits=32,
                 buffer_bits=32,
                 post_op_buffer_bits=32,
                 name=""):
        try:
            params = LayerParams(
                LayerType.StatefulRecurrent, {
                    "num_coeffs": num_coeffs,
                    "repeat": repeat,
                    "subsample_ratio": subsample_ratio,
                    "out_channels": out_channels,
                    "activation": activation,
                    "output_bits": output_bits,
                    "dense_buffer_bits": dense_buffer_bits,
                    "buffer_bits": buffer_bits,
                    "post_op_buffer_bits": post_op_buffer_bits,
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
