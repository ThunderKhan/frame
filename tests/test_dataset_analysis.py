from fastapi.testclient import TestClient

from frame.api.app import app


def test_dataset_catalog_exposes_multiple_analysis_modes() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/datasets")

    assert response.status_code == 200

    payload = response.json()
    assert payload["count"] >= 13

    dataset_ids = {dataset["id"] for dataset in payload["datasets"]}

    assert "frame-benchmark" in dataset_ids
    assert "ibm-aml" in dataset_ids
    assert "amlsim" in dataset_ids
    assert "paysim" in dataset_ids
    assert "banksim" in dataset_ids
    assert "elliptic" in dataset_ids
    assert "ieee-cis" in dataset_ids
    assert "ulb-creditcard" in dataset_ids
    assert "baf-neurips" in dataset_ids
    assert "bitcoinheist" in dataset_ids

    supports = {dataset["support"] for dataset in payload["datasets"]}

    assert "full_pipeline" in supports
    assert "adapter_ready" in supports
    assert "multi_file_graph" in supports
    assert "multi_file_gated" in supports
    assert "transaction_only" in supports


def test_builtin_frame_benchmark_runs_end_to_end() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/analysis/builtin/frame-benchmark"
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["dataset_id"] == "frame-benchmark"
    assert payload["analysis_mode"] == "relational_graph_unsupervised"
    assert payload["model"]["name"] == "IsolationForest"
    assert payload["summary"]["rows_analyzed"] > 200
    assert payload["summary"]["graph_nodes"] > 0
    assert payload["summary"]["graph_edges"] > 0
    assert payload["evaluation"] is not None
    assert payload["evaluation"]["positive_labels"] > 0
    assert payload["graph"]["nodes"]
    assert payload["graph"]["edges"]
    assert payload["stream_events"]
    assert payload["graph"]["stream_events"] == payload["stream_events"]
    assert payload["graph"]["analysis_id"] == payload["analysis_id"]
    assert payload["stream_events"][0]["row"] == 1

    first_event = payload["stream_events"][0]
    assert "risk_score" in first_event
    assert "action" in first_event
    assert "evidence_count" in first_event

    flagged_events = [
        event
        for event in payload["stream_events"]
        if event["action"] in {"REVIEW", "BLOCK"}
    ]
    assert flagged_events


def test_custom_dataset_analysis_builds_graph_and_scores_rows() -> None:
    client = TestClient(app)

    lines = ["tx,source,target,amount,label"]

    for index in range(30):
        source = f"acct_{index % 6}"
        target = "hub" if index >= 24 else f"merchant_{index % 10}"
        amount = 100 + index * 7
        label = 1 if index >= 24 else 0

        lines.append(f"tx_{index},{source},{target},{amount},{label}")

    response = client.post(
        "/api/v1/analysis/dataset",
        json={
            "dataset_id": "custom",
            "filename": "custom.csv",
            "csv_text": "\n".join(lines),
            "row_limit": 5000,
            "mapping": {
                "transaction_id": "tx",
                "amount": "amount",
                "label": "label",
                "entities": [
                    {
                        "column": "source",
                        "type": "account",
                    },
                    {
                        "column": "target",
                        "type": "merchant",
                    },
                ],
            },
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["analysis_mode"] == "relational_graph_unsupervised"
    assert payload["model"]["name"] == "IsolationForest"
    assert payload["summary"]["rows_analyzed"] == 30
    assert payload["summary"]["graph_nodes"] > 0
    assert payload["summary"]["graph_edges"] > 0

    assert payload["graph"]["nodes"]
    assert payload["graph"]["edges"]
    assert len(payload["stream_events"]) == 30
    assert payload["stream_events"][0]["transaction_id"] == "tx_0"

    first_node = payload["graph"]["nodes"][0]
    assert "attributes" in first_node
    assert "node_type" in first_node["attributes"]

    assert payload["evaluation"]["labeled_rows"] == 30
    assert payload["evaluation"]["positive_labels"] == 6
    assert "anomaly_pr_auc" in payload["evaluation"]

    assert len(payload["top_anomalies"]) == 30


def test_known_paysim_adapter_maps_without_explicit_schema() -> None:
    client = TestClient(app)

    lines = [
        (
            "step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,"
            "nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud"
        )
    ]

    for index in range(20):
        lines.append(
            ",".join(
                [
                    str(index + 1),
                    "TRANSFER",
                    str(500 + index),
                    f"C{index % 4}",
                    "1000",
                    "500",
                    f"M{index % 7}",
                    "0",
                    "500",
                    "1" if index >= 18 else "0",
                    "0",
                ]
            )
        )

    response = client.post(
        "/api/v1/analysis/dataset",
        json={
            "dataset_id": "paysim",
            "filename": "paysim.csv",
            "csv_text": "\n".join(lines),
            "row_limit": 100,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["dataset_id"] == "paysim"
    assert payload["summary"]["entity_types"] == ["account"]
    assert payload["evaluation"]["positive_labels"] == 2
