import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  type RiskDetail,
  type RiskEvidence,
  getRiskDetail,
} from "./api";

import "./InvestigationOverlay.css";


function formatEvidenceType(
  value: string,
) {
  return value
    .replaceAll(
      "_",
      " ",
    )
    .toUpperCase();
}


function formatValue(
  value: number,
) {
  if (
    Number.isInteger(
      value,
    )
  ) {
    return String(
      value,
    );
  }

  return value.toFixed(
    2,
  );
}


function caseStatus(
  action: RiskDetail["action"],
) {
  if (
    action === "BLOCK"
  ) {
    return "INTERCEPTED";
  }

  if (
    action === "REVIEW"
  ) {
    return "ANALYST REVIEW";
  }

  return "OBSERVED";
}


function EvidenceRow({
  evidence,
  index,
}: {
  evidence: RiskEvidence;
  index: number;
}) {
  const severity =
    Math.max(
      0,
      Math.min(
        1,
        evidence.severity,
      ),
    );

  return (
    <article className="investigation-evidence">
      <header className="investigation-evidence-header">
        <span>
          {String(
            index + 1,
          ).padStart(
            2,
            "0",
          )}
          .
        </span>

        <strong>
          {formatEvidenceType(
            evidence.type,
          )}
        </strong>

        <span>
          VALUE{" "}
          {formatValue(
            evidence.value,
          )}
        </span>
      </header>

      <p>
        {
          evidence.message
        }
      </p>

      <div
        className="investigation-severity"
        aria-label={`Observed signal severity ${(
          severity *
          100
        ).toFixed(
          0,
        )}%`}
      >
        <span
          style={{
            width: `${
              severity *
              100
            }%`,
          }}
        />
      </div>
    </article>
  );
}


function graphNodeIds(
  result: RiskDetail,
): string[] {
  const entities =
    result.entities;

  if (!entities) {
    return [];
  }

  return [
    `customer:${entities.customer}`,
    `device:${entities.device}`,
    `ip:${entities.ip}`,
    `card:${entities.card}`,
    `merchant:${entities.merchant}`,
  ];
}


