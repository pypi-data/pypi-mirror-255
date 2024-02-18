"""
Copyright Wenyi Tang 2024

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

:Author: Jianjin Liao
:Email: jianjin.liao@intel.com
"""

# pylint: disable=arguments-differ

from typing import List

import numpy as np
from onnx import mapping, numpy_helper
from onnx.helper import make_node
from onnx.onnx_pb import NodeProto

from onnx2onnx.graph import OnnxGraph

from . import PASSES
from .pattern import GraphPattern, SingleNodePattern
from .rewriter import Rewriter
from .utils import make_constant


@PASSES.register(name="split_to_slice")
class SplitToSliceRewriter(Rewriter):
    """Change Split node to Slice node."""

    def __init__(self):
        super().__init__(SingleNodePattern("Split"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        node_pb = nodes[0]
        node = node_pb.name
        split = self.get_value(self.get_input_node(node_pb, 1))
        axis = self.get_attribute(node_pb, "axis") or 0
        starts = 0
        for i, (ch, _) in enumerate(zip(split, graph.onnx_successors(node_pb))):
            starts_node = make_constant(
                name=f"{node}/Starts{i}", value=np.array([starts], dtype="int64")
            )
            ends_node = make_constant(
                name=f"{node}/Ends{i}", value=np.array([starts + ch], dtype="int64")
            )
            axes_node = make_constant(
                name=f"{node}/Axes{i}", value=np.array([axis], dtype="int64")
            )
            slice_node = make_node(
                op_type="Slice",
                inputs=[
                    node_pb.input[0],
                    starts_node.output[0],
                    ends_node.output[0],
                    axes_node.output[0],
                ],
                outputs=[node_pb.output[i]],
                name=f"{node}/Slice{i}",
            )
            self += [starts_node, ends_node, axes_node, slice_node]
            starts += ch
        self -= node_pb


@PASSES.register(name="resize_move_size_to_scale")
class ResizeMoveSizeToScaleRewriter(Rewriter):
    """Move `size` input to `scale` input for Resize Op."""

    def __init__(self):
        super().__init__(SingleNodePattern("Resize"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        node_pb = nodes[0]
        node = node_pb.name
        _, roi, scales, sizes = self.get_input_nodes(node_pb)
        if sizes is None and scales is None:
            raise ValueError(
                f"Op '{node}' both scales and sizes are empty!"
                " Try fold_constant pass before this."
            )
        if scales is not None:
            return
        input_shape = graph.tensor_shape(node_pb.input[0])
        axes = self.get_attribute(node_pb, "axes") or range(len(input_shape))
        ct_mode = self.get_attribute(node_pb, "coordinate_transformation_mode")
        sizes_val = numpy_helper.to_array(sizes.attribute[0].t)
        if roi is not None and ct_mode == "tf_crop_and_resize":
            roi_val = self.get_value(roi).reshape([2, -1])
            roi_size = []
            for i, j, k in zip(roi_val[0], roi_val[1], sizes_val):
                if i < 0:
                    i += k
                if j < 0:
                    j += k
                assert j >= i >= 0
                roi_size.append(j - i)
            scales_val = [sizes_val[i] / roi_size[i] for i, _ in enumerate(axes)]
        else:
            scales_val = [sizes_val[i] / input_shape[j] for i, j in enumerate(axes)]
        scales = make_constant(
            f"{node}/const/scales", np.array(scales_val, dtype="float32")
        )
        node_pb.input[2] = scales.output[0]
        node_pb.input.pop()  # remove `sizes`
        self += scales
        self -= sizes


@PASSES.register(name="resize_to_nearest_neighbor")
class ResizeToNearestNeighborRewriter(Rewriter):
    """Simplify any resize with integer scales to nearest neighbor interpolate"""

    def __init__(self):
        super().__init__(SingleNodePattern("Resize"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        node_pb = nodes[0]
        mode = self.get_attribute(node_pb, "mode")
        if mode != "nearest":
            self.set_attribute(node_pb, "mode", "nearest")
        self._simplify_coordinate_transformation_mode(node_pb)

    def _simplify_coordinate_transformation_mode(self, node_pb):
        self.set_attribute(node_pb, "coordinate_transformation_mode", "asymmetric")


@PASSES.register(name="gemm_to_conv")
class GEMMToConvRewrite(Rewriter):
    """Convert GEMM op to Conv"""

    def __init__(self):
        super().__init__(SingleNodePattern("Gemm") | SingleNodePattern("MatMul"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        gemm_node = nodes[0]
        self._convert_fc_to_conv(graph, gemm_node)

    def _convert_fc_to_conv(self, graph: OnnxGraph, gemm_node: NodeProto):
        node = gemm_node.name

        data_shape = graph.tensor_shape(gemm_node.input[0])
        weight_shape = graph.tensor_shape(gemm_node.input[1])
        alpha = self.get_attribute(gemm_node, "alpha") or 1.0
        beta = self.get_attribute(gemm_node, "beta") or 1.0
        transA = self.get_attribute(gemm_node, "transA") or 0
        transB = self.get_attribute(gemm_node, "transB") or 0
        if len(data_shape) != 2 or len(weight_shape) != 2 or transA:
            return

        # data reshape
        data_shape_cst = make_constant(
            name=f"{node}/DataShape", value=np.array(data_shape + [1, 1], dtype="int64")
        )
        data_reshape_node = make_node(
            op_type="Reshape",
            inputs=[
                gemm_node.input[0],
                data_shape_cst.output[0],
            ],
            outputs=[f"{node}/Conv_input0"],
            name=f"{node}/DataReshape",
        )

        # weight reshape fold
        weight_node = self.get_input_node(gemm_node, 1)
        if weight_node.op_type == "Constant":
            # fold const
            weight_value = self.get_value(weight_node).copy()
            weight_value *= alpha
            if not transB:
                weight_value = weight_value.T
            new_weight_node = make_constant(
                name=f"{node}/Weight",
                value=weight_value[..., None, None],
            )
            self -= weight_node
            weight_port = new_weight_node.output[0]
        elif weight_node.op_type == "DequantizeLinear":
            quant_weight_node = self.get_input_node(weight_node, 0)
            quant_weight = self.get_value(quant_weight_node)
            if not transB:
                quant_weight = quant_weight.T
                # must quantize on output channels
                assert self.get_attribute(weight_node, "axis") == 1
                self.set_attribute(weight_node, "axis", 0)
            new_weight_node = make_constant(
                f"{node}/QWeight", quant_weight[..., None, None]
            )
            weight_node.input[0] = new_weight_node.output[0]
            weight_port = weight_node.output[0]
            self -= quant_weight_node
            if alpha != 1:
                # rescale with alpha
                scale_node = self.get_input_node(weight_node, 1)
                scale_value = self.get_value(scale_node).copy()
                scale_value *= alpha
                scale_const_node = make_constant(f"{node}/scale", scale_value)
                self -= scale_node
                self += scale_const_node
                weight_node.input[1] = scale_const_node.output[0]
        else:
            return

        conv_inputs = [data_reshape_node.output[0], weight_port]

        # bias
        if len(gemm_node.input) == 3:
            bias_node = self.get_input_node(gemm_node, 2)
            if bias_node.op_type == "Constant":
                bias_value = self.get_value(bias_node) * beta
                if bias_value.ndim > 1:
                    bias_value = bias_value.squeeze()
                bias_const_node = make_constant(f"{node}/bias", bias_value)
                self -= bias_node
                self += bias_const_node
                conv_inputs.append(bias_const_node.output[0])
            else:
                conv_inputs.append(gemm_node.input[2])

        # conv
        conv_node = make_node(
            op_type="Conv",
            inputs=conv_inputs,
            outputs=[f"{node}/Conv_out"],
            name=f"{node}/Conv",
        )
        self.set_attribute(conv_node, "dilations", [1, 1])
        self.set_attribute(conv_node, "group", 1)
        self.set_attribute(conv_node, "kernel_shape", [1, 1])
        self.set_attribute(conv_node, "pads", [0, 0, 0, 0])
        self.set_attribute(conv_node, "strides", [1, 1])

        # out reshape
        out_shape = graph.tensor_shape(gemm_node.output[0])
        out_shape_cst = make_constant(
            name=f"{node}/OutShape", value=np.array(out_shape, dtype="int64")
        )
        out_reshape_node = make_node(
            op_type="Reshape",
            inputs=[
                conv_node.output[0],
                out_shape_cst.output[0],
            ],
            outputs=gemm_node.output[:],
            name=f"{node}/OutReshape",
        )

        self += [
            data_shape_cst,
            data_reshape_node,
            new_weight_node,
            conv_node,
            out_shape_cst,
            out_reshape_node,
        ]
        self -= gemm_node


@PASSES.register(name="shape_to_constant")
class ShapeToConstantPass(Rewriter):
    """Convert static Shape op output to Constant."""

    def __init__(self):
        super().__init__(pattern=SingleNodePattern("Shape"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        node = nodes[0]
        try:
            shape = graph.tensor_shape(node.input[0])
            if not all(isinstance(i, int) for i in shape):
                return  # dynamic shape
        except ValueError:
            # shape is not constant
            return
        # replace Shape with Constant
        shape_const = make_constant(node.name + "/Reshape", np.array(shape, "int64"))
        shape_const.output[0] = node.output[0]
        self -= node
        self += shape_const


@PASSES.register(name="reshape_reorder")
class ReshapeReorderRewrite(Rewriter):
    """reorder Reshape after “DequantizeLinear” and eliminate duplicated reshape."""

    def __init__(self):
        pattern = GraphPattern()
        reshape1 = SingleNodePattern("Reshape")
        quantize = SingleNodePattern("QuantizeLinear")
        dequantize = SingleNodePattern("DequantizeLinear")

        pattern.add_edge(reshape1, quantize)
        pattern.add_edge(quantize, dequantize)

        super().__init__(pattern)

    def check(self, graph, reshape1_node, reshape2_node):
        """check shapes between reshape1 input tensor and reshape2 output tensor"""
        if reshape2_node is None or reshape2_node.op_type != "Reshape":
            return False

        # it maybe None if it's generated from other pass
        shape1 = graph.tensor_shape(reshape1_node.input[0])
        shape2 = self.get_value(self.get_input_node(reshape2_node, 1))
        if (
            shape1 is not None
            and len(shape1) == len(shape2)
            and np.all([i == j] for i, j in zip(shape1, shape2))
        ):
            return True
        return False

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        reshape1_node, quant_node, dequant_node = nodes
        # remove first reshape
        new_quant_node = make_node(
            op_type="QuantizeLinear",
            inputs=[reshape1_node.input[0]] + quant_node.input[1:],
            outputs=quant_node.output[:],
            name=quant_node.name + "_rr",
        )

        # eliminate duplicated reshape
        reshape2_node = self.get_output_node(dequant_node)
        if self.check(graph, reshape1_node, reshape2_node):
            new_dequant_node = make_node(
                op_type="DequantizeLinear",
                inputs=dequant_node.input[:],
                outputs=reshape2_node.output[:],
                name=dequant_node.name + "_rr",
            )
            self += [new_quant_node, new_dequant_node]
            self -= [reshape1_node, quant_node, dequant_node, reshape2_node]
            # remove shape constant
            self -= [
                self.get_input_node(reshape1_node, 1),
                self.get_input_node(reshape2_node, 1),
            ]
        else:
            new_dequant_node = make_node(
                op_type="DequantizeLinear",
                inputs=dequant_node.input[:],
                outputs=[dequant_node.output[0] + "_output"],
                name=dequant_node.name + "_rr",
            )
            new_rehsape_node = make_node(
                op_type="Reshape",
                inputs=[dequant_node.output[0] + "_output", reshape1_node.input[1]],
                outputs=[dequant_node.output[0]],
                name=reshape1_node.name + "_rr",
            )
            self += [new_quant_node, new_dequant_node, new_rehsape_node]
            self -= [reshape1_node, quant_node, dequant_node]


@PASSES.register(name="prelu_to_leaky")
class PReluToLeakyRewriter(Rewriter):
    """Convert PRelu whose parameter is a scaler to LeakyRelu."""

    def __init__(self):
        super().__init__(pattern=SingleNodePattern("PRelu"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto], *args, **kwargs):
        node = nodes[0]
        # quick check slope shape
        slope_shape = graph.tensor_shape(node.input[1])
        if len(slope_shape) >= 1 and slope_shape[0] != 1:
            # keep PRelu
            return

        slope_value = None
        for pred in graph.onnx_predecessors(node):
            if node.input[1] in pred.output:
                slope_value = self.get_value(pred)
                break
        if slope_value is None:
            # slope is not static
            return

        leakyrelu_node = make_node(
            "LeakyRelu",
            inputs=node.input[:1],
            outputs=node.output,
            name=node.name + "/to_leaky",
            alpha=float(slope_value),
        )
        self += leakyrelu_node
        self -= node


@PASSES.register(name="space2depth_to_conv")
class SpaceToDepthToConvRewriter(Rewriter):
    """Convert SpaceToDepth to Conv."""

    def __init__(self):
        super().__init__(pattern=SingleNodePattern("SpaceToDepth"))

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto], to_depthwise=False):
        s2d = nodes[0]
        blocksize = self.get_attribute(s2d, "blocksize")
        _, ic, _, _ = graph.tensor_shape(s2d.input[0])
        _, oc, _, _ = graph.tensor_shape(s2d.output[0])
        dtype = graph.tensor_type(s2d.input[0])
        assert ic * blocksize**2 == oc, "invalid space2depth parameters"

        assert not to_depthwise, "not implemented yet"
        if to_depthwise:
            kernel = np.tile(
                np.eye(blocksize**2)
                .reshape([-1, blocksize, blocksize])
                .astype(mapping.TENSOR_TYPE_MAP[dtype].np_dtype),
                [ic, 1, 1],
            )[:, None]
            # TODO: output channels need to be reordered
        else:
            kernel = (
                np.tile(
                    np.eye(blocksize**2)
                    .reshape([-1, blocksize, blocksize])
                    .astype(mapping.TENSOR_TYPE_MAP[dtype].np_dtype),
                    [ic, 1, 1, 1],
                )
                .transpose([1, 0, 2, 3])
                .reshape([oc, 1, blocksize, blocksize])
            )
            # expand to [oc, ic, blocksize, blocksize]
            kernel = np.concatenate(
                [kernel, np.tile(np.zeros_like(kernel), [1, ic - 1, 1, 1])], axis=1
            )
            for i in range(1, ic):
                kernel[i::ic][:, i] = kernel[i::ic][:, 0]
                kernel[i::ic][:, 0] = 0  # swap
        conv_weight = make_constant(name=f"{s2d.name}/weight", value=kernel)
        conv = make_node(
            op_type="Conv",
            inputs=list(s2d.input) + [conv_weight.output[0]],
            outputs=s2d.output,
            name=f"{s2d.name}/conv",
            kernel_shape=[blocksize, blocksize],
            strides=[blocksize, blocksize],
            group=ic if to_depthwise else 1,
        )
        self -= s2d
        self += [conv, conv_weight]


@PASSES.register(name="space2depth_to_qconv")
class SpaceToDepthToQConvRewriter(Rewriter):
    """Convert SpaceToDepth - QDQ to quantized Conv."""

    def __init__(self):
        qdq_pattern = GraphPattern()
        s2d = SingleNodePattern("SpaceToDepth")
        qpattern = SingleNodePattern("QuantizeLinear")
        dqpattern = SingleNodePattern("DequantizeLinear")
        qdq_pattern.add_edge(s2d, qpattern)
        qdq_pattern.add_edge(qpattern, dqpattern)
        super().__init__(pattern=qdq_pattern)

    def _copy_qdq(self, node: NodeProto) -> NodeProto:
        axis = self.get_attribute(node, "axis") or 0
        scale_node = self.get_input_node(node, 1)
        scale_value = self.get_value(scale_node)
        new_scale = make_constant(node.name + "/scale/copy", scale_value)
        input_names = [node.input[0] + "/copy", new_scale.output[0]]
        if len(node.input) == 3:
            zero_node = self.get_input_node(node, 2)
            zero_value = self.get_value(zero_node)
            new_zero = make_constant(node.name + "/zero/copy", zero_value)
            self += new_zero
            input_names += new_zero.output[:]
        new_node = make_node(
            node.op_type,
            input_names,
            [o + "/copy" for o in node.output],
            node.name + "/s2d_to_qconv/copy",
            axis=axis,
        )
        self += [new_scale]
        return new_node

    def rewrite(self, graph: OnnxGraph, nodes: List[NodeProto]):
        s2d, qnode, dqnode = nodes
        blocksize = self.get_attribute(s2d, "blocksize")
        _, ic, _, _ = graph.tensor_shape(s2d.input[0])
        _, oc, _, _ = graph.tensor_shape(s2d.output[0])
        etype = graph.tensor_type(dqnode.input[0])
        dtype = mapping.TENSOR_TYPE_MAP[etype].np_dtype
        assert ic * blocksize**2 == oc, "invalid space2depth parameters"

        qnode_ahead = self._copy_qdq(qnode)
        dqnode_ahead = self._copy_qdq(dqnode)
        qnode_ahead.input[0] = s2d.input[0]
        dqnode_ahead.input[0] = qnode_ahead.output[0]

        kernel = (
            # fmt: off
            np.tile(
                np.eye(blocksize**2)
                .reshape([-1, blocksize, blocksize])
                .astype(dtype),
                [ic, 1, 1, 1],
            )
            .transpose([1, 0, 2, 3])
            .reshape([oc, 1, blocksize, blocksize])
            # fmt: on
        )
        # expand to [oc, ic, blocksize, blocksize]
        kernel = np.concatenate(
            [kernel, np.tile(np.zeros_like(kernel), [1, ic - 1, 1, 1])], axis=1
        )
        for i in range(1, ic):
            kernel[i::ic][:, i] = kernel[i::ic][:, 0]
            kernel[i::ic][:, 0] = 0  # swap
        conv_weight = make_constant(name=f"{s2d.name}/weight", value=kernel)

        # kernel dequantize
        kernel_scale = make_constant(
            conv_weight.name + "/scale", np.ones([oc], np.float32)
        )
        kernel_zp = make_constant(conv_weight.name + "/zero", np.zeros([oc], dtype))
        kernel_dq = make_node(
            "DequantizeLinear",
            [conv_weight.output[0], kernel_scale.output[0], kernel_zp.output[0]],
            [conv_weight.output[0] + "/dq"],
            conv_weight.name + "/dequantize",
            axis=0,
        )

        conv = make_node(
            op_type="Conv",
            inputs=dqnode_ahead.output[:] + [kernel_dq.output[0]],
            outputs=s2d.output,
            name=f"{s2d.name}/conv",
            kernel_shape=[blocksize, blocksize],
            strides=[blocksize, blocksize],
        )
        self -= s2d
        self += [
            qnode_ahead,
            dqnode_ahead,
            kernel_dq,
            kernel_scale,
            kernel_zp,
            conv_weight,
            conv,
        ]
