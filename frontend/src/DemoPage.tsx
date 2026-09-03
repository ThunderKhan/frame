import {
  type FormEvent,
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  type FrameStats,
  type GraphSnapshot,
  type RecentRiskResult,
  type RiskDetail,
  type RiskScoreInput,
  getGraph,
  getRecentRiskResults,
  getStats,
  resetDemo,
  scoreTransaction,
} from "./api";

import {
  PaymentGraph,
} from "./PaymentGraph";

import "./DemoPage.css";

type Theme =
  | "light"
  | "dark";

type Scenario =
  | "normal"
  | "coordination"
  | "ring";

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

const EMPTY_CUSTOM = {
  customer_id: "judge_customer_01",
  merchant_id: "merchant_12",
  device_id: "judge_device_01",
  card_id: "judge_card_01",
  ip_id: "judge_ip_01",
  amount: "1499",
  account_age_days: "420",
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

function runId(prefix: string) {
  return `${prefix}_${Date.now()}_${Math.random()
    .toString(36)
    .slice(2, 7)}`;
}

function transaction(
  id: string,
  timestamp: Date,
  overrides: Partial<RiskScoreInput>,
): RiskScoreInput {
  return {
    transaction_id: id,
    customer_id: "customer_default",
    merchant_id: "merchant_01",
    device_id: "device_default",
    card_id: "card_default",
    ip_id: "ip_default",
    amount: 1200,
    timestamp: timestamp.toISOString(),
    account_age_days: 365,
    ...overrides,
  };
}

function scenarioTransactions(
  scenario: Scenario,
): RiskScoreInput[] {
  const base = new Date();
  const id = runId(scenario);

  if (scenario === "normal") {
    return Array.from(
      { length: 3 },
      (_, index) =>
        transaction(
          `${id}_${index + 1}`,
          base,
          {
            customer_id: `normal_customer_${id}_${index + 1}`,
            merchant_id: `merchant_${10 + index}`,
            device_id: `normal_device_${id}_${index + 1}`,
            card_id: `normal_card_${id}_${index + 1}`,
            ip_id: `normal_ip_${id}_${index + 1}`,
            amount: 700 + index * 260,
            account_age_days: 280 + index * 120,
          },
        ),
    );
  }

  if (scenario === "coordination") {
    return Array.from(
      { length: 8 },
      (_, index) =>
        transaction(
          `${id}_${index + 1}`,
          base,
          {
            customer_id: `coord_customer_${id}_${(index % 4) + 1}`,
            merchant_id: `merchant_${20 + (index % 3)}`,
            device_id: `shared_device_${id}`,
            card_id: `coord_card_${id}_${(index % 4) + 1}`,
            ip_id: `shared_ip_${id}`,
            amount: 900 + (index % 4) * 175,
            account_age_days: 190 + (index % 4) * 90,
          },
        ),
    );
  }

  return Array.from(
    { length: 20 },
    (_, index) => {
      const customer =
        (index % 5) + 1;

      return transaction(
        `${id}_${index + 1}`,
        base,
        {
          customer_id: `ring_customer_${id}_${customer}`,
          merchant_id: `merchant_${30 + (index % 4)}`,
          device_id: `ring_device_${id}`,
          card_id: `ring_card_${id}_${customer}`,
          ip_id: `ring_ip_${id}`,
          amount: 1100 + (index % 5) * 210,
          account_age_days: 120 + customer * 70,
        },
      );
    },
  );
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

  const [running, setRunning] =
    useState<string | null>(null);

  const [lastResult, setLastResult] =
    useState<RiskDetail | null>(null);

  const [demoError, setDemoError] =
    useState<string | null>(null);

  const [custom, setCustom] =
    useState(EMPTY_CUSTOM);

  const refresh = useCallback(async () => {
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
  }, []);

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

    const initialRefresh = window.setTimeout(
      () => void refresh(),
      0,
    );

    const interval = window.setInterval(
      () => void refresh(),
      2000,
    );

    return () => {
      window.clearTimeout(initialRefresh);
      window.clearInterval(interval);
    };
  }, [refresh]);

  async function runScenario(
    scenario: Scenario,
  ) {
    setRunning(scenario);
    setDemoError(null);

    try {
      let result: RiskDetail | null = null;

      for (
        const item of scenarioTransactions(scenario)
      ) {
        result = await scoreTransaction(item);
      }

      setLastResult(result);
      await refresh();
    } catch (error) {
      setDemoError(
        error instanceof Error
          ? error.message
          : "Scenario failed",
      );
    } finally {
      setRunning(null);
    }
  }

  async function handleReset() {
    setRunning("reset");
    setDemoError(null);

    try {
      await resetDemo();
      setLastResult(null);
      await refresh();
    } catch (error) {
      setDemoError(
        error instanceof Error
          ? error.message
          : "Reset failed",
      );
    } finally {
      setRunning(null);
    }
  }

  async function handleCustom(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    setRunning("custom");
    setDemoError(null);

    try {
      const result = await scoreTransaction(
        transaction(
          runId("custom"),
          new Date(),
          {
            customer_id: custom.customer_id,
            merchant_id: custom.merchant_id,
            device_id: custom.device_id,
            card_id: custom.card_id,
            ip_id: custom.ip_id,
            amount: Number(custom.amount),
            account_age_days: Number(
              custom.account_age_days,
            ),
          },
        ),
      );

      setLastResult(result);
      await refresh();
    } catch (error) {
      setDemoError(
        error instanceof Error
          ? error.message
          : "Custom transaction failed",
      );
    } finally {
      setRunning(null);
    }
  }

  const busy = running !== null;

  return (
    <main className="demo-shell">
      <header className="demo-nav">
        <a className="demo-brand" href="/">
          FRAME /// LIVE DEMO
        </a>

        <nav aria-label="Demo navigation">
          <a href="/">HOME</a>
          <a href="#test">TEST FRAME</a>
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

      <section className="demo-testbench" id="test">
        <header className="demo-section-head compact">
          <div>
            <p>[ TEST FRAME / 00 ]</p>
            <h2>INJECT LIVE TRAFFIC</h2>
          </div>

          <button
            className="demo-reset"
            type="button"
            disabled={busy}
            onClick={() => void handleReset()}
          >
            {running === "reset"
              ? "RESETTING..."
              : "RESET DEMO"}
          </button>
        </header>

        <div className="demo-test-grid">
          <article className="scenario-card">
            <span>01 / BASELINE</span>
            <h3>NORMAL PAYMENT</h3>
            <p>
              Three unrelated customers with unique cards,
              devices and IPs. Establish clean baseline traffic.
            </p>
            <button
              type="button"
              disabled={busy}
              onClick={() => void runScenario("normal")}
            >
              {running === "normal"
                ? "SCORING..."
                : ">>> SEND NORMAL TRAFFIC"}
            </button>
          </article>

          <article className="scenario-card">
            <span>02 / COORDINATION</span>
            <h3>SHARED INFRASTRUCTURE</h3>
            <p>
              Four customers reuse one device and IP across
              several merchants. Context begins to accumulate.
            </p>
            <button
              type="button"
              disabled={busy}
              onClick={() => void runScenario("coordination")}
            >
              {running === "coordination"
                ? "SCORING..."
                : ">>> INJECT COORDINATION"}
            </button>
          </article>

          <article className="scenario-card scenario-card-alert">
            <span>03 / RING BURST</span>
            <h3>COORDINATED FRAUD RING</h3>
            <p>
              Twenty ordinary-looking payments rapidly converge
              on shared device/IP infrastructure across five accounts.
            </p>
            <button
              type="button"
              disabled={busy}
              onClick={() => void runScenario("ring")}
            >
              {running === "ring"
                ? "BUILDING RING..."
                : ">>> START RING BURST"}
            </button>
          </article>
        </div>

        <div className="demo-test-status">
          <div>
            <span>RECOMMENDED SEQUENCE</span>
            <strong>RESET → NORMAL → COORDINATION → RING BURST</strong>
          </div>

          <div>
            <span>LATEST RESULT</span>
            <strong>
              {lastResult
                ? `${(lastResult.risk_score * 100).toFixed(1)}% / ${lastResult.action} / ${lastResult.evidence_count} SIGNALS`
                : "WAITING FOR TEST TRAFFIC"}
            </strong>
          </div>
        </div>

        {demoError && (
          <div className="demo-test-error">
            /// {demoError}
          </div>
        )}

        <details className="demo-custom">
          <summary>ADVANCED / CUSTOM TRANSACTION</summary>

          <form onSubmit={(event) => void handleCustom(event)}>
            {(
              [
                ["customer_id", "CUSTOMER"],
                ["merchant_id", "MERCHANT"],
                ["device_id", "DEVICE"],
                ["card_id", "CARD"],
                ["ip_id", "IP"],
                ["amount", "AMOUNT"],
                ["account_age_days", "ACCOUNT AGE DAYS"],
              ] as const
            ).map(([key, label]) => (
              <label key={key}>
                <span>{label}</span>
                <input
                  name={key}
                  type={
                    key === "amount" ||
                    key === "account_age_days"
                      ? "number"
                      : "text"
                  }
                  min={
                    key === "amount"
                      ? "0.01"
                      : key === "account_age_days"
                        ? "0"
                        : undefined
                  }
                  step={key === "amount" ? "0.01" : undefined}
                  required
                  value={custom[key]}
                  onChange={(event) =>
                    setCustom((current) => ({
                      ...current,
                      [key]: event.target.value,
                    }))
                  }
                />
              </label>
            ))}

            <button type="submit" disabled={busy}>
              {running === "custom"
                ? "SCORING..."
                : ">>> SCORE CUSTOM TRANSACTION"}
            </button>
          </form>
        </details>
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