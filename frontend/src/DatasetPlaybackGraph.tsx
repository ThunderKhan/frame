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
  GraphEdge,
  GraphNode,
  GraphSnapshot,
} from "./api";

import "./DatasetPlaybackGraph.css";

export interface DatasetStreamEvent {
  transaction_id: string;
  row: number;
  amount: number;
  label: number | null;
  entities: string[];
}

interface DatasetPlaybackGraphProps {
  graph: GraphSnapshot;
  events: DatasetStreamEvent[];
  analysisId: string;
}

interface RenderNode extends GraphNode {
  x?: number;
  y?: number;
}

interface RenderLink extends GraphEdge {
  source: string | RenderNode;
  target: string | RenderNode;
}

function endpointId(endpoint: string | RenderNode): string {
  return typeof endpoint === "string" ? endpoint : endpoint.id;
}

function themeValue(name: string, fallback: string) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim() || fallback;
}

function buildVisibleGraph(
  fullGraph: GraphSnapshot,
  events: DatasetStreamEvent[],
  visibleEventCount: number,
): GraphSnapshot {
  if (visibleEventCount >= events.length) {
    return fullGraph;
  }

  const visibleIds = new Set<string>();
  const visiblePairs = new Set<string>();

  for (const event of events.slice(0, visibleEventCount)) {
    const entities = event.entities.filter(Boolean);

    for (const entity of entities) {
      visibleIds.add(entity);
    }

    for (let left = 0; left < entities.length; left += 1) {
      for (let right = left + 1; right < entities.length; right += 1) {
        const a = entities[left];
        const b = entities[right];
        visiblePairs.add(a < b ? `${a}\u0000${b}` : `${b}\u0000${a}`);
      }
    }
  }

  return {
    nodes: fullGraph.nodes.filter((node) => visibleIds.has(node.id)),
    edges: fullGraph.edges.filter((edge) => {
      const key = edge.source < edge.target
        ? `${edge.source}\u0000${edge.target}`
        : `${edge.target}\u0000${edge.source}`;
      return visiblePairs.has(key);
    }),
  };
}

function buildSharedInfrastructure(graph: GraphSnapshot): Set<string> {
  const nodeTypes = new Map(
    graph.nodes.map((node) => [
      node.id,
      String(node.attributes.node_type ?? "entity"),
    ]),
  );

  const customerNeighbors = new Map<string, Set<string>>();

  for (const edge of graph.edges) {
    const sourceType = nodeTypes.get(edge.source);
    const targetType = nodeTypes.get(edge.target);

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
      .map(([nodeId]) => nodeId),
  );
}

