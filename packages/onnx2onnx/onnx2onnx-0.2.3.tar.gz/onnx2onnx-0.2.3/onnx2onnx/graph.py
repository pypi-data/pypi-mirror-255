"""
Copyright Wenyi Tang 2023

:Author: Wenyi Tang
:Email: wenyitang@outlook.com

"""

import os
import warnings
from copy import deepcopy
from itertools import chain
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
from uuid import uuid4

import networkx as nx
import onnx
from onnx.helper import make_graph, make_model, make_tensor_type_proto, make_value_info


class OnnxGraph(nx.DiGraph):
    """Create a DAG from onnx graph."""

    def __init__(self, model: Optional[onnx.ModelProto] = None) -> None:
        if model is None:
            super().__init__()
        else:
            assert isinstance(model, onnx.ModelProto)
            super().__init__(name=model.graph.name)
            self._model = model
            self._node_to_out = {}
            self._out_to_node = {}
            try:
                graph = onnx.shape_inference.infer_shapes(model).graph
            except onnx.shape_inference.InferenceError as ex:
                warnings.warn(f"Inferring shape failed, value info is not set:\n {ex}")
                graph = model.graph
            self.inputs = {i.name for i in graph.input}
            self.outputs = {i.name for i in graph.output}
            self._value_info = graph.value_info
            for node in graph.node:
                self._add_onnx_node_internal(node)
            self._build_edges()

    def _add_onnx_node_internal(self, node: onnx.NodeProto) -> None:
        if not node.HasField("name"):
            node.name = f"{node.op_type}/{uuid4().hex}"
        name = node.name
        if name in self:
            raise RuntimeError(
                f"node '{name}' is already in the graph, "
                "duplicated name is not permitted!"
            )
        has_input = any(i in self.inputs for i in node.input)
        has_output = any(i in self.outputs for i in node.output)
        self.add_node(name, pb=node, has_input=has_input, has_output=has_output)
        self._node_to_out[name] = node.output

    def _build_edges(self):
        out_to_node = {i: k for k, v in self._node_to_out.items() for i in v}
        for n in self.nodes:
            node = self.nodes[n]["pb"]
            for i in node.input:
                if upstream := out_to_node.get(i):
                    self.add_edge(upstream, n)
        self._out_to_node = out_to_node

    def add_onnx_node(self, node: onnx.NodeProto) -> None:
        """Insert a node and its edges."""
        assert isinstance(node, onnx.NodeProto)
        self._add_onnx_node_internal(node)
        self._build_edges()
        # remove connected edge from inputs
        for output_name in node.output:
            for i, graph_input in enumerate(self.input):
                if graph_input.name == output_name:
                    self.input.pop(i)
                    self.inputs.remove(output_name)

    def remove_onnx_node(self, node: onnx.NodeProto | str, no_replace=False) -> None:
        """Remove a node from the graph"""
        assert isinstance(node, (onnx.NodeProto, str))
        if isinstance(node, str):
            name = node
            node = self.nodes[name]["pb"]
        else:
            name = node.name
        if name not in self:
            raise ValueError(f"Node {name} is not existing in the graph!")
        if no_replace:
            # dump node output info to inputs
            for output_name in node.output:
                if self._out_to_node.get(output_name) != name:
                    # node is replaced
                    continue
                shape, dtype = self.tensor_info(output_name)
                self.input.append(
                    make_value_info(output_name, make_tensor_type_proto(dtype, shape))
                )
                self.inputs.add(output_name)
        self._node_to_out.pop(name)
        for output_name in node.output:
            if self._out_to_node[output_name] == name:
                self._out_to_node.pop(output_name)
        self.remove_node(name)

    def onnx_predecessors(self, n: onnx.NodeProto | str) -> List[onnx.NodeProto]:
        """Returns a list of predecessor nodes of n."""
        assert isinstance(n, (onnx.NodeProto, str))
        preds = self.predecessors(n if isinstance(n, str) else n.name)
        return [self.nodes[p]["pb"] for p in preds]

    def onnx_successors(self, n: onnx.NodeProto | str) -> List[onnx.NodeProto]:
        """Returns a list of successors nodes of n."""
        assert isinstance(n, (onnx.NodeProto, str))
        succs = self.successors(n if isinstance(n, str) else n.name)
        return [self.nodes[s]["pb"] for s in succs]

    def onnx_subgraph(self, nodes: Iterable[onnx.NodeProto | str]) -> "OnnxGraph":
        """Create a sub onnx graph from nodes"""
        sub: nx.DiGraph = self.subgraph(
            (n if isinstance(n, str) else n.name for n in nodes)
        )
        subonnx = make_graph([], f"subgraph of {self.name}", inputs=[], outputs=[])

        def _compute_input(node):
            check_list = set()
            for pred in sub.predecessors(node.name):
                check_list.update(sub.nodes[pred]["pb"].output)
            for input_name in node.input:
                if input_name not in check_list:
                    yield input_name

        graph_inputs = set()
        for i in nx.topological_sort(sub):
            node = self.nodes[i]["pb"]
            subonnx.node.append(node)
            for output_name in node.output:
                is_outside = any(  # has an edge connected outside subgraph
                    output_name in j.input
                    for j in self.onnx_successors(node)
                    if j.name not in sub
                )
                if sub.out_degree(i) == 0 or is_outside:
                    shape, dtype = self.tensor_info(output_name)
                    subonnx.output.append(
                        make_value_info(
                            output_name, make_tensor_type_proto(dtype, shape)
                        )
                    )
            node_inputs = list(_compute_input(node))
            if node.op_type != "Constant" and node_inputs:
                graph_inputs.update(node_inputs)
        for input_name in graph_inputs:
            shape, dtype = self.tensor_info(input_name)
            subonnx.input.append(
                make_value_info(input_name, make_tensor_type_proto(dtype, shape))
            )
        sub_model = make_model(
            subonnx,
            doc_string=self._model.doc_string,
            domain=self._model.domain,
            model_version=self._model.model_version,
            ir_version=self._model.ir_version,
            opset_imports=self._model.opset_import,
            producer_name=self._model.producer_name,
            producer_version=self._model.producer_version,
        )
        return OnnxGraph(sub_model)

    def tensor_info(self, name: str) -> Tuple[List[int], int]:
        """Get shape and dtype of a tensor by its name."""
        shape = None
        dtype = onnx.TensorProto.UNDEFINED
        if name in self.inputs or name in self.outputs:
            value_infos = list(chain(self.input, self.output))
        else:
            value_infos = self._value_info
        for value_info in value_infos:
            if value_info.name == name:
                shape = [i for i in value_info.type.tensor_type.shape.dim]
                shape = [
                    int(i.dim_value) if i.dim_value else i.dim_param for i in shape
                ]
                dtype = value_info.type.tensor_type.elem_type
                break
        if shape is None:
            for tensor in self.initializer:
                if tensor.name == name:
                    shape = [int(i) for i in tensor.dims]
                    dtype = tensor.data_type
        return shape, dtype

    def tensor_shape(self, name: str) -> List[int]:
        """Get shape from a given tensor name."""
        shape, _ = self.tensor_info(name)
        if shape == onnx.TensorProto.UNDEFINED:
            raise ValueError(f"Can't find tensor shape with name '{name}'")
        return shape

    def tensor_type(self, name: str) -> int:
        """Get tensor type from a given tensor name."""
        _, elem_type = self.tensor_info(name)
        if elem_type is None:
            raise ValueError(f"Can't find tensor dtype with name '{name}'")
        return elem_type

    @property
    def input(self) -> List[onnx.ValueInfoProto]:
        """Return a list of graph inputs value info."""
        return self._model.graph.input

    @property
    def output(self) -> List[onnx.ValueInfoProto]:
        """Return a list of graph outputs value info."""
        return self._model.graph.output

    @property
    def initializer(self) -> List[onnx.TensorProto]:
        """Return a list of graph initializer tensors."""
        return self._model.graph.initializer

    @property
    def model(self) -> onnx.ModelProto:
        """Make new model"""
        graph = deepcopy(self._model.graph)
        graph.ClearField("node")
        graph.ClearField("value_info")
        for n in nx.topological_sort(self):
            graph.node.append(self.nodes[n]["pb"])
        model = make_model(
            graph,
            doc_string=self._model.doc_string,
            domain=self._model.domain,
            model_version=self._model.model_version,
            ir_version=self._model.ir_version,
            opset_imports=self._model.opset_import,
            producer_name=self._model.producer_name,
            producer_version=self._model.producer_version,
        )
        model.metadata_props.extend(self._model.metadata_props)
        return model

    # pylint: disable=redefined-builtin
    def save(
        self,
        model_path: str | os.PathLike,
        format: Optional[str] = None,
        infer_shapes: bool = True,
    ):
        """Serialize the graph to onnx model and save to model_path."""
        model = self.model
        if format == "protobuf" or format is None:
            model_path = Path(model_path).with_suffix(".onnx")
        elif format == "textproto":
            model_path = Path(model_path).with_suffix(".pbtxt")
        elif format == "json":
            model_path = Path(model_path).with_suffix(".json")
        elif format == "onnxtxt":
            model_path = Path(model_path).with_suffix(".onnxtxt")
        if infer_shapes:
            model = onnx.shape_inference.infer_shapes(model, data_prop=True)
        onnx.checker.check_model(model, full_check=True)
        onnx.save_model(model, model_path, format=format)
