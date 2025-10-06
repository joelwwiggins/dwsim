<script>
  export let results = null
</script>

<div class="results-panel">
  <h3>Simulation Results</h3>
  {#if results}
    <div class="results-content">
      {#if results.unit_operations}
        <div class="section">
          <h4>Unit Operations</h4>
          {#each Object.entries(results.unit_operations) as [unitId, unitResults]}
            <div class="unit-result">
              <h5>{unitId}</h5>
              <div class="properties">
                {#each Object.entries(unitResults) as [key, value]}
                  <div class="property">
                    <span class="key">{key}:</span>
                    <span class="value">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      {/if}

      {#if results.streams}
        <div class="section">
          <h4>Streams</h4>
          {#each Object.entries(results.streams) as [streamId, streamProps]}
            <div class="stream-result">
              <h5>{streamId}</h5>
              <div class="properties">
                <div class="property">
                  <span class="key">Temperature:</span>
                  <span class="value">{streamProps.temperature?.toFixed(2)} K</span>
                </div>
                <div class="property">
                  <span class="key">Pressure:</span>
                  <span class="value">{streamProps.pressure?.toFixed(0)} Pa</span>
                </div>
                <div class="property">
                  <span class="key">Mass Flow:</span>
                  <span class="value">{streamProps.mass_flow_rate?.toFixed(4)} kg/s</span>
                </div>
                {#if streamProps.composition}
                  <div class="property">
                    <span class="key">Composition:</span>
                    <span class="value">{JSON.stringify(streamProps.composition)}</span>
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {:else}
    <div class="no-results">
      Run simulation to see results
    </div>
  {/if}
</div>

<style>
  .results-panel {
    width: 300px;
    background: #f8f9fa;
    border-left: 1px solid #e9ecef;
    padding: 16px;
    overflow-y: auto;
    max-height: 100%;
  }

  .results-panel h3 {
    margin: 0 0 16px 0;
    font-size: 14px;
    font-weight: 600;
    color: #495057;
  }

  .section {
    margin-bottom: 20px;
  }

  .section h4 {
    margin: 0 0 12px 0;
    font-size: 13px;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .unit-result, .stream-result {
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 8px;
  }

  .unit-result h5, .stream-result h5 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
    color: #495057;
  }

  .properties {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .property {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
  }

  .key {
    color: #6c757d;
    font-weight: 500;
  }

  .value {
    color: #495057;
    font-family: monospace;
  }

  .no-results {
    color: #6c757d;
    font-style: italic;
    text-align: center;
    padding: 40px 20px;
  }
</style>