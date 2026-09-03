import {
  type ChangeEvent,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  createPortal,
} from "react-dom";

import {
  type GraphSnapshot,
} from "./api";
import {
  PaymentGraph,
} from "./PaymentGraph";

import "./DatasetLab.css";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";

type Support =
  | "full_pipeline"
  | "adapter_ready"
  | "multi_file_graph"
  | "multi_file_gated"
  | "transaction_only";

interface EntityMapping {
  column: string;
  type: string;
}

interface Mapping {
  transaction_id?: string | null;
  timestamp?: string | null;
  amount?: string | null;
  label?: string | null;
  entities: EntityMapping[];
}

interface DatasetProfile {
  id: string;
  name: string;
  provider: string;
  kind: string;
  access: string;
  support: Support;
  scale: string;
  labels: boolean;
  graph_mode: string;
  description: string;
  source_url: string;
  limitations: string;
  default_mapping: Mapping | null;
}

interface CatalogResponse {
  datasets: DatasetProfile[];
  count: number;
  upload_limits: {
    max_csv_mb: number;
    max_rows: number;
  };
}

interface AnalysisResult {
  analysis_id: string;
  dataset_id: string;
  filename: string;
  analysis_mode: string;
  model: {
    name: string;
    purpose: string;
    features: string[];
  };
  summary: {
    rows_analyzed: number;
    columns: number;
    graph_nodes: number;
    graph_edges: number;
    components: number;
    largest_component: number;
    entity_types: string[];
  };
  evaluation: null | {
    labeled_rows: number;
    positive_labels: number;
    anomaly_pr_auc?: number;
    anomaly_roc_auc?: number;
  };
  graph: GraphSnapshot & {
    truncated?: boolean;
    total_nodes?: number;
    total_edges?: number;
  };
  top_anomalies: Array<{
    transaction_id: string;
    row: number;
    anomaly_score: number;
    amount: number;
    label: number | null;
    entities: string[];
  }>;
}

const ENTITY_TYPES = [
  "account",
  "customer",
  "merchant",
  "card",
  "device",
  "ip",
  "terminal",
  "bank",
  "entity",
] as const;

function parseHeader(text: string): string[] {
  const firstLine = text.split(/\r?\n/, 1)[0] ?? "";
  const values: string[] = [];
  let current = "";
  let quoted = false;

  for (let index = 0; index < firstLine.length; index += 1) {
    const character = firstLine[index];

    if (character === '"') {
      if (quoted && firstLine[index + 1] === '"') {
        current += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
      continue;
    }

    if (character === "," && !quoted) {
      values.push(current.trim());
      current = "";
      continue;
    }

    current += character;
  }

  values.push(current.trim());
  return values.filter(Boolean);
}

async function readApiError(response: Response) {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall back to a status message.
  }

  return `HTTP ${response.status}`;
}

function supportLabel(support: Support) {
  switch (support) {
    case "full_pipeline":
      return "FULL PIPELINE";
    case "adapter_ready":
      return "ADAPTER READY";
    case "multi_file_graph":
      return "MULTI-FILE GRAPH";
    case "multi_file_gated":
      return "GATED / MULTI-FILE";
    case "transaction_only":
      return "TRANSACTION ONLY";
  }
}

function isSingleCsvRunnable(profile: DatasetProfile | undefined) {
  if (!profile) {
    return true;
  }

  return profile.support === "full_pipeline" ||
    profile.support === "adapter_ready";
}