function nodeRadius(nodeType: string, shared: boolean) {
  if (shared) {
    return 6;
  }

  switch (nodeType) {
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

export function DatasetPlaybackGraph({
  graph,
  events,
  analysisId,
}: DatasetPlaybackGraphProps) {
  const graphRef = useRef<ForceGraphMethods | undefined>(undefined);
  const [visibleEventCount, setVisibleEventCount] = useState(0);
  const [playing, setPlaying] = useState(true);

  const totalEvents = events.length;
  const tickMs = totalEvents > 0
    ? Math.max(28, Math.min(110, Math.floor(9000 / totalEvents)))
    : 80;

  useEffect(() => {
    setVisibleEventCount(0);
    setPlaying(true);
  }, [analysisId]);

  useEffect(() => {
    if (!playing || visibleEventCount >= totalEvents || totalEvents === 0) {
      return;
    }

    const timer = window.setTimeout(() => {
      setVisibleEventCount((current) => Math.min(current + 1, totalEvents));
    }, tickMs);

    return () => window.clearTimeout(timer);
  }, [playing, tickMs, totalEvents, visibleEventCount]);

  useEffect(() => {
    if (visibleEventCount >= totalEvents && totalEvents > 0) {
      setPlaying(false);
    }
  }, [totalEvents, visibleEventCount]);

  const visibleGraph = useMemo(
    () => buildVisibleGraph(graph, events, visibleEventCount),
    [events, graph, visibleEventCount],
  );

  const sharedInfrastructure = useMemo(
    () => buildSharedInfrastructure(visibleGraph),
    [visibleGraph],
  );

  const suspiciousNeighbors = useMemo(() => {
    const neighbors = new Set<string>();
    for (const edge of visibleGraph.edges) {
      if (sharedInfrastructure.has(edge.source)) {
        neighbors.add(edge.target);
      }
      if (sharedInfrastructure.has(edge.target)) {
        neighbors.add(edge.source);
      }
    }
    return neighbors;
  }, [sharedInfrastructure, visibleGraph.edges]);

  const currentEvent = visibleEventCount > 0
    ? events[Math.min(visibleEventCount - 1, totalEvents - 1)]
    : null;

  const red = themeValue("--red", "#ff3b30");
  const background = themeValue("--graph-bg", "#050505");
  const foreground = themeValue("--graph-fg", "#f4f4f0");

  function restart() {
    setVisibleEventCount(0);
    setPlaying(true);
  }

  function showFinal() {
    setVisibleEventCount(totalEvents);
    setPlaying(false);
    window.setTimeout(() => graphRef.current?.zoomToFit(650, 70), 80);
  }

  return (
    <section className="dataset-playback">
      <header className="dataset-playback-head">
        <div>
          <span>[ TRANSACTION STREAM PLAYBACK ]</span>
          <strong>
            {visibleEventCount.toLocaleString()} / {totalEvents.toLocaleString()} PAYMENTS
          </strong>
        </div>
        <div className="dataset-playback-stats">
          <span>{visibleGraph.nodes.length.toLocaleString()} NODES</span>
          <span>{visibleGraph.edges.length.toLocaleString()} EDGES</span>
          <span>{sharedInfrastructure.size} SHARED INFRA</span>
        </div>
        <div className="dataset-playback-controls">
          <button type="button" onClick={() => setPlaying((value) => !value)}>
            {playing ? "PAUSE" : visibleEventCount >= totalEvents ? "PLAY AGAIN" : "RESUME"}
          </button>
          <button type="button" onClick={restart}>RESTART</button>
          <button type="button" onClick={showFinal}>SHOW FINAL</button>
        </div>
      </header>

      <div className="dataset-playback-progress" aria-hidden="true">
        <span
          style={{
            width: totalEvents === 0
              ? "0%"
              : `${(visibleEventCount / totalEvents) * 100}%`,
          }}
        />
      </div>

      <div className="dataset-playback-canvas">
        {visibleGraph.nodes.length === 0 ? (
          <div className="dataset-playback-empty">
            <strong>STREAM INITIALIZING</strong>
            <span>Waiting for the first transaction event…</span>
          </div>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={{
              nodes: visibleGraph.nodes.map((node) => ({ ...node })),
              links: visibleGraph.edges.map((edge) => ({ ...edge })),
            }}
            backgroundColor={background}
            warmupTicks={18}
            cooldownTicks={70}
            d3AlphaDecay={0.045}
            d3VelocityDecay={0.36}
            nodeRelSize={4}
            linkColor={(rawLink) => {
              const link = rawLink as RenderLink;
              return sharedInfrastructure.has(endpointId(link.source)) ||
                sharedInfrastructure.has(endpointId(link.target))
                ? red
                : "rgba(244,244,240,0.12)";
            }}
            linkWidth={(rawLink) => {
              const link = rawLink as RenderLink;
              return sharedInfrastructure.has(endpointId(link.source)) ||
                sharedInfrastructure.has(endpointId(link.target))
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
              const nodeType = String(node.attributes.node_type ?? "entity");
              const isShared = sharedInfrastructure.has(node.id);
              const isContext = suspiciousNeighbors.has(node.id);
              const radius = nodeRadius(nodeType, isShared);
              const x = node.x ?? 0;
              const y = node.y ?? 0;

              context.beginPath();
              context.arc(x, y, radius, 0, Math.PI * 2);
              context.fillStyle = isShared
                ? red
                : isContext
                  ? foreground
                  : "rgba(244,244,240,0.30)";
              context.fill();

              if (isShared) {
                context.strokeStyle = red;
                context.lineWidth = 1;
                context.beginPath();
                context.arc(x, y, radius + 3, 0, Math.PI * 2);
                context.stroke();
              }

              if (isShared && (sharedInfrastructure.size <= 10 || globalScale > 2.4)) {
                const label = nodeType === "device" ? "SHARED DEVICE" : "SHARED IP";
                const fontSize = Math.max(3.2, 10 / globalScale);
                context.font = `800 ${fontSize}px \"JetBrains Mono\", Consolas, monospace`;
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
              const nodeType = String(node.attributes.node_type ?? "entity");
              const entityId = String(node.attributes.entity_id ?? node.id);
              const status = sharedInfrastructure.has(node.id)
                ? "SHARED ACROSS MULTIPLE CUSTOMERS"
                : "OBSERVED ENTITY";
              return `${entityId}\nTYPE: ${nodeType}\n${status}`;
            }}
          />
        )}

        <div className="dataset-playback-event">
          <span>{playing ? "● LIVE PLAYBACK" : "○ PLAYBACK PAUSED"}</span>
          <strong>{currentEvent?.transaction_id ?? "WAITING FOR TX"}</strong>
          <small>
            {currentEvent
              ? `${currentEvent.entities.length} entities · amount ${currentEvent.amount.toFixed(2)}${currentEvent.label === null ? "" : ` · label ${currentEvent.label}`}`
              : "Transactions will appear in original dataset order."}
          </small>
        </div>

        <div className="dataset-playback-legend">
          <span><i className="shared" /> SHARED DEVICE / IP</span>
          <span><i className="context" /> CONNECTED ENTITY</span>
          <span><i /> ORDINARY CONTEXT</span>
        </div>
      </div>
    </section>
  );
}
