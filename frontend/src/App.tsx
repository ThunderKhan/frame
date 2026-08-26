import {
  type ReactNode,
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

type Theme =
  | "light"
  | "dark";

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
    useState<FrameStats>(
      EMPTY_STATS,
    );

  const [recent, setRecent] =
    useState<
      RecentRiskResult[]
    >([]);

  const [graph, setGraph] =
    useState<GraphSnapshot>({
      nodes: [],
      edges: [],
    });

  const [online, setOnline] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [theme, setTheme] =
    useState<Theme>(() => {
      const saved =
        window.localStorage.getItem(
          "frame-theme",
        );

      if (
        saved === "light" ||
        saved === "dark"
      ) {
        return saved;
      }

      return window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches
        ? "dark"
        : "light";
    });

  const appRef =
    useRef<HTMLElement | null>(
      null,
    );

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme,
    );

    window.localStorage.setItem(
      "frame-theme",
      theme,
    );
  }, [theme]);

  useEffect(() => {
    /*
     * Older versions of the hero CTA used href="#story".
     * Clear that stale fragment without changing scroll position.
     */
    if (
      window.location.hash ===
      "#story"
    ) {
      window.history.replaceState(
        null,
        "",
        `${window.location.pathname}${window.location.search}`,
      );
    }
  }, []);

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
      window.clearInterval(
        interval,
      );
    };
  }, []);

  useEffect(() => {
    const root =
      appRef.current;

    if (!root) {
      return;
    }

    const reducedMotion =
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

    const revealElements =
      Array.from(
        root.querySelectorAll<HTMLElement>(
          "[data-reveal]",
        ),
      );

    let animationFrame = 0;

    let currentScroll =
      window.scrollY;

    let targetScroll =
      window.scrollY;

    const update = () => {
      targetScroll =
        window.scrollY;

      currentScroll +=
        (
          targetScroll -
          currentScroll
        ) *
        0.09;

      root.style.setProperty(
        "--scroll-y",
        `${currentScroll}`,
      );

      if (!reducedMotion) {
        const viewportHeight =
          window.innerHeight;

        revealElements.forEach(
          (element) => {
            const rect =
              element.getBoundingClientRect();

            const viewportCenter =
              viewportHeight /
              2;

            const elementCenter =
              rect.top +
              rect.height /
                2;

            const distance =
              Math.abs(
                elementCenter -
                  viewportCenter,
              );

            const maxDistance =
              viewportHeight *
              0.75;

            const progress =
              Math.max(
                0,
                Math.min(
                  1,
                  1 -
                    distance /
                      maxDistance,
                ),
              );

            element.style.setProperty(
              "--reveal",
              progress.toFixed(
                4,
              ),
            );

            const direction =
              rect.top <
              viewportCenter
                ? -1
                : 1;

            element.style.setProperty(
              "--reveal-direction",
              `${direction}`,
            );
          },
        );
      }

      animationFrame =
        window.requestAnimationFrame(
          update,
        );
    };

    animationFrame =
      window.requestAnimationFrame(
        update,
      );

    return () => {
      window.cancelAnimationFrame(
        animationFrame,
      );
    };
  }, []);

  function scrollToStory() {
    const story =
      document.getElementById(
        "story",
      );

    if (!story) {
      return;
    }

    const reducedMotion =
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

    story.scrollIntoView({
      behavior:
        reducedMotion
          ? "auto"
          : "smooth",
      block: "start",
    });
  }

  const latestDecision =
    recent.length > 0
      ? recent[
          recent.length - 1
        ]
      : null;

  const activeRisk =
    latestDecision
      ? latestDecision.risk_score
      : stats.average_risk_score;

  const activeAction =
    latestDecision?.action ??
    "SCAN";

  const activeEvidence =
    latestDecision
      ?.evidence_count ?? 0;

  const watchlistCount =
    stats.reviewed +
    stats.blocked;

  const activeClusterId =
    `RING_${String(
      Math.max(
        1,
        watchlistCount,
      ),
    ).padStart(
      2,
      "0",
    )}`;

  const heroFigure =
    activeRisk > 0
      ? activeRisk.toFixed(3)
      : "0.000";

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

        <div className="register-control">
          <span
            className={
              online
                ? "engine-state is-online"
                : "engine-state is-offline"
            }
          >
            [
            {online
              ? " ENGINE ONLINE "
              : " ENGINE OFFLINE "}
            ]
          </span>

          <button
            className="theme-toggle"
            type="button"
            aria-label={`Current theme is ${theme}. Switch to ${
              theme === "light"
                ? "dark"
                : "light"
            } mode`}
            onClick={() => {
              setTheme(
                theme === "light"
                  ? "dark"
                  : "light",
              );
            }}
          >
            {theme === "light"
              ? "[ LIGHT → DARK ]"
              : "[ DARK → LIGHT ]"}
          </button>
        </div>
      </div>

      <section className="hero-section">
        <div className="hero-noise">
          {heroFigure}
        </div>

        <div className="hero-copy">
          <p className="micro-label">
            [
            {" "}
            COORDINATED
            PAYMENT ABUSE
            {" "}
            ]
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

          <button
            className="hero-action"
            type="button"
            onClick={
              scrollToStory
            }
          >
            &gt;&gt;&gt; SEE HOW
            FRAME WORKS
          </button>
        </div>

        <aside className="hero-forensics">
          <div className="hero-board glass-sheet">
            <div className="hero-board-header">
              <p className="micro-label">
                [
                {" "}
                ACTIVE CLUSTER
                {" "}
                ]
              </p>

              <span
                className={`live-flag ${activeAction.toLowerCase()}`}
              >
                {
                  activeClusterId
                }
              </span>
            </div>

            <div className="hero-board-grid">
              <ForensicStat
                label="RISK SCORE"
                value={`${(
                  activeRisk *
                  100
                ).toFixed(
                  1,
                )}%`}
              />

              <ForensicStat
                label="ACTION"
                value={
                  activeAction
                }
              />

              <ForensicStat
                label="EVIDENCE"
                value={formatNumber(
                  activeEvidence,
                )}
              />

              <ForensicStat
                label="NODES"
                value={formatNumber(
                  stats.graph_nodes,
                )}
              />
            </div>

            <div className="hero-diagram-wrap">
              <HeroClusterDiagram />
            </div>

            <div className="hero-board-notes">
              <NoteRow
                label="LAST TX"
                value={
                  latestDecision
                    ?.transaction_id ??
                  "NO TRAFFIC"
                }
              />

              <NoteRow
                label="WATCHLIST"
                value={formatNumber(
                  watchlistCount,
                )}
              />

              <NoteRow
                label="GRAPH"
                value={`${formatNumber(
                  stats.graph_nodes,
                )} / ${formatNumber(
                  stats.graph_edges,
                )}`}
              />
            </div>

            <div className="signal-chip-row">
              <span className="signal-chip">
                &gt;&gt;&gt;
                {" "}
                SHARED DEVICE
              </span>

              <span className="signal-chip">
                /// LINK DENSITY
              </span>

              <span className="signal-chip">
                [ LIVE CASE ]
              </span>
            </div>
          </div>
        </aside>
      </section>

      <section
        className="story-section"
        id="story"
        data-reveal
      >
        <header className="story-header">
          <p className="micro-label">
            [
            {" "}
            HOW FRAME WORKS
            {" "}
            ]
          </p>

          <h2 className="story-title">
            FROM NORMAL-LOOKING
            PAYMENTS TO A
            GRAPH-BASED DECISION
          </h2>
        </header>

        <div className="story-grid">
          <StoryStep
            number="01"
            title="ISOLATED"
            body="A single payment often looks harmless on its own."
          >
            <div className="story-module">
              <StoryTransactionRow
                txId="TX_1042"
                amount="₹1,840"
                customer="CUST_18"
              />

              <StoryTransactionRow
                txId="TX_1048"
                amount="₹2,160"
                customer="CUST_41"
              />

              <StoryTransactionRow
                txId="TX_1051"
                amount="₹1,920"
                customer="CUST_07"
              />

              <StoryTransactionRow
                txId="TX_1058"
                amount="₹2,240"
                customer="CUST_29"
              />
            </div>
          </StoryStep>

          <StoryStep
            number="02"
            title="CONNECTED"
            body="FRAME links customers, devices and IPs into one relationship graph."
          >
            <div className="story-module">
              <StoryLine
                label="SHARED DEVICE"
                value="DEVICE_17"
              />

              <StoryLine
                label="SHARED IP"
                value="IP_302"
              />

              <StoryLine
                label="GRAPH NODES"
                value={formatNumber(
                  stats.graph_nodes,
                )}
              />

              <StoryLine
                label="GRAPH EDGES"
                value={formatNumber(
                  stats.graph_edges,
                )}
              />
            </div>
          </StoryStep>

          <StoryStep
            number="03"
            title="SIGNAL"
            body="Graph structure and temporal evidence become features for online risk scoring."
          >
            <div className="story-module">
              <StoryLine
                label="AVG RISK"
                value={`${(
                  stats.average_risk_score *
                  100
                ).toFixed(
                  1,
                )}%`}
              />

              <StoryLine
                label="WATCHLIST"
                value={formatNumber(
                  watchlistCount,
                )}
              />

              <StoryLine
                label="EVIDENCE"
                value={formatNumber(
                  activeEvidence,
                )}
              />

              <StoryLine
                label="MODEL"
                value="FRAME-V1"
              />
            </div>
          </StoryStep>

          <StoryStep
            number="04"
            title="DECISION"
            body="Deterministic policy converts the model score into ALLOW, REVIEW or BLOCK."
          >
            <div className="decision-module">
              <div className="decision-score">
                {(
                  activeRisk *
                  100
                ).toFixed(
                  1,
                )}
                %
              </div>

              <div className="decision-action-large">
                {
                  activeAction
                }
              </div>

              <div className="policy-note">
                <span>
                  REVIEW ≥
                  0.020
                </span>

                <span>
                  BLOCK ≥
                  0.700
                </span>
              </div>
            </div>
          </StoryStep>
        </div>
      </section>

      <section
        className="manifest-section"
        data-reveal
      >
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
        data-reveal
      >
        <header className="section-heading">
          <div>
            <p className="micro-label">
              [
              {" "}
              NETWORK / 01
              {" "}
              ]
            </p>

            <h2>
              PAYMENT
              <br />
              RELATIONSHIP
              <br />
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
              [
              {" "}
              ACTIVE NETWORK
              {" "}
              ]
            </p>

            <strong>
              {
                stats.graph_nodes
              }
            </strong>

            <span>
              ENTITIES
              OBSERVED
            </span>
          </div>
        </div>
      </section>

      <section
        className="operations-grid"
        data-reveal
      >
        <article className="ledger-panel">
          <header className="panel-header">
            <span>
              [
              {" "}
              LIVE DECISIONS /
              02
              {" "}
              ]
            </span>

            <span>
              {
                recent.length
              }
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
              {" "}
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
              [
              {" "}
              SIGNAL INDEX /
              03
              {" "}
              ]
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
            value={`${(
              stats.average_risk_score *
              100
            ).toFixed(
              1,
            )}%`}
          />

          {latestDecision && (
            <div className="active-signal glass-sheet">
              <p>
                [
                {" "}
                LATEST DECISION
                {" "}
                ]
              </p>

              <strong>
                {
                  latestDecision.transaction_id
                }
              </strong>

              <span>
                &gt;&gt;&gt;
                {" "}
                {
                  latestDecision.action
                }
              </span>
            </div>
          )}
        </aside>
      </section>

      <footer
        className="colophon"
        data-reveal
      >
        <div>
          FRAME™ ///
          <br />
          FRAUD RING
          ANALYSIS &amp;
          MAPPING ENGINE
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
          {online
            ? "LIVE"
            : "OFFLINE"}
        </div>
      </footer>
    </main>
  );
}

