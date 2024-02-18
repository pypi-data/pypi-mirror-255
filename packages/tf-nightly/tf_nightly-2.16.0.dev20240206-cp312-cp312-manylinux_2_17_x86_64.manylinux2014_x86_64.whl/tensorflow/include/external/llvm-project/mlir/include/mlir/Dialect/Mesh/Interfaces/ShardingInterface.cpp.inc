/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

/// Returns a list of iterator types that describe the number of loops.
/// The iterator types determine how the operation traverses its input and
/// output tensors.
/// 
/// Example 1: A gemm op has 3 loops, M, N and K. Their loop iterator
/// types are parallel, parallel, reduction-sum. This indicates that M and
/// N are traversed in parallel, while the K dimension is used for
/// reduction.
/// 
/// Example 2: A softmax op's loop iterator types are parallel and
/// invalid. The second dimension is considered as invalid because it is
/// neither parallel nor any kind of reduction. 
SmallVector<::mlir::mesh::IteratorType> mlir::mesh::ShardingInterface::getLoopIteratorTypes() {
      return getImpl()->getLoopIteratorTypes(getImpl(), getOperation());
  }
/// Return the indexing maps attribute within the current operation.
/// Indexing maps determine how indices in the iteration space map to
/// tensor indices. They are specified using `affine_map` in MLIR, which
/// provides an affine transformation of indices.
SmallVector<AffineMap> mlir::mesh::ShardingInterface::getIndexingMaps() {
      return getImpl()->getIndexingMaps(getImpl(), getOperation());
  }
/// Given that certain operands or results of the operation may have
/// sharding annotations, this method leverages this information to deduce
/// how the operation should be sharded.
FailureOr<ShardingOption> mlir::mesh::ShardingInterface::getShardingOption(ArrayRef<MeshShardingAttr> operandShardings, ArrayRef<MeshShardingAttr> resultShardings) {
      return getImpl()->getShardingOption(getImpl(), getOperation(), operandShardings, resultShardings);
  }
/// Based on a given ShardingOption, this method adds `mesh.shard`
/// operations for the operands and results that previously lacked
/// sharding annotations.
LogicalResult mlir::mesh::ShardingInterface::addShardingAnnotations(OpBuilder & b, const ShardingOption & shardingOption) {
      return getImpl()->addShardingAnnotations(getImpl(), getOperation(), b, shardingOption);
  }
