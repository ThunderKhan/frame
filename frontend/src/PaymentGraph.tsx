import {
  useMemo,
} from "react";

import ForceGraph2D from "react-force-graph-2d";

import type {
  GraphEdge,
  GraphNode,
  GraphSnapshot,
} from "./api";

interface PaymentGraphProps {
  graph: GraphSnapshot;
}

interface RenderNode {
  id: string;

  node_type?: string;
  entity_id?: string;

  degree: number;

  suspiciousInfrastructure: boolean;
  suspiciousNeighbor: boolean;

  x?: number;
  y?: number;
}

interface RenderLink {
  source: string | RenderNode;
  target: string | RenderNode;

  relation?: string;

  suspicious: boolean;
}

interface ThemeColors {
  red: string;
  graphBackground: string;
  graphForeground: string;
}

function endpointId(
  endpoint:
    | string
    | RenderNode,
): string {
  if (
    typeof endpoint ===
    "string"
  ) {
    return endpoint;
  }

  return endpoint.id;
}

function getNodeType(
  node: GraphNode,
): string {
  return String(
    node.attributes.node_type ??
      "",
  );
}

function buildDegreeMap(
  graph: GraphSnapshot,
): Map<string, number> {
  const degree =
    new Map<
      string,
      number
    >();

  for (
    const node
    of graph.nodes
  ) {
    degree.set(
      node.id,
      0,
    );
  }

  for (
    const edge
    of graph.edges
  ) {
    degree.set(
      edge.source,
      (
        degree.get(
          edge.source,
        ) ?? 0
      ) + 1,
    );

    degree.set(
      edge.target,
      (
        degree.get(
          edge.target,
        ) ?? 0
      ) + 1,
    );
  }

  return degree;
}

function buildSuspiciousInfrastructure(
  graph: GraphSnapshot,
  degree: Map<
    string,
    number
  >,
): Set<string> {
  const suspicious =
    new Set<string>();

  for (
    const node
    of graph.nodes
  ) {
    const nodeType =
      getNodeType(
        node,
      );

    const nodeDegree =
      degree.get(
        node.id,
      ) ?? 0;

    /*
     * This is an observed graph property,
     * not model attribution.
     *
     * A device/IP with degree >= 2 has
     * already been observed across more
     * than one customer relationship.
     */
    if (
      (
        nodeType ===
          "device" ||
        nodeType ===
          "ip"
      ) &&
      nodeDegree >= 2
    ) {
      suspicious.add(
        node.id,
      );
    }
  }

  return suspicious;
}

function buildSuspiciousNeighbors(
  edges: GraphEdge[],
  suspiciousInfrastructure:
    Set<string>,
): Set<string> {
  const neighbors =
    new Set<string>();

  for (
    const edge
    of edges
  ) {
    if (
      suspiciousInfrastructure.has(
        edge.source,
      )
    ) {
      neighbors.add(
        edge.target,
      );
    }

    if (
      suspiciousInfrastructure.has(
        edge.target,
      )
    ) {
      neighbors.add(
        edge.source,
      );
    }
  }

  return neighbors;
}

function themeColors(): ThemeColors {
  const root =
    getComputedStyle(
      document.documentElement,
    );

  return {
    red:
      root
        .getPropertyValue(
          "--red",
        )
        .trim() ||
      "#e61919",

    graphBackground:
      root
        .getPropertyValue(
          "--graph-bg",
        )
        .trim() ||
      "#050505",

    graphForeground:
      root
        .getPropertyValue(
          "--graph-fg",
        )
        .trim() ||
      "#f4f4f0",
  };
}

function abbreviatedEntityLabel(
  node: RenderNode,
): string {
  const entity =
    String(
      node.entity_id ??
        node.id,
    );

  if (
    entity.length <= 21
  ) {
    return entity;
  }

  return `${entity.slice(
    0,
    18,
  )}...`;
}

function nodeRadius(
  node: RenderNode,
): number {
  if (
    node.suspiciousInfrastructure
  ) {
    return 7;
  }

  if (
    node.suspiciousNeighbor
  ) {
    return 4.5;
  }

  switch (
    node.node_type
  ) {
    case "customer":
      return 3.2;

    case "merchant":
      return 2.4;

    case "device":
    case "ip":
      return 3;

    case "card":
      return 2.2;

    default:
      return 2.5;
  }
}

