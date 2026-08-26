const API_BASE =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";

export interface FrameStats {
  transactions_scored: number;
  allowed: number;
  reviewed: number;
  blocked: number;
  average_risk_score: number;
  graph_nodes: number;
  graph_edges: number;
}

export interface RecentRiskResult {
  transaction_id: string;
  risk_score: number;
  action: "ALLOW" | "REVIEW" | "BLOCK";
  evidence_count: number;
}

export async function getStats(): Promise<FrameStats> {
  const response = await fetch(
    `${API_BASE}/api/v1/stats`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load FRAME statistics",
    );
  }

  return response.json();
}

export async function getRecentRiskResults(): Promise<
  RecentRiskResult[]
> {
  const response = await fetch(
    `${API_BASE}/api/v1/risk/recent?limit=20`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load recent risk decisions",
    );
  }

  return response.json();
}

export interface GraphNode {
  id: string;
  attributes: {
    node_type?: string;
    entity_id?: string;
    [key: string]: unknown;
  };
}

export interface GraphEdge {
  source: string;
  target: string;
  attributes: {
    relation?: string;
    [key: string]: unknown;
  };
}

export interface GraphSnapshot {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export async function getGraph(): Promise<GraphSnapshot> {
  const response = await fetch(
    `${API_BASE}/api/v1/graph`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load payment graph",
    );
  }

  return response.json();
}