export function InvestigationOverlay() {
  const [
    selected,
    setSelected,
  ] = useState<
    RiskDetail | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(
    false,
  );

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    closing,
    setClosing,
  ] = useState(
    false,
  );

  const closeTimerRef =
    useRef<
      number | null
    >(null);


  const closeInvestigation =
    useCallback(
      () => {
        if (closing) {
          return;
        }

        setClosing(
          true,
        );

        if (
          closeTimerRef.current
          !== null
        ) {
          window.clearTimeout(
            closeTimerRef.current,
          );
        }

        const reducedMotion =
          window.matchMedia(
            "(prefers-reduced-motion: reduce)",
          ).matches;

        closeTimerRef.current =
          window.setTimeout(
            () => {
              setSelected(
                null,
              );

              setError(
                null,
              );

              setLoading(
                false,
              );

              setClosing(
                false,
              );

              closeTimerRef.current =
                null;
            },
            reducedMotion
              ? 0
              : 180,
          );
      },
      [
        closing,
      ],
    );


  useEffect(() => {
    return () => {
      if (
        closeTimerRef.current
        !== null
      ) {
        window.clearTimeout(
          closeTimerRef.current,
        );
      }
    };
  }, []);


  useEffect(() => {
    async function handleDecisionClick(
      event: MouseEvent,
    ) {
      const target =
        event.target;

      if (
        !(
          target instanceof
          Element
        )
      ) {
        return;
      }

      const row =
        target.closest(
          ".decision-row",
        );

      if (
        !row
      ) {
        return;
      }

      const actionElement =
        row.querySelector(
          ".decision-action",
        );

      const action =
        actionElement
          ?.textContent
          ?.replaceAll(
            "[",
            "",
          )
          .replaceAll(
            "]",
            "",
          )
          .trim();

      if (
        action !==
          "REVIEW" &&
        action !==
          "BLOCK"
      ) {
        return;
      }

      const idElement =
        row.querySelector(
          ".decision-id",
        );

      const transactionId =
        idElement
          ?.textContent
          ?.trim();

      if (
        !transactionId
      ) {
        return;
      }

      if (
        closeTimerRef.current
        !== null
      ) {
        window.clearTimeout(
          closeTimerRef.current,
        );

        closeTimerRef.current =
          null;
      }

      setClosing(
        false,
      );

      setLoading(
        true,
      );

      setError(
        null,
      );

      try {
        const result =
          await getRiskDetail(
            transactionId,
          );

        setSelected(
          result,
        );
      } catch {
        setError(
          "Unable to load investigation.",
        );

        setSelected(
          null,
        );
      } finally {
        setLoading(
          false,
        );
      }
    }

    document.addEventListener(
      "click",
      handleDecisionClick,
    );

    return () => {
      document.removeEventListener(
        "click",
        handleDecisionClick,
      );
    };
  }, []);


  useEffect(() => {
    function handleKeyDown(
      event: KeyboardEvent,
    ) {
      if (
        event.key ===
        "Escape"
      ) {
        closeInvestigation();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [
    closeInvestigation,
  ]);


  function locateInNetwork() {
    if (
      !selected
    ) {
      return;
    }

    const nodeIds =
      graphNodeIds(
        selected,
      );

    if (
      nodeIds.length === 0
    ) {
      return;
    }

    window.dispatchEvent(
      new CustomEvent(
        "frame:focus-network",
        {
          detail: {
            transactionId:
              selected.transaction_id,

            nodeIds,
          },
        },
      ),
    );

    closeInvestigation();

    window.setTimeout(
      () => {
        const network =
          document.getElementById(
            "network",
          );

        if (!network) {
          return;
        }

        const reducedMotion =
          window.matchMedia(
            "(prefers-reduced-motion: reduce)",
          ).matches;

        network.scrollIntoView({
          behavior:
            reducedMotion
              ? "auto"
              : "smooth",

          block:
            "start",
        });
      },
      200,
    );
  }


  const visible =
    selected !== null ||
    loading ||
    error !== null;


  if (
    !visible
  ) {
    return null;
  }


  return (
    <div
      className={
        closing
          ? "investigation-layer closing"
          : "investigation-layer"
      }
      role="presentation"
    >
      <button
        className="investigation-backdrop"
        type="button"
        aria-label="Close investigation"
        onClick={
          closeInvestigation
        }
      />

      <aside
        className="investigation-panel"
        aria-label="Transaction investigation"
      >
        <header className="investigation-header">
          <div>
            <span>
              [
              {" "}
              INVESTIGATION / 04
              {" "}
              ]
            </span>

            <h2>
              OBSERVED
              <br />
              NETWORK
              <br />
              EVIDENCE
            </h2>
          </div>

          <button
            className="investigation-close"
            type="button"
            aria-label="Close investigation"
            onClick={
              closeInvestigation
            }
          >
            [ X ]
          </button>
        </header>

        {loading && (
          <div className="investigation-loading">
            &gt;&gt;&gt;
            {" "}
            LOADING CASE
          </div>
        )}

        {error && (
          <div className="investigation-error">
            &gt;&gt;&gt;
            {" "}
            {error}
          </div>
        )}

        {selected && (
          <>
            <div className="investigation-case-grid">
              <div className="investigation-case-id">
                <span>
                  TRANSACTION
                </span>

                <strong>
                  {
                    selected.transaction_id
                  }
                </strong>
              </div>

              <div>
                <span>
                  RISK SCORE
                </span>

                <strong>
                  {(
                    selected.risk_score *
                    100
                  ).toFixed(
                    1,
                  )}
                  %
                </strong>
              </div>

              <div>
                <span>
                  ACTION
                </span>

                <strong
                  className={`investigation-action ${selected.action.toLowerCase()}`}
                >
                  [
                  {
                    selected.action
                  }
                  ]
                </strong>
              </div>

              <div>
                <span>
                  SIGNALS
                </span>

                <strong>
                  {String(
                    selected.evidence_count,
                  ).padStart(
                    2,
                    "0",
                  )}
                </strong>
              </div>

              <div className="investigation-case-status">
                <span>
                  CASE STATUS
                </span>

                <strong>
                  [
                  {" "}
                  {caseStatus(
                    selected.action,
                  )}
                  {" "}
                  ]
                </strong>
              </div>
            </div>

            <div className="investigation-disclaimer">
              <strong>
                ///
                {" "}
                OBSERVED CONTEXT
              </strong>

              <p>
                These are graph
                and temporal facts
                observed when this
                transaction was
                scored. They are
                not feature
                attributions or a
                claim that any one
                signal caused the
                model score.
              </p>
            </div>

            {selected.entities && (
              <div className="investigation-network-action">
                <span>
                  [
                  {" "}
                  GRAPH CONTEXT
                  {" "}
                  ]
                </span>

                <button
                  type="button"
                  onClick={
                    locateInNetwork
                  }
                >
                  &gt;&gt;&gt;
                  {" "}
                  LOCATE IN NETWORK
                </button>
              </div>
            )}

            <section className="investigation-evidence-list">
              <header>
                <span>
                  [
                  {" "}
                  SIGNAL REGISTER
                  {" "}
                  ]
                </span>

                <span>
                  {
                    selected.evidence.length
                  }
                  {" "}
                  OBSERVED
                </span>
              </header>

              {selected.evidence.length ===
              0 ? (
                <div className="investigation-empty">
                  NO OBSERVED
                  NETWORK EVIDENCE
                </div>
              ) : (
                selected.evidence.map(
                  (
                    evidence,
                    index,
                  ) => (
                    <EvidenceRow
                      key={`${evidence.type}-${index}`}
                      evidence={
                        evidence
                      }
                      index={
                        index
                      }
                    />
                  ),
                )
              )}
            </section>

            <footer className="investigation-footer">
              <span>
                FRAME™
              </span>

              <span>
                CASE REVIEW
              </span>

              <span>
                ESC TO CLOSE
              </span>
            </footer>
          </>
        )}
      </aside>
    </div>
  );
}