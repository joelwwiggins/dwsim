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
  <div class="toolbar-group">
    <button on:click={newFlowsheet} title="New Flowsheet">
      📄 New
    </button>
    <button on:click={saveFlowsheet} title="Save Flowsheet">
      💾 Save
    </button>
    <button on:click={loadFlowsheet} title="Load Flowsheet">
      📁 Load
    </button>
  </div>

  <div class="toolbar-group">
    <button on:click={runSimulation} title="Run Simulation">
      ▶️ Run
    </button>
  </div>

  <div class="toolbar-group">
    <span class="status">Ready</span>
  </div>
</div>

<style>
  .toolbar {
    height: 40px;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 16px;
  }

  .toolbar-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .toolbar button {
    padding: 6px 12px;
    background: white;
    border: 1px solid #ced4da;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
    transition: background-color 0.1s ease;
  }

  .toolbar button:hover {
    background: #e9ecef;
  }

  .status {
    font-size: 12px;
    color: #6c757d;
    font-weight: 500;
  }
</style>