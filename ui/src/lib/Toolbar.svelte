<script>
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  function newFlowsheet() {
    dispatch('newFlowsheet')
  }

  function saveFlowsheet() {
    dispatch('saveFlowsheet')
  }

  function loadFlowsheet() {
    dispatch('loadFlowsheet')
  }

  function runSimulation() {
    dispatch('runSimulation')
  }
</script>

<div class="toolbar">
  <div class="toolbar-section">
    <h3 class="section-title">File Operations</h3>
    <div class="toolbar-group">
      <button class="toolbar-btn primary" on:click={newFlowsheet} title="New Flowsheet">
        <span class="btn-icon">📄</span>
        <span class="btn-text">New</span>
      </button>
      <button class="toolbar-btn" on:click={saveFlowsheet} title="Save Flowsheet">
        <span class="btn-icon">💾</span>
        <span class="btn-text">Save</span>
      </button>
      <button class="toolbar-btn" on:click={loadFlowsheet} title="Load Flowsheet">
        <span class="btn-icon">📁</span>
        <span class="btn-text">Load</span>
      </button>
    </div>
  </div>

  <div class="toolbar-section">
    <h3 class="section-title">Simulation</h3>
    <div class="toolbar-group">
      <button class="toolbar-btn success" on:click={runSimulation} title="Run Simulation">
        <span class="btn-icon">▶️</span>
        <span class="btn-text">Run</span>
      </button>
    </div>
  </div>

  <div class="toolbar-section">
    <div class="toolbar-group">
      <div class="status-badge">
        <span class="status-icon">✓</span>
        <span class="status-text">Ready</span>
      </div>
    </div>
  </div>
</div>

<style>
  .toolbar {
    height: 60px;
    background: #ffffff;
    border-bottom: 1px solid #e1e5e9;
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 32px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  .toolbar-section {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .section-title {
    font-size: 10px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0;
  }

  .toolbar-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .toolbar-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: #475569;
    transition: all 0.2s ease;
    min-height: 36px;
  }

  .toolbar-btn:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .toolbar-btn.primary {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
  }

  .toolbar-btn.primary:hover {
    background: #2563eb;
    border-color: #2563eb;
  }

  .toolbar-btn.success {
    background: #10b981;
    color: white;
    border-color: #10b981;
  }

  .toolbar-btn.success:hover {
    background: #059669;
    border-color: #059669;
  }

  .btn-icon {
    font-size: 14px;
  }

  .btn-text {
    font-weight: 500;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    color: #166534;
  }

  .status-icon {
    color: #22c55e;
    font-weight: bold;
  }

  .status-text {
    color: #166534;
  }
</style>