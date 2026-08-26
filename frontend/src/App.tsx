import {
  useEffect,
  useRef,
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

import { PaymentGraph } from "./PaymentGraph";

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

  const [graph, setGraph] =
    useState<GraphSnapshot>({
      nodes: [],
      edges: [],
    });

  const [online, setOnline] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const appRef =
    useRef<HTMLElement | null>(null);

  useEffect(() => {
    async function refresh() {
      try {
        const [
          nextStats,
          nextRecent,
          nextGraph,
        ] = await Promise.all([
          getStats(),
          getRecentRiskResults(),
          getGraph(),
        ]);

        setStats(nextStats);
        setRecent(nextRecent);
        setGraph(nextGraph);

        setOnline(true);
      } catch {
        setOnline(false);
      } finally {
        setLoading(false);
      }
    }

    void refresh();

    const interval =
      window.setInterval(
        () => void refresh(),
        2000,
      );

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    const root = appRef.current;

    if (!root) {
      return;
    }

    let frame = 0;
    let currentScroll =
      window.scrollY;
    let targetScroll =
      window.scrollY;

    const update =
      () => {
        targetScroll =
          window.scrollY;

        currentScroll +=
          (targetScroll -
            currentScroll) *
          0.08;

        root.style.setProperty(
          "--scroll-y",
          `${currentScroll}`,
        );

        frame =
          window.requestAnimationFrame(
            update,
          );
      };

    frame =
      window.requestAnimationFrame(
        update,
      );

    return () => {
      window.cancelAnimationFrame(
        frame,
      );
    };
  }, []);

  const latestDecision =
    recent.length > 0
      ? recent[
          recent.length - 1
        ]
      : null;

  return (
    <main
      className="app-shell"
      ref={appRef}
    >
      <div className="register-strip">
        <span>
          FRAME ///
          FRAUD RING ANALYSIS
          &amp; MAPPING ENGINE
        </span>

        <span>
          ISSUE 001
        </span>

        <span>
          MODEL FRAME-ONLINE-V1
        </span>

        <span>
          [
          {online
            ? " ENGINE ONLINE "
            : " ENGINE OFFLINE "}
          ]
        </span>
      </div>

      <section className="hero-section">
        <div className="hero-noise">
          /// 05
        </div>

        <div className="hero-copy">
          <p className="micro-label">
            [ COORDINATED
            PAYMENT ABUSE ]
          </p>

          <h1 className="hero-title">
            FRAUD
            <br />
            RING
            <br />
            INTELLIGENCE
          </h1>

          <p className="hero-summary">
            Individual payments
            can look normal.
            <br />
            Coordinated abuse
            does not.
          </p>

          <a
            className="hero-action"
            href="#network"
          >
            &gt;&gt;&gt; ENTER
            NETWORK
          </a>
        </div>

        <aside className="hero-meta glass-sheet">
          <MetaRow
            label="TX SCORED"
            value={
              stats.transactions_scored
            }
          />

          <MetaRow
            label="REVIEW"
            value={
              stats.reviewed
            }
          />

          <MetaRow
            label="BLOCK"
            value={
              stats.blocked
            }
          />

          <MetaRow
            label="NODES"
            value={
              stats.graph_nodes
            }
          />

          <div className="hero-status-line">
            <span>
              &gt;&gt;&gt;
            </span>

            <span>
              {online
                ? "SYSTEM ACTIVE"
                : "SYSTEM UNAVAILABLE"}
            </span>
          </div>
        </aside>
      </section>

      <section className="manifest-section">
        <div className="section-index">
          [ 00 / THESIS ]
        </div>

        <ManifestRow
          number="01."
          title="SINGLE EVENTS LIE."
          body="A payment can appear legitimate in isolation."
        />

        <ManifestRow
          number="02."
          title="RELATIONSHIPS REVEAL."
          body="Shared devices, IPs and transaction timing expose coordinated structure."
        />

        <ManifestRow
          number="03."
          title="POLICY DECIDES."
          body="Graph and temporal signals produce a calibrated risk score. Deterministic policy converts that score into ALLOW, REVIEW or BLOCK."
        />
      </section>

      <section
        className="network-section"
        id="network"
      >
        <header className="section-heading">
          <div>
            <p className="micro-label">
              [ NETWORK / 01 ]
            </p>

            <h2>
              PAYMENT
              RELATIONSHIP
              GRAPH
            </h2>
          </div>

          <div className="section-meta">
            <span>
              NODES{" "}
              {formatNumber(
                stats.graph_nodes,
              )}
            </span>

            <span>
              EDGES{" "}
              {formatNumber(
                stats.graph_edges,
              )}
            </span>

            <span>
              /// LIVE
            </span>
          </div>
        </header>

        <div className="graph-stage">
          <div className="graph-registration">
            <span>
              + 001
            </span>

            <span>
              FRAME™
            </span>

            <span>
              + NET
            </span>
          </div>

          {loading ? (
            <GraphSkeleton />
          ) : (
            <PaymentGraph
              graph={graph}
            />
          )}

          <div className="floating-status glass-sheet">
            <p>
              [ ACTIVE NETWORK ]
            </p>

            <strong>
              {stats.graph_nodes}
            </strong>

            <span>
              ENTITIES OBSERVED
            </span>
          </div>
        </div>
      </section>

      <section className="operations-grid">
        <article className="ledger-panel">
          <header className="panel-header">
            <span>
              [ LIVE DECISIONS /
              02 ]
            </span>

            <span>
              {recent.length}
              {" "}
              ENTRIES
            </span>
          </header>

          {loading ? (
            <LedgerSkeleton />
          ) : recent.length ===
            0 ? (
            <div className="empty-ledger">
              &gt;&gt;&gt;
              WAITING FOR
              TRANSACTIONS
            </div>
          ) : (
            <div className="ledger">
              {recent
                .slice()
                .reverse()
                .map(
                  (
                    result,
                    index,
                  ) => (
                    <DecisionRow
                      key={`${result.transaction_id}-${index}`}
                      result={
                        result
                      }
                    />
                  ),
                )}
            </div>
          )}
        </article>

        <aside className="signal-panel">
          <header className="panel-header">
            <span>
              [ SIGNAL INDEX /
              03 ]
            </span>

            <span>
              /// OBSERVED
            </span>
          </header>

          <SignalRow
            label="REVIEW"
            value={
              stats.reviewed
            }
          />

          <SignalRow
            label="BLOCK"
            value={
              stats.blocked
            }
          />

          <SignalRow
            label="ALLOW"
            value={
              stats.allowed
            }
          />

          <SignalRow
            label="AVG RISK"
            value={
              `${(
                stats.average_risk_score *
                100
              ).toFixed(1)}%`
            }
          />

          {latestDecision && (
            <div className="active-signal glass-sheet">
              <p>
                [ LATEST
                DECISION ]
              </p>

              <strong>
                {
                  latestDecision.transaction_id
                }
              </strong>

              <span>
                &gt;&gt;&gt;{" "}
                {
                  latestDecision.action
                }
              </span>
            </div>
          )}
        </aside>
      </section>

      <footer className="colophon">
        <div>
          FRAME™ ///
          FRAUD RING ANALYSIS
          &amp; MAPPING ENGINE
        </div>

        <div>
          MODEL:
          FRAME-ONLINE-V1
          <br />
          POLICY:
          REVIEW ≥ 0.020
          <br />
          BLOCK ≥ 0.700
        </div>

        <div>
          SUBSTRATE:
          DIGITAL NEWSPRINT
          <br />
          EDITION:
          BUILDATHON 2026
          <br />
          STATUS:
          {
            online
              ? "LIVE"
              : "OFFLINE"
          }
        </div>
      </footer>
    </main>
  );
}