interface ForensicStatProps {
  label: string;
  value: string;
}

function ForensicStat({
  label,
  value,
}: ForensicStatProps) {
  return (
    <div className="forensic-stat">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}

interface NoteRowProps {
  label: string;
  value: string;
}

function NoteRow({
  label,
  value,
}: NoteRowProps) {
  return (
    <div className="note-row">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}

interface StoryStepProps {
  number: string;
  title: string;
  body: string;
  children: ReactNode;
}

function StoryStep({
  number,
  title,
  body,
  children,
}: StoryStepProps) {
  return (
    <article className="story-card">
      <div className="story-card-head">
        <span className="story-number">
          {number}
        </span>

        <h3>
          {title}
        </h3>
      </div>

      <p className="story-body">
        {body}
      </p>

      {children}
    </article>
  );
}

interface StoryTransactionRowProps {
  txId: string;
  amount: string;
  customer: string;
}

function StoryTransactionRow({
  txId,
  amount,
  customer,
}: StoryTransactionRowProps) {
  return (
    <div className="story-tx-row">
      <span>
        {txId}
      </span>

      <span>
        {amount}
      </span>

      <span>
        {customer}
      </span>

      <strong>
        NORMAL
      </strong>
    </div>
  );
}

interface StoryLineProps {
  label: string;
  value: string;
}

function StoryLine({
  label,
  value,
}: StoryLineProps) {
  return (
    <div className="story-line">
      <span>
        {label}
      </span>

      <strong>
        {value}
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
        ).toFixed(
          1,
        )}
        %
      </span>

      <span>
        {
          result.evidence_count
        }
        {" "}
        SIG
      </span>

      <strong
        className={`decision-action ${result.action.toLowerCase()}`}
      >
        [
        {
          result.action
        }
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
          ? formatNumber(
              value,
            )
          : value}
      </strong>
    </div>
  );
}

