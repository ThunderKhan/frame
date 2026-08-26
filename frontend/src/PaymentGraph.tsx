import { useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";

import type {
  GraphSnapshot,
} from "./api";

interface PaymentGraphProps {
  graph: GraphSnapshot;
}

function nodeColor(
  nodeType?: string,
): string {
  switch (nodeType) {
    case "customer":
      return "#8b5cf6";
    case "device":
      return "#ef4444";
    case "ip":
      return "#f59e0b";
    case "card":
      return "#22c55e";
    case "merchant":
      return "#3b82f6";
    default:
      return "#94a3b8";
  }
}

export function PaymentGraph({
  graph,
}: PaymentGraphProps) {
  const graphData = useMemo(
    () => ({
      nodes: graph.nodes.map(
        (node) => ({
          id: node.id,
          node_type:
            node.attributes.node_type,
          entity_id:
            node.attributes.entity_id,
        }),
      ),

      links: graph.edges.map(
        (edge) => ({
          source: edge.source,
          target: edge.target,
          relation:
            edge.attributes.relation,
        }),
      ),
    }),
    [graph],
  );

  if (graphData.nodes.length === 0) {
    return (
      <div className="empty-state">
        Waiting for graph activity.
      </div>
    );
  }

  return (
    <div className="graph-container">
      <ForceGraph2D
        graphData={graphData}
        backgroundColor="#0d1016"
        nodeRelSize={5}
        linkColor={() => "#343b49"}
        linkWidth={1}
        nodeCanvasObject={(
          node,
          context,
          globalScale,
        ) => {
          const label = String(
            node.entity_id ?? node.id,
          );

          const nodeType = String(
            node.node_type ?? "",
          );

          const radius = 5;

          context.beginPath();

          context.arc(
            node.x ?? 0,
            node.y ?? 0,
            radius,
            0,
            2 * Math.PI,
          );

          context.fillStyle =
            nodeColor(nodeType);

          context.fill();

          if (globalScale > 2.2) {
            const fontSize =
              11 / globalScale;

            context.font =
              `${fontSize}px Inter`;

            context.fillStyle =
              "#d7dce5";

            context.fillText(
              label,
              (node.x ?? 0) + 7,
              (node.y ?? 0) + 3,
            );
          }
        }}
        nodePointerAreaPaint={(
          node,
          color,
          context,
        ) => {
          context.beginPath();

          context.arc(
            node.x ?? 0,
            node.y ?? 0,
            6,
            0,
            2 * Math.PI,
          );

          context.fillStyle = color;
          context.fill();
        }}
      />
    </div>
  );
}