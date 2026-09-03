import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import ForceGraph2D, {
  type ForceGraphMethods,
} from "react-force-graph-2d";

import type {
  GraphNode,
  GraphSnapshot,
} from "./api";
import {
  DatasetPlaybackGraph,
  type DatasetStreamEvent,
} from "./DatasetPlaybackGraph";

interface PaymentGraphProps {
  graph: GraphSnapshot;
}

interface StreamGraphSnapshot extends GraphSnapshot {
  stream_events?: DatasetStreamEvent[];
  analysis_id?: string;
}

interface RenderNode extends GraphNode {
  x?: number;
  y?: number;
}

interface RenderLink {
  source: string | RenderNode;
  target: string | RenderNode;
}

interface NetworkFocusEventDetail {
  transactionId: string;
  nodeIds: string[];
}

function endpointId(endpoint: string | RenderNode): string {
  return typeof endpoint === "string" ? endpoint : endpoint.id;
}

function themeValue(name: string, fallback: string) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim() || fallback;
}

function nodeType(node: GraphNode): string {
  return String(node.attributes.node_type ?? "entity");
}

function buildSharedInfrastructure(graph: GraphSnapshot): Set<string> {
  const types = new Map(graph.nodes.map((node) => [node.id, nodeType(node)]));
  const customerNeighbors = new Map<string, Set<string>>();

  for (const edge of graph.edges) {
    const sourceType = types.get(edge.source);
    const targetType = types.get(edge.target);

    if (
      (sourceType === "device" || sourceType === "ip") &&
      targetType === "customer"
    ) {
      const neighbors = customerNeighbors.get(edge.source) ?? new Set<string>();
      neighbors.add(edge.target);
      customerNeighbors.set(edge.source, neighbors);
    }

    if (
      (targetType === "device" || targetType === "ip") &&
      sourceType === "customer"
    ) {
      const neighbors = customerNeighbors.get(edge.target) ?? new Set<string>();
      neighbors.add(edge.source);
      customerNeighbors.set(edge.target, neighbors);
    }
  }

  return new Set(
    [...customerNeighbors.entries()]
      .filter(([, customers]) => customers.size >= 2)
      .map(([id]) => id),
  );
}

function nodeRadius(type: string, shared: boolean, focused: boolean) {
  if (focused) {
    return 7;
  }
  if (shared) {
    return 6;
  }

  switch (type) {
    case "customer":
      return 3.6;
    case "device":
    case "ip":
      return 3.2;
    case "card":
      return 2.8;
    case "merchant":
      return 2.6;
    default:
      return 2.8;
  }
}

