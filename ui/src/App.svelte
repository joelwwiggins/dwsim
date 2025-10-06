<script>
  import FlowsheetCanvas from './lib/FlowsheetCanvas.svelte'
  import UnitPalette from './lib/UnitPalette.svelte'
  import PropertyPanel from './lib/PropertyPanel.svelte'
  import ResultsPanel from './lib/ResultsPanel.svelte'
  import Toolbar from './lib/Toolbar.svelte'

  let selectedNode = null
  let selectedEdge = null
  let simulationResults = null
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
      if (result.success) {
        simulationResults = result.results
      } else {
        simulationResults = null
        alert(`Simulation failed: ${result.message}`)
      }
    } catch (error) {
      console.error('Failed to run simulation:', error)
      simulationResults = null
      alert('Failed to run simulation')
    }
  }

  function handleNodeSelect(event) {
    selectedNode = event.detail.node
    selectedEdge = null
  }

  function handleEdgeSelect(event) {
    selectedEdge = event.detail.edge
    selectedNode = null
  }

  function handleUpdateNode(event) {
    const { nodeId, key, value } = event.detail
    // Update node data in flowsheet
    const node = flowsheetData.nodes.find(n => n.id === nodeId)
    if (node) {
      node.data[key] = value
      handleFlowsheetUpdate({ detail: flowsheetData })
    }
  }

  function handleUpdateStream(event) {
    const { streamId, key, value } = event.detail
    // Update stream data in flowsheet
    const stream = flowsheetData.streams.find(s => s.id === streamId)
    if (stream) {
      stream[key] = value
      handleFlowsheetUpdate({ detail: flowsheetData })
    }
  }

  function handleFlowsheetUpdate(event) {
    flowsheetData = event.detail
    loadFlowsheet(flowsheetData)
  }

  function handleNewFlowsheet() {
    flowsheetData = { nodes: [], edges: [] }
    selectedNode = null
    selectedEdge = null
  }

  async function handleSaveFlowsheet() {
    try {
      const response = await fetch(`${API_BASE}/flowsheet/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(flowsheetData)
      })
      const result = await response.json()
      if (result.success) {
        alert(`Flowsheet saved as ${result.filename}`)
      } else {
        alert(`Save failed: ${result.message}`)
      }
    } catch (error) {
      console.error('Failed to save flowsheet:', error)
      alert('Failed to save flowsheet')
    }
  }

  async function handleLoadFlowsheet() {
    try {
      // First get list of available flowsheets
      const listResponse = await fetch(`${API_BASE}/flowsheet/list`)
      const listResult = await listResponse.json()
      
      if (listResult.flowsheets.length === 0) {
        alert('No saved flowsheets found')
        return
      }
      
      // For now, load the most recent one
      const mostRecent = listResult.flowsheets.sort((a, b) => 
        new Date(b.modified) - new Date(a.modified)
      )[0]
      
      const response = await fetch(`${API_BASE}/flowsheet/load-file?filename=${encodeURIComponent(mostRecent.filename)}`)
      const result = await response.json()
      
      if (result.success) {
        flowsheetData = result.flowsheet
        selectedNode = null
        selectedEdge = null
        simulationResults = null
        alert(`Loaded flowsheet: ${mostRecent.filename}`)
      } else {
        alert(`Load failed: ${result.message}`)
      }
    } catch (error) {
      console.error('Failed to load flowsheet:', error)
      alert('Failed to load flowsheet')
    }
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
      on:edgeSelect={handleEdgeSelect}
      on:flowsheetUpdate={handleFlowsheetUpdate}
    />
    <PropertyPanel {selectedNode} {selectedEdge} {flowsheetData} on:updateNode={handleUpdateNode} on:updateStream={handleUpdateStream} />
    <ResultsPanel {simulationResults} />
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
