import "./App.css";

function App() {
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
          <span className="status-dot" />
          Risk engine online
        </div>
      </header>

      <section className="hero-grid">
        <article className="panel">
          <p className="panel-label">Transactions scored</p>
          <strong className="metric">0</strong>
        </article>

        <article className="panel">
          <p className="panel-label">Under review</p>
          <strong className="metric">0</strong>
        </article>

        <article className="panel">
          <p className="panel-label">Blocked</p>
          <strong className="metric">0</strong>
        </article>

        <article className="panel">
          <p className="panel-label">Graph entities</p>
          <strong className="metric">0</strong>
        </article>
      </section>

      <section className="workspace">
        <article className="panel graph-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-label">Network intelligence</p>
              <h2>Payment relationship graph</h2>
            </div>
          </div>

          <div className="empty-state">
            Graph visualization coming next.
          </div>
        </article>

        <article className="panel">
          <p className="panel-label">Live decisions</p>
          <h2>Recent risk activity</h2>

          <div className="empty-state">
            Waiting for transactions.
          </div>
        </article>
      </section>
    </main>
  );
}

export default App;