function ImmediatePaymentGraph({ graph }: PaymentGraphProps) {
  const graphRef = useRef<ForceGraphMethods | undefined>(undefined);
  const [focusedNodeIds, setFocusedNodeIds] = useState<Set<string>>(new Set());
  const [focusedTransactionId, setFocusedTransactionId] = useState<string | null>(null);

  const sharedInfrastructure = useMemo(
    () => buildSharedInfrastructure(graph),
    [graph],
  );

  const sharedNeighbors = useMemo(() => {
    const neighbors = new Set<string>();
    for (const edge of graph.edges) {
      if (sharedInfrastructure.has(edge.source)) {
        neighbors.add(edge.target);
      }
      if (sharedInfrastructure.has(edge.target)) {
        neighbors.add(edge.source);
      }
    }
    return neighbors;
  }, [graph.edges, sharedInfrastructure]);

  useEffect(() => {
    function handleFocus(event: Event) {
      const detail = (event as CustomEvent<NetworkFocusEventDetail>).detail;
      const ids = detail?.nodeIds ?? [];
      setFocusedNodeIds(new Set(ids));
      setFocusedTransactionId(detail?.transactionId ?? null);

      window.setTimeout(() => {
        graphRef.current?.zoomToFit(
          700,
          90,
          (rawNode) => ids.includes((rawNode as RenderNode).id),
        );
      }, 80);
    }

    window.addEventListener("frame:focus-network", handleFocus);
    return () => window.removeEventListener("frame:focus-network", handleFocus);
  }, []);

  useEffect(() => {
    if (graph.nodes.length === 0) {
      return;
    }

    const timer = window.setTimeout(
      () => graphRef.current?.zoomToFit(600, 70),
      180,
    );
    return () => window.clearTimeout(timer);
  }, [graph]);

  if (graph.nodes.length === 0) {
    return (
      <div
        style={{
          minHeight: 560,
          display: "grid",
          placeItems: "center",
          color: "var(--graph-fg)",
          background: "var(--graph-bg)",
          fontFamily: '"JetBrains Mono", Consolas, monospace',
          fontSize: 11,
          letterSpacing: ".08em",
        }}
      >
        &gt;&gt;&gt; WAITING FOR GRAPH ACTIVITY
      </div>
    );
  }

  const red = themeValue("--red", "#ff3b30");
  const background = themeValue("--graph-bg", "#050505");
  const foreground = themeValue("--graph-fg", "#f4f4f0");

  return (
    <div style={{ position: "relative", minHeight: 560, background }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={{
          nodes: graph.nodes.map((node) => ({ ...node })),
          links: graph.edges.map((edge) => ({ ...edge })),
        }}
        backgroundColor={background}
        warmupTicks={40}
        cooldownTicks={90}
        d3AlphaDecay={0.04}
        d3VelocityDecay={0.34}
        nodeRelSize={4}
        linkColor={(rawLink) => {
          const link = rawLink as RenderLink;
          const source = endpointId(link.source);
          const target = endpointId(link.target);
          return sharedInfrastructure.has(source) || sharedInfrastructure.has(target)
            ? red
            : "rgba(244,244,240,0.12)";
        }}
        linkWidth={(rawLink) => {
          const link = rawLink as RenderLink;
          const source = endpointId(link.source);
          const target = endpointId(link.target);
          return sharedInfrastructure.has(source) || sharedInfrastructure.has(target)
            ? 1.8
            : 0.45;
        }}
        linkDirectionalParticles={(rawLink) => {
          const link = rawLink as RenderLink;
          return sharedInfrastructure.has(endpointId(link.source)) ||
            sharedInfrastructure.has(endpointId(link.target))
            ? 1
            : 0;
        }}
        linkDirectionalParticleWidth={1.2}
        linkDirectionalParticleColor={() => red}
        nodeCanvasObject={(rawNode, context, globalScale) => {
          const node = rawNode as RenderNode;
          const type = nodeType(node);
          const shared = sharedInfrastructure.has(node.id);
          const connected = sharedNeighbors.has(node.id);
          const focused = focusedNodeIds.has(node.id);
          const radius = nodeRadius(type, shared, focused);
          const x = node.x ?? 0;
          const y = node.y ?? 0;

          context.beginPath();
          context.arc(x, y, radius, 0, Math.PI * 2);
          context.fillStyle = shared
            ? red
            : connected || focused
              ? foreground
              : "rgba(244,244,240,0.28)";
          context.fill();

          if (shared || focused) {
            context.strokeStyle = shared ? red : foreground;
            context.lineWidth = 1.2;
            context.beginPath();
            context.arc(x, y, radius + 3, 0, Math.PI * 2);
            context.stroke();
          }

          if (shared && (sharedInfrastructure.size <= 10 || globalScale > 2.5)) {
            const label = type === "device" ? "SHARED DEVICE" : "SHARED IP";
            const fontSize = Math.max(3.1, 10 / globalScale);
            context.font = `800 ${fontSize}px "JetBrains Mono", Consolas, monospace`;
            context.textAlign = "left";
            context.textBaseline = "middle";
            context.fillStyle = red;
            context.fillText(label, x + radius + 5, y);
          }
        }}
        nodePointerAreaPaint={(rawNode, color, context) => {
          const node = rawNode as RenderNode;
          context.beginPath();
          context.arc(node.x ?? 0, node.y ?? 0, 7, 0, Math.PI * 2);
          context.fillStyle = color;
          context.fill();
        }}
        nodeLabel={(rawNode) => {
          const node = rawNode as RenderNode;
          const type = nodeType(node);
          const entity = String(node.attributes.entity_id ?? node.id);
          const status = sharedInfrastructure.has(node.id)
            ? "SHARED ACROSS MULTIPLE CUSTOMERS"
            : "OBSERVED ENTITY";
          return `${entity}\nTYPE: ${type}\n${status}`;
        }}
      />

      {focusedTransactionId && (
        <div
          style={{
            position: "absolute",
            top: 16,
            right: 16,
            padding: "11px 13px",
            border: "1px solid rgba(244,244,240,.35)",
            color: foreground,
            background: "rgba(5,5,5,.86)",
            fontFamily: '"JetBrains Mono", Consolas, monospace',
            fontSize: 9,
            fontWeight: 800,
            letterSpacing: ".07em",
          }}
        >
          CASE FOCUS /// {focusedTransactionId}
        </div>
      )}
    </div>
  );
}

export function PaymentGraph({ graph }: PaymentGraphProps) {
  const streamGraph = graph as StreamGraphSnapshot;
  const events = streamGraph.stream_events ?? [];

  if (events.length > 0) {
    return (
      <DatasetPlaybackGraph
        key={streamGraph.analysis_id ?? `${events[0]?.transaction_id ?? "stream"}-${events.length}`}
        graph={graph}
        events={events}
      />
    );
  }

  return <ImmediatePaymentGraph graph={graph} />;
}
