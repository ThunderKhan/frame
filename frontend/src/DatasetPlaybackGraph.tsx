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

import "./DatasetPlaybackGraph.css";

export interface DatasetStreamEvent {
  transaction_id: string;
  row: number;
  amount: number;
  label: number | null;
  entities: string[];
  risk_score?: number;
  action?: "ALLOW" | "REVIEW" | "BLOCK";
  evidence_count?: number;
}

interface DatasetPlaybackGraphProps {
  graph: GraphSnapshot;
  events: DatasetStreamEvent[];
}

interface RenderNode extends GraphNode {
  x?: number;
  y?: number;
}

interface RenderLink {
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

function nodeTypeMap(graph: GraphSnapshot): Map<string, string> {
  return new Map(
    graph.nodes.map((node) => [
      node.id,
      String(node.attributes.node_type ?? "entity"),
    ]),
  );
}

function buildSharedInfrastructure(graph: GraphSnapshot): Set<string> {
  const nodeTypes = nodeTypeMap(graph);
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

function isSharedCustomerLink(
  rawLink: RenderLink,
  sharedInfrastructure: Set<string>,
  nodeTypes: Map<string, string>,
): boolean {
  const source = endpointId(rawLink.source);
  const target = endpointId(rawLink.target);

  return (
    sharedInfrastructure.has(source) && nodeTypes.get(target) === "customer"
  ) || (
    sharedInfrastructure.has(target) && nodeTypes.get(source) === "customer"
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
}: DatasetPlaybackGraphProps) {
  const graphRef = useRef<ForceGraphMethods | undefined>(undefined);
  const [visibleEventCount, setVisibleEventCount] = useState(0);
  const [playing, setPlaying] = useState(true);

  const totalEvents = events.length;
  const tickMs = totalEvents > 0
    ? Math.max(28, Math.min(110, Math.floor(9000 / totalEvents)))
    : 80;

  const currentEvent = visibleEventCount > 0
    ? events[Math.min(visibleEventCount - 1, totalEvents - 1)]
    : null;

  const currentDelay = currentEvent?.action === "REVIEW" || currentEvent?.action === "BLOCK"
    ? 650
    : tickMs;

  useEffect(() => {
    if (!playing || visibleEventCount >= totalEvents || totalEvents === 0) {
      return;
    }

    const timer = window.setTimeout(() => {
      const next = Math.min(visibleEventCount + 1, totalEvents);
      setVisibleEventCount(next);
      if (next >= totalEvents) {
        setPlaying(false);
      }
    }, currentDelay);

    return () => window.clearTimeout(timer);
  }, [currentDelay, playing, totalEvents, visibleEventCount]);

  useEffect(() => {
    if (visibleEventCount === 0 || visibleEventCount % 24 !== 0) {
      return;
    }

    const timer = window.setTimeout(
      () => graphRef.current?.zoomToFit(260, 62),
      40,
    );
    return () => window.clearTimeout(timer);
  }, [visibleEventCount]);

  const visibleGraph = useMemo(
    () => buildVisibleGraph(graph, events, visibleEventCount),
    [events, graph, visibleEventCount],
  );

  const nodeTypes = useMemo(
    () => nodeTypeMap(visibleGraph),
    [visibleGraph],
  );

  const sharedInfrastructure = useMemo(
    () => buildSharedInfrastructure(visibleGraph),
    [visibleGraph],
  );

  const suspiciousNeighbors = useMemo(() => {
    const neighbors = new Set<string>();

    for (const edge of visibleGraph.edges) {
      const sourceType = nodeTypes.get(edge.source);
      const targetType = nodeTypes.get(edge.target);

      if (sharedInfrastructure.has(edge.source) && targetType === "customer") {
        neighbors.add(edge.target);
      }

      if (sharedInfrastructure.has(edge.target) && sourceType === "customer") {
        neighbors.add(edge.source);
      }
    }

    return neighbors;
  }, [nodeTypes, sharedInfrastructure, visibleGraph.edges]);

  const latestPolicyAlert = useMemo(
    () => events
      .slice(0, visibleEventCount)
      .filter((event) => event.action === "REVIEW" || event.action === "BLOCK")
      .at(-1) ?? null,
    [events, visibleEventCount],
  );

  const red = themeValue("--red", "#ff3b30");
  const background = themeValue("--graph-bg", "#050505");
  const foreground = themeValue("--graph-fg", "#f4f4f0");

  function restart() {
    setVisibleEventCount(0);
    setPlaying(true);
  }

  function togglePlayback() {
    if (visibleEventCount >= totalEvents) {
      restart();
      return;
    }
    setPlaying((value) => !value);
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
          <button type="button" onClick={togglePlayback}>
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
            linkColor={(rawLink) =>
              isSharedCustomerLink(
                rawLink as RenderLink,
                sharedInfrastructure,
                nodeTypes,
              )
                ? red
                : "rgba(244,244,240,0.10)"
            }
            linkWidth={(rawLink) =>
              isSharedCustomerLink(
                rawLink as RenderLink,
                sharedInfrastructure,
                nodeTypes,
              )
                ? 2.1
                : 0.35
            }
            linkDirectionalParticles={(rawLink) =>
              isSharedCustomerLink(
                rawLink as RenderLink,
                sharedInfrastructure,
                nodeTypes,
              )
                ? 1
                : 0
            }
            linkDirectionalParticleWidth={1.3}
            linkDirectionalParticleColor={() => red}
            nodeCanvasObject={(rawNode, context, globalScale) => {
              const node = rawNode as RenderNode;
              const type = String(node.attributes.node_type ?? "entity");
              const isShared = sharedInfrastructure.has(node.id);
              const isContext = suspiciousNeighbors.has(node.id);
              const radius = nodeRadius(type, isShared);
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
                const label = type === "device" ? "SHARED DEVICE" : "SHARED IP";
                const fontSize = Math.max(3.2, 10 / globalScale);
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
              const type = String(node.attributes.node_type ?? "entity");
              const entityId = String(node.attributes.entity_id ?? node.id);
              const status = sharedInfrastructure.has(node.id)
                ? "SHARED ACROSS MULTIPLE CUSTOMERS"
                : "OBSERVED ENTITY";
              return `${entityId}\nTYPE: ${type}\n${status}`;
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

        {latestPolicyAlert && (
          <div
            className={`dataset-policy-alert is-${latestPolicyAlert.action?.toLowerCase()}`}
          >
            <span>[ FRAME-ONLINE-V1 POLICY ALERT ]</span>
            <strong>
              {latestPolicyAlert.action} /// {((latestPolicyAlert.risk_score ?? 0) * 100).toFixed(1)}% RISK
            </strong>
            <small>
              {latestPolicyAlert.transaction_id} · {latestPolicyAlert.evidence_count ?? 0} OBSERVED SIGNALS
            </small>
          </div>
        )}

        <div className="dataset-playback-legend">
          <span><i className="shared" /> SHARED DEVICE / IP</span>
          <span><i className="context" /> CONNECTED CUSTOMER</span>
          <span><i /> ORDINARY CONTEXT</span>
        </div>
      </div>
    </section>
  );
}