function drawBackingPlate(
  context:
    CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  align:
    | "left"
    | "right",
  background: string,
) {
  const horizontalPadding = 4;
  const verticalPadding = 3;

  const plateX =
    align === "left"
      ? x -
        horizontalPadding
      : x -
        width -
        horizontalPadding;

  const plateY =
    y -
    height /
      2 -
    verticalPadding;

  context.fillStyle =
    background;

  context.globalAlpha =
    0.88;

  context.fillRect(
    plateX,
    plateY,
    width +
      horizontalPadding *
        2,
    height +
      verticalPadding *
        2,
  );

  context.globalAlpha =
    1;
}

function drawSuspiciousLabel(
  context:
    CanvasRenderingContext2D,
  node: RenderNode,
  radius: number,
  globalScale: number,
  colors: ThemeColors,
) {
  const x =
    node.x ?? 0;

  const y =
    node.y ?? 0;

  const nodeType =
    node.node_type ??
    "entity";

  /*
   * Device labels live to the LEFT.
   * IP labels live to the RIGHT.
   *
   * This deliberately separates the two
   * highest-value labels in the fraud ring.
   */
  const labelOnLeft =
    nodeType ===
    "device";

  const direction =
    labelOnLeft
      ? -1
      : 1;

  const textAlign:
    | "left"
    | "right" =
    labelOnLeft
      ? "right"
      : "left";

  const labelX =
    x +
    direction *
      (
        radius +
        11
      );

  const primaryY =
    y - 3;

  const secondaryY =
    y + 9;

  const primary =
    nodeType ===
    "device"
      ? "SHARED DEVICE"
      : nodeType ===
          "ip"
        ? "SHARED IP"
        : "SHARED INFRA";

  const secondary =
    abbreviatedEntityLabel(
      node,
    );

  const primarySize =
    Math.max(
      3.4,
      11 /
        globalScale,
    );

  const secondarySize =
    Math.max(
      2.7,
      8 /
        globalScale,
    );

  context.textAlign =
    textAlign;

  context.textBaseline =
    "middle";

  context.font =
    `800 ${primarySize}px ` +
    `"JetBrains Mono", ` +
    `Consolas, monospace`;

  const primaryWidth =
    context.measureText(
      primary,
    ).width;

  context.font =
    `700 ${secondarySize}px ` +
    `"JetBrains Mono", ` +
    `Consolas, monospace`;

  const secondaryWidth =
    context.measureText(
      secondary,
    ).width;

  const plateWidth =
    Math.max(
      primaryWidth,
      secondaryWidth,
    );

  drawBackingPlate(
    context,
    labelX,
    y + 3,
    plateWidth,
    primarySize +
      secondarySize +
      10,
    textAlign,
    colors.graphBackground,
  );

  context.textAlign =
    textAlign;

  context.textBaseline =
    "middle";

  context.font =
    `800 ${primarySize}px ` +
    `"JetBrains Mono", ` +
    `Consolas, monospace`;

  context.fillStyle =
    colors.red;

  context.fillText(
    primary,
    labelX,
    primaryY,
  );

  context.font =
    `700 ${secondarySize}px ` +
    `"JetBrains Mono", ` +
    `Consolas, monospace`;

  context.fillStyle =
    "rgba(244, 244, 240, 0.62)";

  context.fillText(
    secondary,
    labelX,
    secondaryY,
  );
}

function drawContextLabel(
  context:
    CanvasRenderingContext2D,
  node: RenderNode,
  radius: number,
  globalScale: number,
  colors: ThemeColors,
) {
  const x =
    node.x ?? 0;

  const y =
    node.y ?? 0;

  const label =
    abbreviatedEntityLabel(
      node,
    );

  const fontSize =
    Math.max(
      2.8,
      9 /
        globalScale,
    );

  context.font =
    `700 ${fontSize}px ` +
    `"JetBrains Mono", ` +
    `Consolas, monospace`;

  context.textAlign =
    "left";

  context.textBaseline =
    "middle";

  const labelX =
    x +
    radius +
    5;

  const width =
    context.measureText(
      label,
    ).width;

  drawBackingPlate(
    context,
    labelX,
    y,
    width,
    fontSize,
    "left",
    colors.graphBackground,
  );

  context.fillStyle =
    colors.graphForeground;

  context.fillText(
    label,
    labelX,
    y,
  );
}