export function DatasetLab() {
  const [target, setTarget] =
    useState<HTMLElement | null>(null);
  const [catalog, setCatalog] =
    useState<CatalogResponse | null>(null);
  const [selectedId, setSelectedId] =
    useState("custom");
  const [fileName, setFileName] =
    useState("");
  const [csvText, setCsvText] =
    useState("");
  const [columns, setColumns] =
    useState<string[]>([]);
  const [mapping, setMapping] =
    useState<Mapping>({
      entities: [
        { column: "", type: "entity" },
        { column: "", type: "entity" },
      ],
    });
  const [analysis, setAnalysis] =
    useState<AnalysisResult | null>(null);
  const [running, setRunning] =
    useState(false);
  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      const next = document.querySelector<HTMLElement>(
        ".demo-testbench",
      );
      if (next) {
        setTarget(next);
        observer.disconnect();
      }
    });

    const existing = document.querySelector<HTMLElement>(
      ".demo-testbench",
    );

    if (existing) {
      const timer = window.setTimeout(
        () => setTarget(existing),
        0,
      );
      return () => window.clearTimeout(timer);
    }

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadCatalog() {
      try {
        const response = await fetch(
          `${API_BASE}/api/v1/datasets`,
        );
        if (!response.ok) {
          throw new Error(await readApiError(response));
        }

        const payload: CatalogResponse = await response.json();
        if (!cancelled) {
          setCatalog(payload);
        }
      } catch (catalogError) {
        if (!cancelled) {
          setError(
            catalogError instanceof Error
              ? catalogError.message
              : "Unable to load dataset catalog",
          );
        }
      }
    }

    void loadCatalog();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedProfile = useMemo(
    () => catalog?.datasets.find((dataset) => dataset.id === selectedId),
    [catalog, selectedId],
  );

  function chooseDataset(profile: DatasetProfile) {
    setSelectedId(profile.id);
    setAnalysis(null);
    setError(null);

    if (profile.default_mapping) {
      setMapping(profile.default_mapping);
    }
  }

  function chooseCustom() {
    setSelectedId("custom");
    setAnalysis(null);
    setError(null);
    setMapping({
      entities: [
        { column: "", type: "entity" },
        { column: "", type: "entity" },
      ],
    });
  }

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const text = await file.text();
    setFileName(file.name);
    setCsvText(text);
    setColumns(parseHeader(text));
    setAnalysis(null);
    setError(null);
  }

  function updateEntity(index: number, key: "column" | "type", value: string) {
    setMapping((current) => ({
      ...current,
      entities: current.entities.map((entity, entityIndex) =>
        entityIndex === index
          ? { ...entity, [key]: value }
          : entity,
      ),
    }));
  }

  async function runAnalysis() {
    if (!csvText || !fileName) {
      setError("Choose a CSV file before running FRAME.");
      return;
    }

    if (!isSingleCsvRunnable(selectedProfile)) {
      setError(
        "This catalog entry uses a different ingestion mode. Use its source link or choose a single-CSV adapter/BYOD file.",
      );
      return;
    }

    const explicitMapping = selectedId === "custom"
      ? mapping
      : undefined;

    if (
      explicitMapping &&
      explicitMapping.entities.filter((entity) => entity.column).length < 2
    ) {
      setError("Map at least two relationship entity columns.");
      return;
    }

    setRunning(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE}/api/v1/analysis/dataset`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            dataset_id: selectedId,
            filename: fileName,
            csv_text: csvText,
            mapping: explicitMapping,
            row_limit: 5000,
          }),
        },
      );

      if (!response.ok) {
        throw new Error(await readApiError(response));
      }

      const payload: AnalysisResult = await response.json();
      setAnalysis(payload);
    } catch (analysisError) {
      setError(
        analysisError instanceof Error
          ? analysisError.message
          : "Dataset analysis failed",
      );
    } finally {
      setRunning(false);
    }
  }

  if (!target) {
    return null;
  }

  return createPortal(
    <div className="dataset-lab-root">
      <header className="dataset-lab-head">
        <div>
          <p>[ DATASET LAB / 00 ]</p>
          <h2>RUN FRAME ON DATA</h2>
        </div>
        <div className="dataset-lab-head-note">
          <span>{catalog?.count ?? "—"} DATASET PROFILES</span>
          <span>BYOD CSV</span>
          <span>GRAPH + ML</span>
        </div>
      </header>

      <section className="dataset-catalog" aria-label="Dataset catalog">
        {catalog?.datasets.map((dataset) => (
          <article
            className={
              selectedId === dataset.id
                ? "dataset-card is-selected"
                : "dataset-card"
            }
            key={dataset.id}
          >
            <div className="dataset-card-meta">
              <span>{dataset.provider}</span>
              <strong>{supportLabel(dataset.support)}</strong>
            </div>
            <h3>{dataset.name}</h3>
            <p>{dataset.description}</p>
            <dl>
              <div><dt>GRAPH</dt><dd>{dataset.graph_mode}</dd></div>
              <div><dt>SCALE</dt><dd>{dataset.scale}</dd></div>
              <div><dt>LABELS</dt><dd>{dataset.labels ? "YES" : "NO"}</dd></div>
            </dl>
            <div className="dataset-card-actions">
              <button
                type="button"
                onClick={() => chooseDataset(dataset)}
              >
                {isSingleCsvRunnable(dataset)
                  ? ">>> USE ADAPTER"
                  : ">>> INSPECT MODE"}
              </button>
              <a href={dataset.source_url} target="_blank" rel="noreferrer">
                SOURCE ↗
              </a>
            </div>
            <small>{dataset.limitations}</small>
          </article>
        ))}

        <article
          className={
            selectedId === "custom"
              ? "dataset-card dataset-card-custom is-selected"
              : "dataset-card dataset-card-custom"
          }
        >
          <div className="dataset-card-meta">
            <span>YOUR DATA</span>
            <strong>SCHEMA MAPPER</strong>
          </div>
          <h3>UPLOAD YOUR OWN CSV</h3>
          <p>
            Map the relationships your data actually contains. FRAME never invents
            missing customers, devices, IPs, cards or merchants.
          </p>
          <button type="button" onClick={chooseCustom}>
            &gt;&gt;&gt; MAP CUSTOM DATA
          </button>
        </article>
      </section>

      <section className="dataset-workbench">
        <header>
          <div>
            <span>SELECTED PROFILE</span>
            <strong>{selectedProfile?.name ?? "CUSTOM / BYOD"}</strong>
          </div>
          <div>
            <span>EXECUTION MODE</span>
            <strong>
              {selectedProfile
                ? supportLabel(selectedProfile.support)
                : "RELATIONAL GRAPH"}
            </strong>
          </div>
        </header>

        <div className="dataset-upload-row">
          <label className="dataset-drop">
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => void handleFile(event)}
            />
            <span>[ CSV INPUT ]</span>
            <strong>{fileName || "DROP / CHOOSE DATASET FILE"}</strong>
            <small>
              Public deployment: first 5,000 rows, 5 MB upload cap.
            </small>
          </label>

          <div className="dataset-run-panel">
            <span>PIPELINE</span>
            <strong>
              INGEST → GRAPH → GRAPH FEATURES → ISOLATION FOREST → EVALUATE
            </strong>
            <button
              type="button"
              disabled={running || !isSingleCsvRunnable(selectedProfile)}
              onClick={() => void runAnalysis()}
            >
              {running ? "ANALYZING..." : ">>> RUN FRAME"}
            </button>
          </div>
        </div>

        {selectedId === "custom" && columns.length > 0 && (
          <div className="dataset-mapper">
            <header>
              <span>[ SCHEMA MAPPER ]</span>
              <strong>{columns.length} COLUMNS DETECTED</strong>
            </header>

            <div className="dataset-entity-map">
              {mapping.entities.map((entity, index) => (
                <div className="dataset-map-row" key={`entity-${index}`}>
                  <span>ENTITY {index + 1}</span>
                  <select
                    value={entity.column}
                    onChange={(event) =>
                      updateEntity(index, "column", event.target.value)
                    }
                  >
                    <option value="">SELECT COLUMN</option>
                    {columns.map((column) => (
                      <option key={column} value={column}>{column}</option>
                    ))}
                  </select>
                  <select
                    value={entity.type}
                    onChange={(event) =>
                      updateEntity(index, "type", event.target.value)
                    }
                  >
                    {ENTITY_TYPES.map((type) => (
                      <option key={type} value={type}>{type.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <div className="dataset-optional-map">
              {([
                ["amount", "AMOUNT"],
                ["label", "LABEL"],
                ["transaction_id", "TRANSACTION ID"],
                ["timestamp", "TIMESTAMP"],
              ] as const).map(([key, label]) => (
                <label key={key}>
                  <span>{label}</span>
                  <select
                    value={mapping[key] ?? ""}
                    onChange={(event) =>
                      setMapping((current) => ({
                        ...current,
                        [key]: event.target.value || null,
                      }))
                    }
                  >
                    <option value="">NOT MAPPED</option>
                    {columns.map((column) => (
                      <option key={column} value={column}>{column}</option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="dataset-error">/// {error}</div>
        )}
      </section>

      {analysis && (
        <section className="dataset-results">
          <header className="dataset-results-head">
            <div>
              <p>[ ANALYSIS / {analysis.analysis_id.slice(0, 8).toUpperCase()} ]</p>
              <h2>RELATIONSHIP ANALYSIS</h2>
            </div>
            <div>
              <span>{analysis.model.name}</span>
              <span>{analysis.analysis_mode.replaceAll("_", " ")}</span>
            </div>
          </header>

          <div className="dataset-summary-grid">
            <div><span>ROWS</span><strong>{analysis.summary.rows_analyzed}</strong></div>
            <div><span>NODES</span><strong>{analysis.summary.graph_nodes}</strong></div>
            <div><span>EDGES</span><strong>{analysis.summary.graph_edges}</strong></div>
            <div><span>COMPONENTS</span><strong>{analysis.summary.components}</strong></div>
            <div><span>LARGEST COMPONENT</span><strong>{analysis.summary.largest_component}</strong></div>
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
                <span>{row.label === null ? "UNLABELED" : `LABEL ${row.label}`}</span>
                <span>{row.entities.slice(0, 3).join(" / ")}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>,
    target,
  );
}
