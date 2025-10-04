<script>
  import FlowsheetCanvas from './lib/FlowsheetCanvas.svelte'
  import UnitPalette from './lib/UnitPalette.svelte'
  import PropertyPanel from './lib/PropertyPanel.svelte'
  import Toolbar from './lib/Toolbar.svelte'

  let selectedNode = null
  let flowsheetData = {
    nodes: [],
    edges: []
  }

  const API_BASE = 'http://localhost:8000/api'

  async function loadFlowsheet(data) {
    try {
      const response = await fetch(`${API_BASE}/flowsheet/load`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      const result = await response.json()
      console.log('Load result:', result)
    } catch (error) {
      console.error('Failed to load flowsheet:', error)
    }
  }

  async function runSimulation() {
    try {
      const response = await fetch(`${API_BASE}/simulation/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      const result = await response.json()
      console.log('Simulation result:', result)
    } catch (error) {
      console.error('Failed to run simulation:', error)
    }
  }

  function handleNodeSelect(event) {
    selectedNode = event.detail.node
  }

  function handleFlowsheetUpdate(event) {
    flowsheetData = event.detail
    loadFlowsheet(flowsheetData)
  }

  function handleNewFlowsheet() {
    flowsheetData = { nodes: [], edges: [] }
    selectedNode = null
  }

  function handleSaveFlowsheet() {
    // TODO: Implement save functionality
    console.log('Save flowsheet:', flowsheetData)
  }

  function handleLoadFlowsheet() {
    // TODO: Implement load functionality
    console.log('Load flowsheet')
  }

  function handleRunSimulation() {
    runSimulation()
  }
</script>

<main class="dwsim-app">
  <Toolbar
    on:newFlowsheet={handleNewFlowsheet}
    on:saveFlowsheet={handleSaveFlowsheet}
    on:loadFlowsheet={handleLoadFlowsheet}
    on:runSimulation={handleRunSimulation}
  />
  <div class="workspace">
    <UnitPalette />
    <FlowsheetCanvas
      {flowsheetData}
      on:nodeSelect={handleNodeSelect}
      on:flowsheetUpdate={handleFlowsheetUpdate}
    />
    <PropertyPanel {selectedNode} />
  </div>
</main>

<style>
  .dwsim-app {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .workspace {
    flex: 1;
    display: flex;
  }
</style>
