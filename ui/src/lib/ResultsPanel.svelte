<script>
  let { results = null } = $props()
</script>

<div class="results-panel">
  <div class="panel-header">
    <h2>Simulation Results</h2>
    <p>View calculation outputs</p>
  </div>

  {#if results}
    <div class="results-content">
      {#if results.unit_operations}
        <div class="results-section">
          <div class="section-header">
            <span class="section-icon">🏭</span>
            <h3>Unit Operations</h3>
          </div>
          <div class="results-grid">
            {#each Object.entries(results.unit_operations) as [unitId, unitResults]}
              <div class="result-card">
                <div class="card-header">
                  <h4>{unitId}</h4>
                </div>
                <div class="card-content">
                  {#each Object.entries(unitResults) as [key, value]}
                    <div class="result-item">
                      <span class="result-label">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:</span>
                      <span class="result-value">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if results.streams}
        <div class="results-section">
          <div class="section-header">
            <span class="section-icon">🌊</span>
            <h3>Streams</h3>
          </div>
          <div class="results-grid">
            {#each Object.entries(results.streams) as [streamId, streamProps]}
              <div class="result-card">
                <div class="card-header">
                  <h4>{streamId}</h4>
                </div>
                <div class="card-content">
                  {#if streamProps.stream_type === 'energy'}
                    <div class="result-item">
                      <span class="result-label">Energy Flow:</span>
                      <span class="result-value">{streamProps.energy_flow_kw?.toFixed(2)} kW</span>
                    </div>
                    <div class="result-item">
                      <span class="result-label">Temp Low:</span>
                      <span class="result-value">{streamProps.temperature_low?.toFixed(1)} K</span>
                    </div>
                    <div class="result-item">
                      <span class="result-label">Temp High:</span>
                      <span class="result-value">{streamProps.temperature_high?.toFixed(1)} K</span>
                    </div>
                  {:else}
                    <div class="result-item">
                      <span class="result-label">Temperature:</span>
                      <span class="result-value">{streamProps.temperature?.toFixed(2)} K</span>
                    </div>
                    <div class="result-item">
                      <span class="result-label">Pressure:</span>
                      <span class="result-value">{streamProps.pressure?.toFixed(0)} Pa</span>
                    </div>
                    <div class="result-item">
                      <span class="result-label">Mass Flow:</span>
                      <span class="result-value">{streamProps.mass_flow_rate?.toFixed(4)} kg/s</span>
                    </div>
                    {#if streamProps.composition}
                      <div class="result-item full-width">
                        <span class="result-label">Composition:</span>
                        <span class="result-value composition">{JSON.stringify(streamProps.composition)}</span>
                      </div>
                    {/if}
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {:else}
    <div class="no-results">
      <div class="no-results-icon">📊</div>
      <h3>No Results</h3>
      <p>Run a simulation to see calculation results here</p>
    </div>
  {/if}
</div>

<style>
  .results-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
  }

  .panel-header {
    padding: 20px 16px 16px;
    border-bottom: 1px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .panel-header h2 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
  }

  .panel-header p {
    margin: 0;
    font-size: 12px;
    color: #64748b;
  }

  .results-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .results-section {
    margin-bottom: 24px;
  }

  .results-section:last-child {
    margin-bottom: 0;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
  }

  .section-icon {
    font-size: 16px;
  }

  .section-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
  }

  .results-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .result-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }

  .card-header {
    background: #ffffff;
    padding: 12px 16px;
    border-bottom: 1px solid #e2e8f0;
  }

  .card-header h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
  }

  .card-content {
    padding: 12px 16px;
  }

  .result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
  }

  .result-item:last-child {
    border-bottom: none;
  }

  .result-item.full-width {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .result-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: capitalize;
  }

  .result-value {
    font-size: 12px;
    font-weight: 500;
    color: #1e293b;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  }

  .result-value.composition {
    word-break: break-all;
    line-height: 1.4;
  }

  .no-results {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 40px 20px;
    color: #6b7280;
  }

  .no-results-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .no-results h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }

  .no-results p {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
  }
</style>