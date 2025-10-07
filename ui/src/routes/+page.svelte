<script>
  import Header from '../lib/Header.svelte'
  import Toolbar from '../lib/Toolbar.svelte'
  import FlowsheetCanvas from '../lib/FlowsheetCanvas.svelte'
  import UnitPalette from '../lib/UnitPalette.svelte'
  import PropertyPanel from '../lib/PropertyPanel.svelte'
  import ResultsPanel from '../lib/ResultsPanel.svelte'
  import Footer from '../lib/Footer.svelte'

  let selectedNode = null
  let selectedEdge = null
  let simulationResults = null
  let flowsheetData = {
    nodes: [],
    edges: []
  }
  let backendHealthy = true
  let simulationState = 'Idle'

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

  function handleMenuClick(event) {
    const { menuItem } = event.detail
    switch (menuItem) {
      case 'file':
        // Could show file menu dropdown
        console.log('File menu clicked')
        break
      case 'edit':
        console.log('Edit menu clicked')
        break
      case 'view':
        console.log('View menu clicked')
        break
      case 'tools':
        console.log('Tools menu clicked')
        break
      case 'help':
        alert('DWSIM Web Edition\n\nChemical Process Simulation Software\n\nFor help and documentation, visit the project repository.')
        break
    }
  }

  async function pollHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`)
      backendHealthy = res.ok
    } catch (e) {
      backendHealthy = false
    }
  }
  pollHealth()
  const healthInterval = setInterval(pollHealth, 8000)
</script>

<div class="app-container">
  <Header on:menuClick={handleMenuClick} />
  <Toolbar
    on:newFlowsheet={handleNewFlowsheet}
    on:saveFlowsheet={handleSaveFlowsheet}
    on:loadFlowsheet={handleLoadFlowsheet}
    on:runSimulation={handleRunSimulation}
  />
  <main class="main-content">
    <aside class="sidebar-left">
      <UnitPalette />
    </aside>

    <section class="canvas-area">
      <FlowsheetCanvas
        {flowsheetData}
        on:nodeSelect={handleNodeSelect}
        on:edgeSelect={handleEdgeSelect}
        on:flowsheetUpdate={handleFlowsheetUpdate}
      />
    </section>

    <aside class="sidebar-right">
      <PropertyPanel {selectedNode} {selectedEdge} {flowsheetData} on:updateNode={handleUpdateNode} on:updateStream={handleUpdateStream} />
      <ResultsPanel {simulationResults} />
    </aside>
  </main>
  <Footer {backendHealthy} {simulationState} />
</div>

<style>
  .app-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f8fafc;
  }

  .main-content {
    flex: 1;
    display: flex;
    overflow: hidden;
  }

  .sidebar-left {
    width: 220px;
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
  }

  .canvas-area {
    flex: 1;
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
  }

  .sidebar-right {
    width: 320px;
    background: #ffffff;
    border-left: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .sidebar-right > :global(*) {
    flex: 1;
    min-height: 0;
  }
</style>