function HeroClusterDiagram() {
  return (
    <svg
      className="hero-diagram"
      viewBox="0 0 420 260"
      role="img"
      aria-label="Example coordinated payment relationship cluster"
    >
      <line
        className="edge edge-core"
        x1="210"
        y1="126"
        x2="104"
        y2="70"
      />

      <line
        className="edge edge-core"
        x1="210"
        y1="126"
        x2="314"
        y2="70"
      />

      <line
        className="edge edge-core"
        x1="210"
        y1="126"
        x2="116"
        y2="196"
      />

      <line
        className="edge edge-alert"
        x1="210"
        y1="126"
        x2="304"
        y2="194"
      />

      <line
        className="edge edge-bridge"
        x1="304"
        y1="194"
        x2="360"
        y2="124"
      />

      <circle
        className="node customer"
        cx="104"
        cy="70"
        r="20"
      />

      <circle
        className="node customer"
        cx="314"
        cy="70"
        r="20"
      />

      <circle
        className="node customer"
        cx="116"
        cy="196"
        r="20"
      />

      <circle
        className="node customer"
        cx="304"
        cy="194"
        r="20"
      />

      <circle
        className="node device"
        cx="210"
        cy="126"
        r="29"
      />

      <circle
        className="node ip"
        cx="360"
        cy="124"
        r="17"
      />

      <text
        className="diagram-label"
        x="78"
        y="38"
      >
        CUST_A
      </text>

      <text
        className="diagram-label"
        x="288"
        y="38"
      >
        CUST_B
      </text>

      <text
        className="diagram-label"
        x="91"
        y="232"
      >
        CUST_C
      </text>

      <text
        className="diagram-label"
        x="278"
        y="232"
      >
        CUST_D
      </text>

      <text
        className="diagram-callout"
        x="160"
        y="88"
      >
        SHARED DEVICE
      </text>

      <text
        className="diagram-core"
        x="210"
        y="126"
        textAnchor="middle"
        dominantBaseline="middle"
      >
        DEV
      </text>

      <text
        className="diagram-label"
        x="331"
        y="94"
      >
        SHARED IP
      </text>
    </svg>
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
      }).map(
        (
          _,
          index,
        ) => (
          <div
            className="decision-row skeleton-row"
            key={
              index
            }
          >
            <span />
            <span />
            <span />
            <span />
          </div>
        ),
      )}
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