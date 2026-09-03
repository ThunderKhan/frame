import {
  useEffect,
  useState,
} from "react";
import {
  createPortal,
} from "react-dom";

import type {
  GraphSnapshot,
} from "./api";
import {
  PaymentGraph,
} from "./PaymentGraph";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";

interface BuiltinAnalysis {
  analysis_id: string;
  analysis_mode: string;
  model: {
    name: string;
    purpose: string;
  };
  summary: {
    rows_analyzed: number;
    graph_nodes: number;
    graph_edges: number;
    components: number;
    largest_component: number;
  };
  evaluation: null | {
    labeled_rows: number;
    positive_labels: number;
    anomaly_pr_auc?: number;
    anomaly_roc_auc?: number;
  };
  graph: GraphSnapshot;
  top_anomalies: Array<{
    transaction_id: string;
    anomaly_score: number;
    amount: number;
    label: number | null;
    entities: string[];
    row: number;
  }>;
}

async function readApiError(
  response: Response,
): Promise<string> {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall through to the HTTP status.
  }

  return `HTTP ${response.status}`;
}

function scrollToWorkbench() {
  window.setTimeout(() => {
    document
      .querySelector(".dataset-workbench")
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  }, 80);
}

export function DatasetLabActions() {
  const [target, setTarget] =
    useState<HTMLElement | null>(null);
  const [running, setRunning] =
    useState(false);
  const [analysis, setAnalysis] =
    useState<BuiltinAnalysis | null>(null);
  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    function refreshTargetAndLabel() {
      const workbench = document.querySelector<HTMLElement>(
        ".dataset-workbench",
      );
      if (workbench) {
        setTarget(workbench);
      }

      for (
        const card of document.querySelectorAll<HTMLElement>(
          ".dataset-card",
        )
      ) {
        const title = card.querySelector("h3")?.textContent?.trim();
        if (title !== "FRAME RING BENCHMARK") {
          continue;
        }

        const button = card.querySelector<HTMLButtonElement>("button");
        if (button) {
          button.textContent = running
            ? "ANALYZING BUILT-IN..."
            : ">>> RUN BUILT-IN";
        }
      }
    }

    refreshTargetAndLabel();

    const observer = new MutationObserver(refreshTargetAndLabel);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => observer.disconnect();
  }, [running]);

  useEffect(() => {
    async function handleClick(event: MouseEvent) {
      const element = event.target;
      if (!(element instanceof Element)) {
        return;
      }

      const button = element.closest<HTMLButtonElement>(".dataset-card button");
      if (!button) {
        return;
      }

      const card = button.closest<HTMLElement>(".dataset-card");
      const title = card?.querySelector("h3")?.textContent?.trim();

      if (title !== "FRAME RING BENCHMARK") {
        scrollToWorkbench();
        return;
      }

      if (running) {
        return;
      }

      setRunning(true);
      setAnalysis(null);
      setError(null);
      scrollToWorkbench();

      try {
        const response = await fetch(
          `${API_BASE}/api/v1/analysis/builtin/frame-benchmark`,
          {
            method: "POST",
          },
        );

        if (!response.ok) {
          throw new Error(await readApiError(response));
        }

        const payload: BuiltinAnalysis = await response.json();
        setAnalysis(payload);

        window.setTimeout(() => {
          document
            .querySelector(".dataset-builtin-results")
            ?.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
        }, 120);
      } catch (analysisError) {
        setError(
          analysisError instanceof Error
            ? analysisError.message
            : "Built-in benchmark analysis failed",
        );
      } finally {
        setRunning(false);
      }
    }

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, [running]);

  if (!target) {
    return null;
  }

  return createPortal(
    <>
      {running && (
        <div className="dataset-model-note">
          <strong>BUILT-IN RUN ///</strong>
          <p>
            Generating the FRAME hard-negative benchmark server-side and running
            relationship graph construction, graph features, anomaly ranking and
            labeled evaluation.
          </p>
        </div>
      )}

      {error && (
        <div className="dataset-error">
          /// {error}
        </div>
      )}

      {analysis && (
        <section className="dataset-results dataset-builtin-results">
          <header className="dataset-results-head">
            <div>
              <p>
                [ BUILT-IN ANALYSIS / {analysis.analysis_id.slice(0, 8).toUpperCase()} ]
              </p>
              <h2>FRAME BENCHMARK RESULT</h2>
            </div>
            <div>
              <span>{analysis.model.name}</span>
              <span>{analysis.analysis_mode.replaceAll("_", " ")}</span>
            </div>
          </header>

          <div className="dataset-summary-grid">
            <div>
              <span>ROWS</span>
              <strong>{analysis.summary.rows_analyzed}</strong>
            </div>
            <div>
              <span>NODES</span>
              <strong>{analysis.summary.graph_nodes}</strong>
            </div>
            <div>
              <span>EDGES</span>
              <strong>{analysis.summary.graph_edges}</strong>
            </div>
            <div>
              <span>COMPONENTS</span>
              <strong>{analysis.summary.components}</strong>
            </div>
            <div>
              <span>FRAUD LABELS</span>
              <strong>{analysis.evaluation?.positive_labels ?? "N/A"}</strong>
            </div>
            <div>
              <span>PR-AUC</span>
              <strong>
                {analysis.evaluation?.anomaly_pr_auc !== undefined
                  ? analysis.evaluation.anomaly_pr_auc.toFixed(4)
                  : "N/A"}
              </strong>
            </div>
          </div>

          <div className="dataset-model-note">
            <strong>MODEL SCOPE ///</strong>
            <p>{analysis.model.purpose}</p>
          </div>

          <div className="dataset-analysis-graph">
            <PaymentGraph graph={analysis.graph} />
          </div>

          <div className="dataset-anomaly-table">
            <header>
              <span>TOP RELATIONSHIP ANOMALIES</span>
              <span>TOP {Math.min(analysis.top_anomalies.length, 20)}</span>
            </header>
            {analysis.top_anomalies.slice(0, 20).map((row) => (
              <div key={`${row.transaction_id}-${row.row}`}>
                <span>{row.transaction_id}</span>
                <strong>{(row.anomaly_score * 100).toFixed(1)}%</strong>
                <span>
                  {row.label === null ? "UNLABELED" : `LABEL ${row.label}`}
                </span>
                <span>{row.entities.slice(0, 3).join(" / ")}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </>,
    target,
  );
}