export function PaymentGraph({
  graph,
}: PaymentGraphProps) {
  const graphData =
    useMemo(
      () => {
        const degree =
          buildDegreeMap(
            graph,
          );

        const suspiciousInfrastructure =
          buildSuspiciousInfrastructure(
            graph,
            degree,
          );

        const suspiciousNeighbors =
          buildSuspiciousNeighbors(
            graph.edges,
            suspiciousInfrastructure,
          );

        const nodes: RenderNode[] =
          graph.nodes.map(
            (node) => ({
              id:
                node.id,

              node_type:
                node.attributes
                  .node_type,

              entity_id:
                node.attributes
                  .entity_id,

              degree:
                degree.get(
                  node.id,
                ) ?? 0,

              suspiciousInfrastructure:
                suspiciousInfrastructure.has(
                  node.id,
                ),

              suspiciousNeighbor:
                suspiciousNeighbors.has(
                  node.id,
                ),
            }),
          );

        const links: RenderLink[] =
          graph.edges.map(
            (edge) => ({
              source:
                edge.source,

              target:
                edge.target,

              relation:
                edge.attributes
                  .relation,

              suspicious:
                suspiciousInfrastructure.has(
                  edge.source,
                ) ||
                suspiciousInfrastructure.has(
                  edge.target,
                ),
            }),
          );

        return {
          nodes,
          links,

          suspiciousCount:
            suspiciousInfrastructure
              .size,
        };
      },
      [graph],
    );

  if (
    graphData.nodes
      .length === 0
  ) {
    return (
      <div
        className="empty-state"
        style={{
          width:
            "100%",

          height:
            "620px",

          display:
            "grid",

          placeItems:
            "center",

          color:
            "var(--graph-fg)",

          background:
            "var(--graph-bg)",

          fontFamily:
            '"JetBrains Mono", Consolas, monospace',

          fontSize:
            "12px",

          letterSpacing:
            "0.1em",

          textTransform:
            "uppercase",
        }}
      >
        &gt;&gt;&gt;
        {" "}
        WAITING FOR
        GRAPH ACTIVITY
      </div>
    );
  }

  const colors =
    themeColors();

  return (
    <div
      className="graph-container"
      style={{
        position:
          "relative",
      }}
    >
      <ForceGraph2D
        graphData={{
          nodes:
            graphData.nodes,

          links:
            graphData.links,
        }}

        backgroundColor={
          colors.graphBackground
        }

        nodeRelSize={
          4
        }

        warmupTicks={
          80
        }

        cooldownTicks={
          120
        }

        d3AlphaDecay={
          0.035
        }

        d3VelocityDecay={
          0.3
        }

        linkColor={(
          rawLink,
        ) => {
          const link =
            rawLink as RenderLink;

          if (
            link.suspicious
          ) {
            return colors.red;
          }

          return (
            "rgba(244, 244, 240, 0.13)"
          );
        }}

        linkWidth={(
          rawLink,
        ) => {
          const link =
            rawLink as RenderLink;

          return (
            link.suspicious
              ? 2.2
              : 0.55
          );
        }}

        linkDirectionalParticles={(
          rawLink,
        ) => {
          const link =
            rawLink as RenderLink;

          return (
            link.suspicious
              ? 2
              : 0
          );
        }}

        linkDirectionalParticleWidth={(
          rawLink,
        ) => {
          const link =
            rawLink as RenderLink;

          return (
            link.suspicious
              ? 1.7
              : 0
          );
        }}

        linkDirectionalParticleColor={() =>
          colors.red
        }

        nodeCanvasObject={(
          rawNode,
          context,
          globalScale,
        ) => {
          const node =
            rawNode as RenderNode;

          const x =
            node.x ?? 0;

          const y =
            node.y ?? 0;

          const radius =
            nodeRadius(
              node,
            );

          /*
           * SHARED DEVICE / IP
           */
          if (
            node.suspiciousInfrastructure
          ) {
            context.beginPath();

            context.arc(
              x,
              y,
              radius + 3,
              0,
              2 *
                Math.PI,
            );

            context.strokeStyle =
              colors.red;

            context.lineWidth =
              1.2;

            context.stroke();

            context.beginPath();

            context.arc(
              x,
              y,
              radius,
              0,
              2 *
                Math.PI,
            );

            context.fillStyle =
              colors.red;

            context.fill();
          } else if (
            node.suspiciousNeighbor
          ) {
            /*
             * Connected customers remain
             * monochrome but receive a
             * clearly visible outline.
             */
            context.beginPath();

            context.arc(
              x,
              y,
              radius,
              0,
              2 *
                Math.PI,
            );

            context.fillStyle =
              colors.graphBackground;

            context.fill();

            context.strokeStyle =
              colors.graphForeground;

            context.lineWidth =
              1.4;

            context.stroke();
          } else {
            /*
             * Ordinary graph context should
             * stay visually subordinate.
             */
            context.beginPath();

            context.arc(
              x,
              y,
              radius,
              0,
              2 *
                Math.PI,
            );

            context.fillStyle =
              "rgba(244, 244, 240, 0.24)";

            context.fill();
          }

          /*
           * Suspicious infrastructure always
           * gets a deliberate, non-colliding
           * primary label.
           */
          if (
            node.suspiciousInfrastructure
          ) {
            drawSuspiciousLabel(
              context,
              node,
              radius,
              globalScale,
              colors,
            );

            return;
          }

          /*
           * Connected customers don't need
           * labels until the analyst zooms in.
           */
          if (
            node.suspiciousNeighbor &&
            globalScale >
              2
          ) {
            drawContextLabel(
              context,
              node,
              radius,
              globalScale,
              colors,
            );

            return;
          }

          /*
           * Ordinary context labels appear
           * only at close inspection.
           */
          if (
            globalScale >
            4
          ) {
            drawContextLabel(
              context,
              node,
              radius,
              globalScale,
              colors,
            );
          }
        }}

        nodePointerAreaPaint={(
          rawNode,
          color,
          context,
        ) => {
          const node =
            rawNode as RenderNode;

          const radius =
            nodeRadius(
              node,
            );

          context.beginPath();

          context.arc(
            node.x ?? 0,
            node.y ?? 0,
            Math.max(
              7,
              radius + 3,
            ),
            0,
            2 *
              Math.PI,
          );

          context.fillStyle =
            color;

          context.fill();
        }}

        nodeLabel={(
          rawNode,
        ) => {
          const node =
            rawNode as RenderNode;

          const status =
            node.suspiciousInfrastructure
              ? "SHARED INFRASTRUCTURE"
              : node.suspiciousNeighbor
                ? "CONNECTED CUSTOMER"
                : "OBSERVED ENTITY";

          return [
            String(
              node.entity_id ??
                node.id,
            ),

            `TYPE: ${
              node.node_type ??
              "unknown"
            }`,

            `DEGREE: ${
              node.degree
            }`,

            status,
          ].join(
            "\n",
          );
        }}

        linkLabel={(
          rawLink,
        ) => {
          const link =
            rawLink as RenderLink;

          const source =
            endpointId(
              link.source,
            );

          const target =
            endpointId(
              link.target,
            );

          return [
            link.relation ??
              "relationship",

            `${source} → ${target}`,

            link.suspicious
              ? "SHARED-INFRASTRUCTURE PATH"
              : "OBSERVED RELATIONSHIP",
          ].join(
            "\n",
          );
        }}
      />

      <div
        style={{
          position:
            "absolute",

          left:
            "18px",

          bottom:
            "18px",

          zIndex:
            5,

          display:
            "grid",

          gap:
            "8px",

          minWidth:
            "230px",

          padding:
            "14px",

          border:
            "1px solid rgba(244,244,240,0.45)",

          color:
            colors.graphForeground,

          background:
            "rgba(5,5,5,0.82)",

          backdropFilter:
            "blur(10px)",

          fontFamily:
            '"JetBrains Mono", Consolas, monospace',

          fontSize:
            "10px",

          fontWeight:
            700,

          letterSpacing:
            "0.08em",

          textTransform:
            "uppercase",

          pointerEvents:
            "none",
        }}
      >
        <div
          style={{
            color:
              colors.red,
          }}
        >
          [
          {" "}
          NETWORK SIGNAL
          {" "}
          ]
        </div>

        <div>
          <span
            style={{
              color:
                colors.red,

              marginRight:
                "9px",
            }}
          >
            ●
          </span>

          SHARED DEVICE /
          IP
        </div>

        <div>
          <span
            style={{
              marginRight:
                "9px",
            }}
          >
            ○
          </span>

          CONNECTED
          CUSTOMER
        </div>

        <div
          style={{
            opacity:
              0.55,
          }}
        >
          · ORDINARY
          CONTEXT
        </div>

        <div
          style={{
            marginTop:
              "4px",

            paddingTop:
              "8px",

            borderTop:
              "1px solid rgba(244,244,240,0.22)",
          }}
        >
          SHARED INFRA:
          {" "}
          {String(
            graphData
              .suspiciousCount,
          ).padStart(
            2,
            "0",
          )}
        </div>
      </div>
    </div>
  );
}