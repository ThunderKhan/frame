import {
  useEffect,
  useState,
} from "react";

import {
  type FrameStats,
  type GraphSnapshot,
  type RecentRiskResult,
  getGraph,
  getRecentRiskResults,
  getStats,
} from "./api";

import {
  PaymentGraph,
} from "./PaymentGraph";

import "./DemoPage.css";

type Theme =
  | "light"
  | "dark";

const THEME_STORAGE_KEY =
  "frame-theme";

const EMPTY_STATS: FrameStats = {
  transactions_scored: 0,
  allowed: 0,
  reviewed: 0,
  blocked: 0,
  average_risk_score: 0,
  graph_nodes: 0,
  graph_edges: 0,
};

function initialTheme(): Theme {
  try {
    const saved =
      window.localStorage.getItem(
        THEME_STORAGE_KEY,
      );

    if (
      saved === "light" ||
      saved === "dark"
    ) {
      return saved;
    }
  } catch {
    // Fall back to the operating-system preference when storage is unavailable.
  }

  return window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches
    ? "dark"
    : "light";
}

function formatNumber(value: number) {
  return String(value).padStart(5, "0");
}

export function DemoPage() {
  const [stats, setStats] =
    useState<FrameStats>(EMPTY_STATS);

  const [graph, setGraph] =
    useState<GraphSnapshot>({
      nodes: [],
      edges: [],
    });

  const [recent, setRecent] =
    useState<RecentRiskResult[]>([]);

  const [online, setOnline] =
    useState(false);

  const [theme, setTheme] =
    useState<Theme>(initialTheme);

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme,
    );

    try {
      window.localStorage.setItem(
        THEME_STORAGE_KEY,
        theme,
      );
    } catch {
      // Theme application should not depend on persistent storage.
    }
  }, [theme]);

  useEffect(() => {
    document.title =
      "FRAME Demo — Live Fraud Ring Console";

    async function refresh() {
      try {
        const [nextStats, nextGraph, nextRecent] =
          await Promise.all([
            getStats(),
            getGraph(),
            getRecentRiskResults(),
          ]);

        setStats(nextStats);
        setGraph(nextGraph);
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

    return () =>
      window.clearInterval(interval);
  }, []);

  return (
    <main className="demo-shell">
      <header className="demo-nav">
        <a className="demo-brand" href="/">
          FRAME /// LIVE DEMO
        </a>

        <nav aria-label="Demo navigation">
          <a href="/">HOME</a>
          <a href="#network">NETWORK</a>
          <a href="#decisions">DECISIONS</a>
          <a href="/docs/">DOCS</a>
          <a
            href="https://github.com/ThunderKhan/frame"
            target="_blank"
            rel="noreferrer"
          >
            GITHUB ↗
          </a>
        </nav>

        <div className="demo-controls">
          <span
            className={
              online
                ? "demo-engine is-online"
                : "demo-engine is-offline"
            }
          >
            [ ENGINE {online ? "ONLINE" : "OFFLINE"} ]
          </span>

          <button
            className="theme-toggle demo-theme-toggle"
            type="button"
            aria-label={`Current theme is ${theme}. Switch to ${
              theme === "light"
                ? "dark"
                : "light"
            } mode`}
            onClick={() =>
              setTheme(
                theme === "light"
                  ? "dark"
                  : "light",
              )
            }
          >
            {theme === "light"
              ? "[ LIGHT → DARK ]"
              : "[ DARK → LIGHT ]"}
          </button>
        </div>
      </header>

      <section className="demo-intro">
        <div>
          <p>[ OPERATIONAL CONSOLE / 001 ]</p>
          <h1>
            LIVE FRAUD
            <br />
            RING DEMO
          </h1>
        </div>

        <div className="demo-stat-grid">
          <div>
            <span>TRANSACTIONS</span>
            <strong>{formatNumber(stats.transactions_scored)}</strong>
          </div>
          <div>
            <span>REVIEW</span>
            <strong>{formatNumber(stats.reviewed)}</strong>
          </div>
          <div>
            <span>BLOCK</span>
            <strong>{formatNumber(stats.blocked)}</strong>
          </div>
          <div>
            <span>AVG RISK</span>
            <strong>
              {(stats.average_risk_score * 100).toFixed(1)}%
            </strong>
          </div>
        </div>
      </section>

      <section className="demo-network" id="network">
        <header className="demo-section-head">
          <div>
            <p>[ NETWORK / 01 ]</p>
            <h2>PAYMENT RELATIONSHIP GRAPH</h2>
          </div>

          <div className="demo-network-meta">
            <span>NODES {formatNumber(stats.graph_nodes)}</span>
            <span>EDGES {formatNumber(stats.graph_edges)}</span>
            <span>/// LIVE</span>
          </div>
        </header>

        <div className="demo-graph-frame">
          <PaymentGraph graph={graph} />
        </div>
      </section>

      <section className="demo-decisions" id="decisions">
        <header className="demo-section-head compact">
          <div>
            <p>[ LIVE DECISIONS / 02 ]</p>
            <h2>TRANSACTION DECISIONS</h2>
          </div>

          <span>{recent.length} ENTRIES</span>
        </header>

        <div className="demo-decision-grid">
          <div className="demo-decision-list">
            {recent.length === 0 ? (
              <div className="demo-empty">
                &gt;&gt;&gt; WAITING FOR TRANSACTIONS
              </div>
            ) : (
              [...recent].reverse().map((item) => (
                <button
                  className="decision-row demo-decision-row"
                  type="button"
                  key={item.transaction_id}
                >
                  <span className="decision-id">
                    {item.transaction_id}
                  </span>

                  <span>
                    {(item.risk_score * 100).toFixed(1)}%
                  </span>

                  <span
                    className={`decision-action ${item.action.toLowerCase()}`}
                  >
                    [ {item.action} ]
                  </span>

                  <span>
                    {String(item.evidence_count).padStart(2, "0")} SIGNALS
                  </span>
                </button>
              ))
            )}
          </div>

          <aside className="demo-signal-index">
            <div><span>REVIEW</span><strong>{formatNumber(stats.reviewed)}</strong></div>
            <div><span>BLOCK</span><strong>{formatNumber(stats.blocked)}</strong></div>
            <div><span>ALLOW</span><strong>{formatNumber(stats.allowed)}</strong></div>
            <div><span>AVG RISK</span><strong>{(stats.average_risk_score * 100).toFixed(1)}%</strong></div>
          </aside>
        </div>
      </section>

      <footer className="demo-footer">
        <span>FRAME™ /// FRAUD RING ANALYSIS &amp; MAPPING ENGINE</span>
        <span>MODEL: FRAME-ONLINE-V1</span>
        <span>POLICY: REVIEW ≥ 0.020 /// BLOCK ≥ 0.700</span>
        <a href="/">← BACK TO FRAME</a>
      </footer>
    </main>
  );
}
