import { useEffect, useState } from "react";

import {
  type FrameStats,
  type RecentRiskResult,
  getRecentRiskResults,
  getStats,
} from "./api";

import "./App.css";

const EMPTY_STATS: FrameStats = {
  transactions_scored: 0,
  allowed: 0,
  reviewed: 0,
  blocked: 0,
  average_risk_score: 0,
  graph_nodes: 0,
  graph_edges: 0,
};

function App() {
  const [stats, setStats] =
    useState<FrameStats>(EMPTY_STATS);

  const [recent, setRecent] =
    useState<RecentRiskResult[]>([]);

  const [online, setOnline] =
    useState(false);

  useEffect(() => {
    async function refresh() {
      try {
        const [nextStats, nextRecent] =
          await Promise.all([
            getStats(),
            getRecentRiskResults(),
          ]);

        setStats(nextStats);
        setRecent(nextRecent);
        setOnline(true);
      } catch {
        setOnline(false);
      }
    }

    void refresh();

    const interval = window.setInterval(
      () => void refresh(),
      2000,
    );

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  return (
    <main className="app">
      <header className="header">
        <div>
          <p className="eyebrow">FRAME</p>
          <h1>Fraud Risk Command Center</h1>
          <p className="subtitle">
            Explainable graph intelligence for coordinated payment abuse.
          </p>
        </div>

        <div className="status">
          <span
            className={
              online
                ? "status-dot"
                : "status-dot offline"
            }
          />
          {online
            ? "Risk engine online"
            : "Risk engine offline"}
        </div>
      </header>

      <section className="hero-grid">
        <MetricCard
          label="Transactions scored"
          value={stats.transactions_scored}
        />

        <MetricCard
          label="Under review"
          value={stats.reviewed}
        />

        <MetricCard
          label="Blocked"
          value={stats.blocked}
        />

        <MetricCard
          label="Graph entities"
          value={stats.graph_nodes}
        />
      </section>

      <section className="workspace">
        <article className="panel graph-panel">
          <p className="panel-label">
            Network intelligence
          </p>

          <h2>Payment relationship graph</h2>

          <div className="empty-state">
            {stats.graph_nodes} nodes ·{" "}
            {stats.graph_edges} edges
            <br />
            Graph visualization coming next.
          </div>
        </article>

        <article className="panel">
          <p className="panel-label">
            Live decisions
          </p>

          <h2>Recent risk activity</h2>

          <div className="decision-list">
            {recent.length === 0 ? (
              <div className="empty-state">
                Waiting for transactions.
              </div>
            ) : (
              recent
                .slice()
                .reverse()
                .map((result) => (
                  <div
                    className="decision"
                    key={result.transaction_id}
                  >
                    <div>
                      <strong>
                        {result.transaction_id}
                      </strong>

                      <span className="risk-score">
                        Risk{" "}
                        {(
                          result.risk_score * 100
                        ).toFixed(1)}
                        %
                      </span>
                    </div>

                    <span
                      className={`badge ${result.action.toLowerCase()}`}
                    >
                      {result.action}
                    </span>
                  </div>
                ))
            )}
          </div>
        </article>
      </section>
    </main>
  );
}

interface MetricCardProps {
  label: string;
  value: number;
}

function MetricCard({
  label,
  value,
}: MetricCardProps) {
  return (
    <article className="panel">
      <p className="panel-label">
        {label}
      </p>

      <strong className="metric">
        {value.toLocaleString()}
      </strong>
    </article>
  );
}

export default App;