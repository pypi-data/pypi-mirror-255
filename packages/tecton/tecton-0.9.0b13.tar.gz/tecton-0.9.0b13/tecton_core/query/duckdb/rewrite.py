from tecton_core.query import nodes
from tecton_core.query.duckdb import nodes as duckdb_nodes
from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.node_interface import NodeRef


class DuckDBTreeRewriter:
    node_mapping = {
        nodes.PartialAggNode: duckdb_nodes.PartialAggDuckDBNode,
    }

    def rewrite(
        self,
        tree: NodeRef,
        prev_query_tree_step: QueryTreeStep,
    ) -> None:
        for i in tree.inputs:
            self.rewrite(tree=i, prev_query_tree_step=prev_query_tree_step)
        tree_node = tree.node
        if isinstance(tree_node, nodes.StagingNode):
            if prev_query_tree_step != tree_node.query_tree_step:
                return
            tree.node = nodes.StagedTableScanNode.from_staging_node(
                tree_node.dialect, tree_node.compute_mode, tree_node
            )
        elif tree_node.__class__ in self.node_mapping:
            tree.node = self.node_mapping[tree_node.__class__].from_query_node(tree_node)
