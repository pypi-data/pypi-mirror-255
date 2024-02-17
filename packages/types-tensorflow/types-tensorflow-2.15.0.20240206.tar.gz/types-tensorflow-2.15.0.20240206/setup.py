from setuptools import setup

name = "types-tensorflow"
description = "Typing stubs for tensorflow"
long_description = '''
## Typing stubs for tensorflow

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`tensorflow`](https://github.com/tensorflow/tensorflow) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`tensorflow`.

This version of `types-tensorflow` aims to provide accurate annotations
for `tensorflow==2.15.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/tensorflow. All fixes for
types and metadata should be contributed there.

Partially generated using [mypy-protobuf==3.5.0](https://github.com/nipunn1313/mypy-protobuf/tree/v3.5.0) on tensorflow==2.12.1

This stub package is marked as [partial](https://peps.python.org/pep-0561/#partial-stub-packages).
If you find that annotations are missing, feel free to contribute and help complete them.


See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `ed38e99138cd716b077e459274cefb6544e00868` and was tested
with mypy 1.8.0, pyright 1.1.342, and
pytype 2024.1.24.
'''.lstrip()

setup(name=name,
      version="2.15.0.20240206",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/tensorflow.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-protobuf', 'types-requests', 'numpy>=1.20'],
      packages=['tensorflow-stubs'],
      package_data={'tensorflow-stubs': ['__init__.pyi', '_aliases.pyi', 'compiler/xla/autotune_results_pb2.pyi', 'compiler/xla/service/hlo_pb2.pyi', 'compiler/xla/service/metrics_pb2.pyi', 'compiler/xla/xla_data_pb2.pyi', 'config/__init__.pyi', 'config/experimental.pyi', 'core/example/example_parser_configuration_pb2.pyi', 'core/example/example_pb2.pyi', 'core/example/feature_pb2.pyi', 'core/framework/allocation_description_pb2.pyi', 'core/framework/api_def_pb2.pyi', 'core/framework/attr_value_pb2.pyi', 'core/framework/cost_graph_pb2.pyi', 'core/framework/dataset_metadata_pb2.pyi', 'core/framework/dataset_options_pb2.pyi', 'core/framework/dataset_pb2.pyi', 'core/framework/device_attributes_pb2.pyi', 'core/framework/full_type_pb2.pyi', 'core/framework/function_pb2.pyi', 'core/framework/graph_pb2.pyi', 'core/framework/graph_transfer_info_pb2.pyi', 'core/framework/kernel_def_pb2.pyi', 'core/framework/log_memory_pb2.pyi', 'core/framework/model_pb2.pyi', 'core/framework/node_def_pb2.pyi', 'core/framework/op_def_pb2.pyi', 'core/framework/optimized_function_graph_pb2.pyi', 'core/framework/reader_base_pb2.pyi', 'core/framework/resource_handle_pb2.pyi', 'core/framework/step_stats_pb2.pyi', 'core/framework/summary_pb2.pyi', 'core/framework/tensor_description_pb2.pyi', 'core/framework/tensor_pb2.pyi', 'core/framework/tensor_shape_pb2.pyi', 'core/framework/tensor_slice_pb2.pyi', 'core/framework/types_pb2.pyi', 'core/framework/variable_pb2.pyi', 'core/framework/versions_pb2.pyi', 'core/protobuf/__init__.pyi', 'core/protobuf/bfc_memory_map_pb2.pyi', 'core/protobuf/cluster_pb2.pyi', 'core/protobuf/composite_tensor_variant_pb2.pyi', 'core/protobuf/config_pb2.pyi', 'core/protobuf/control_flow_pb2.pyi', 'core/protobuf/coordination_config_pb2.pyi', 'core/protobuf/core_platform_payloads_pb2.pyi', 'core/protobuf/data_service_pb2.pyi', 'core/protobuf/debug_event_pb2.pyi', 'core/protobuf/debug_pb2.pyi', 'core/protobuf/device_filters_pb2.pyi', 'core/protobuf/device_properties_pb2.pyi', 'core/protobuf/distributed_runtime_payloads_pb2.pyi', 'core/protobuf/error_codes_pb2.pyi', 'core/protobuf/fingerprint_pb2.pyi', 'core/protobuf/graph_debug_info_pb2.pyi', 'core/protobuf/meta_graph_pb2.pyi', 'core/protobuf/named_tensor_pb2.pyi', 'core/protobuf/queue_runner_pb2.pyi', 'core/protobuf/remote_tensor_handle_pb2.pyi', 'core/protobuf/rewriter_config_pb2.pyi', 'core/protobuf/rpc_options_pb2.pyi', 'core/protobuf/saved_model_pb2.pyi', 'core/protobuf/saved_object_graph_pb2.pyi', 'core/protobuf/saver_pb2.pyi', 'core/protobuf/service_config_pb2.pyi', 'core/protobuf/snapshot_pb2.pyi', 'core/protobuf/struct_pb2.pyi', 'core/protobuf/tensor_bundle_pb2.pyi', 'core/protobuf/tensorflow_server_pb2.pyi', 'core/protobuf/tpu/compilation_result_pb2.pyi', 'core/protobuf/tpu/dynamic_padding_pb2.pyi', 'core/protobuf/tpu/optimization_parameters_pb2.pyi', 'core/protobuf/tpu/topology_pb2.pyi', 'core/protobuf/tpu/tpu_embedding_configuration_pb2.pyi', 'core/protobuf/trackable_object_graph_pb2.pyi', 'core/protobuf/transport_options_pb2.pyi', 'core/protobuf/verifier_config_pb2.pyi', 'core/util/event_pb2.pyi', 'core/util/memmapped_file_system_pb2.pyi', 'core/util/saved_tensor_slice_pb2.pyi', 'core/util/test_log_pb2.pyi', 'data/__init__.pyi', 'data/experimental.pyi', 'dtypes.pyi', 'experimental/__init__.pyi', 'feature_column/__init__.pyi', 'initializers.pyi', 'io/__init__.pyi', 'io/gfile.pyi', 'keras/__init__.pyi', 'keras/activations.pyi', 'keras/callbacks.pyi', 'keras/constraints.pyi', 'keras/initializers.pyi', 'keras/layers.pyi', 'keras/losses.pyi', 'keras/metrics.pyi', 'keras/models.pyi', 'keras/optimizers/__init__.pyi', 'keras/optimizers/legacy/__init__.pyi', 'keras/optimizers/schedules.pyi', 'keras/regularizers.pyi', 'math.pyi', 'python/__init__.pyi', 'python/feature_column/__init__.pyi', 'python/feature_column/feature_column_v2.pyi', 'python/feature_column/sequence_feature_column.pyi', 'python/framework/dtypes.pyi', 'python/keras/__init__.pyi', 'python/keras/protobuf/projector_config_pb2.pyi', 'python/keras/protobuf/saved_metadata_pb2.pyi', 'python/keras/protobuf/versions_pb2.pyi', 'python/trackable/__init__.pyi', 'python/trackable/autotrackable.pyi', 'python/trackable/base.pyi', 'sparse.pyi', 'train/__init__.pyi', 'train/experimental.pyi', 'tsl/protobuf/autotuning_pb2.pyi', 'tsl/protobuf/bfc_memory_map_pb2.pyi', 'tsl/protobuf/coordination_config_pb2.pyi', 'tsl/protobuf/coordination_service_pb2.pyi', 'tsl/protobuf/distributed_runtime_payloads_pb2.pyi', 'tsl/protobuf/dnn_pb2.pyi', 'tsl/protobuf/error_codes_pb2.pyi', 'tsl/protobuf/histogram_pb2.pyi', 'tsl/protobuf/rpc_options_pb2.pyi', 'tsl/protobuf/test_log_pb2.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