interface MetaRowProps {
  label: string;
  value: number;
}

function MetaRow({
  label,
  value,
}: MetaRowProps) {
  return (
    <div className="meta-row">
      <span>{label}</span>

      <strong>
        {formatNumber(value)}
      </strong>
    </div>
  );
}

interface ManifestRowProps {
  number: string;
  title: string;
  body: string;
}

function ManifestRow({
  number,
  title,
  body,
}: ManifestRowProps) {
  return (
    <article className="manifest-row">
      <span className="manifest-number">
        {number}
      </span>

      <h3>
        {title}
      </h3>

      <p>
        {body}
      </p>
    </article>
  );
}

interface DecisionRowProps {
  result: RecentRiskResult;
}

function DecisionRow({
  result,
}: DecisionRowProps) {
  return (
    <div className="decision-row">
      <span className="decision-id">
        {
          result.transaction_id
        }
      </span>

      <span>
        {(
          result.risk_score *
          100
        ).toFixed(1)}
        %
      </span>

      <span>
        {result.evidence_count}
        {" "}
        SIG
      </span>

      <strong
        className={`decision-action ${result.action.toLowerCase()}`}
      >
        [
        {result.action}
        ]
      </strong>
    </div>
  );
}

interface SignalRowProps {
  label: string;
  value:
    | number
    | string;
}

function SignalRow({
  label,
  value,
}: SignalRowProps) {
  return (
    <div className="signal-row">
      <span>
        {label}
      </span>

      <strong>
        {typeof value ===
        "number"
          ? formatNumber(value)
          : value}
      </strong>
    </div>
  );
}

function GraphSkeleton() {
  return (
    <div
      className="graph-skeleton"
      aria-label="Loading network graph"
    >
      <span className="skeleton-node node-a" />
      <span className="skeleton-node node-b" />
      <span className="skeleton-node node-c" />
      <span className="skeleton-node node-d" />

      <span className="skeleton-line line-a" />
      <span className="skeleton-line line-b" />
      <span className="skeleton-line line-c" />

      <span className="skeleton-scan" />
    </div>
  );
}

function LedgerSkeleton() {
  return (
    <div className="ledger">
      {Array.from({
        length: 5,
      }).map((_, index) => (
        <div
          className="decision-row skeleton-row"
          key={index}
        >
          <span />
          <span />
          <span />
          <span />
        </div>
      ))}
    </div>
  );
}

function formatNumber(
  value: number,
) {
  return Math.max(
    0,
    value,
  )
    .toString()
    .padStart(
      5,
      "0",
    );
}

export default App;