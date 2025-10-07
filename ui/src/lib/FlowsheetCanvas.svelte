<script>
import StreamPropertyDialog from "./StreamPropertyDialog.svelte";
import UnitConfigWizard from "./UnitConfigWizard.svelte";
import ResultsVisualization from "./ResultsVisualization.svelte";
  import { createEventDispatcher } from 'svelte'
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    MiniMap
  } from '@xyflow/svelte'
  import UnitNode from './UnitNode.svelte'
  import StreamNode from './StreamNode.svelte'

  const dispatch = createEventDispatcher()

  let { flowsheetData = { nodes: [], edges: [] } } = $props()

  let nodes = $state(flowsheetData.nodes)
  let edges = $state(flowsheetData.edges)

  // Undo/Redo functionality
  let history = $state([])
  let historyIndex = $state(-1)

  // Context menu
  let contextMenu = $state({ visible: false, x: 0, y: 0, target: null })

  // Dialogs
  let streamDialog = $state({ open: false, streamData: null })
  let unitWizard = $state({ open: false, unitType: "", config: {} })
  let resultsPanel = $state({ visible: false, results: null, unitType: "", unitId: "" })

  // Keyboard shortcuts
  let keysPressed = $state(new Set())
  let edges = $state(flowsheetData.edges)

  // Unit operation types and their default properties
  const unitTypes = {
    mixer: { label: 'Mixer', color: '#ff6b6b', inputs: 2, outputs: 1 },
    heater: { label: 'Heater', color: '#4ecdc4', inputs: 1, outputs: 1 },
    cooler: { label: 'Cooler', color: '#74b9ff', inputs: 1, outputs: 1 },
    valve: { label: 'Valve', color: '#45b7d1', inputs: 1, outputs: 1 },
    pump: { label: 'Pump', color: '#96ceb4', inputs: 1, outputs: 1 },
    splitter: { label: 'Splitter', color: '#ffeaa7', inputs: 1, outputs: 2 },
    tank: { label: 'Tank', color: '#a29bfe', inputs: 1, outputs: 1 },
    compressor: { label: 'Compressor', color: '#fd79a8', inputs: 1, outputs: 1 },
    expander: { label: 'Expander', color: '#00b894', inputs: 1, outputs: 1 },
    heat_exchanger: { label: 'Heat Exchanger', color: '#e17055', inputs: 2, outputs: 2 },
    pipe: { label: 'Pipe', color: '#636e72', inputs: 1, outputs: 1 },
    vessel: { label: 'Vessel', color: '#a29bfe', inputs: 1, outputs: 1 },
    component_separator: { label: 'Component Separator', color: '#fdcb6e', inputs: 1, outputs: 2 },
    filter: { label: 'Filter', color: '#e84393', inputs: 1, outputs: 1 },
    orifice_plate: { label: 'Orifice Plate', color: '#00cec9', inputs: 1, outputs: 1 },
    relief_valve: { label: 'Relief Valve', color: '#d63031', inputs: 1, outputs: 1 }
  }

  // Stream types
  const streamTypes = {
    material_stream: { label: 'Material Stream', color: '#2d3436', inputs: 1, outputs: 1 },
    energy_stream: { label: 'Energy Stream', color: '#e17055', inputs: 1, outputs: 1 }
  }

  function createNode(type, position) {
    let nodeType = 'unitNode'
    let typeData
    let objectType = 'unit_operation'

    if (unitTypes[type]) {
      typeData = unitTypes[type]
    } else if (streamTypes[type]) {
      typeData = streamTypes[type]
      nodeType = 'streamNode'
      objectType = 'stream'
    } else {
      console.error(`Unknown node type: ${type}`)
      return
    }

    const nodeId = `${type}_${Date.now()}`

    const newNode = {
      id: nodeId,
      type: nodeType,
      position,
      data: {
        label: typeData.label,
        color: typeData.color,
        inputs: typeData.inputs,
        outputs: typeData.outputs,
        unitType: type
      },
      style: { '--node-color': typeData.color }
    }

    // Add to local nodes immediately for UI responsiveness
    nodes = [...nodes, newNode]
    updateFlowsheet()

    // Call backend API to add the object
    const apiData = {
      type: objectType,
      id: nodeId,
      data: {
        unitType: type,
        name: typeData.label
      }
    }

    // Add stream-specific properties
    if (objectType === 'stream') {
      if (type === 'material_stream') {
        apiData.data.temperature = 298.15
        apiData.data.pressure = 101325
        apiData.data.mass_flow_rate = 0.0
        apiData.data.composition = {}
      } else if (type === 'energy_stream') {
        apiData.data.energy_flow = 0.0  // Watts
        apiData.data.temperature_low = 0.0
        apiData.data.temperature_high = 2000.0
      }
    }

    fetch('/api/flowsheet/add-object', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(apiData)
    })
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        console.error('Failed to add object to backend:', data.message)
        // Remove from local nodes if backend failed
        nodes = nodes.filter(node => node.id !== nodeId)
        updateFlowsheet()
      }
    })
    .catch(error => {
      console.error('Error adding object:', error)
      // Remove from local nodes if API call failed
      nodes = nodes.filter(node => node.id !== nodeId)
      updateFlowsheet()
    })
  }

  function updateFlowsheet() {
    flowsheetData = { nodes, edges, streams: flowsheetData.streams || [] }
    dispatch('flowsheetUpdate', flowsheetData)
  }

  function onDrop(event) {
    event.preventDefault()
    const type = event.dataTransfer.getData('unitType')
    if (!type) return

    // Prefer XYFlow's internal transform if available
    const flowEl = event.currentTarget
    const bounds = flowEl.getBoundingClientRect()
    const position = {
      x: (event.clientX - bounds.left),
      y: (event.clientY - bounds.top)
    }

    createNode(type, position)
  }

  function autoConnectNode(newNode) {
    const CONNECTION_THRESHOLD = 100 // pixels
    const newNodeData = unitTypes[newNode.data.unitType] || streamTypes[newNode.data.unitType]

    // Check connections for each existing node
    for (const existingNode of nodes) {
      if (existingNode.id === newNode.id) continue

      const distance = Math.sqrt(
        Math.pow(newNode.position.x - existingNode.position.x, 2) +
        Math.pow(newNode.position.y - existingNode.position.y, 2)
      )

      if (distance < CONNECTION_THRESHOLD) {
        // Check if connection makes sense (output to input)
        const existingData = unitTypes[existingNode.data.unitType] || streamTypes[existingNode.data.unitType]

        // Simple auto-connection logic: connect if one has output and other has input
        if (newNodeData.outputs > 0 && existingData.inputs > 0) {
          // Connect new node output to existing node input
          createAutoConnection(newNode.id, existingNode.id, 'output', 'input')
        } else if (existingData.outputs > 0 && newNodeData.inputs > 0) {
          // Connect existing node output to new node input
          createAutoConnection(existingNode.id, newNode.id, 'output', 'input')
        }
      }
    }
  }

  function createAutoConnection(sourceId, targetId, sourceHandle, targetHandle) {
    const edgeId = `edge_${sourceId}_${targetId}_${Date.now()}`
    const newEdge = {
      id: edgeId,
      source: sourceId,
      target: targetId,
      sourceHandle,
      targetHandle,
      type: 'default'
    }

    // Check if edge already exists
    const edgeExists = edges.some(edge =>
      edge.source === sourceId && edge.target === targetId
    )

    if (!edgeExists) {
      edges = [...edges, newEdge]
    saveToHistory()
    dispatch("flowsheetUpdate", { nodes, edges })

      // Add default stream data
      const streamData = {
        id: newEdge.id,
        name: `Stream ${newEdge.id}`,
        temperature: 298.15,
        pressure: 101325,
        mass_flow_rate: 0.0,
        composition: {}
      }

      if (!flowsheetData.streams) {
        flowsheetData.streams = []
      }
      flowsheetData.streams = [...flowsheetData.streams, streamData]

      updateFlowsheet()
    }
  }
  function onDragOver(event) {
    event.preventDefault()
  }

  function onNodeClick(event) {
    if (event.detail.event?.button === 2) { // Right click
      showContextMenu(event.detail.event, { type: "unit", data: event.detail })
      return
    }
    const node = event.detail
    selectedNode = node
    selectedEdge = null  // Clear edge selection
    dispatch('nodeSelect', { node })
  }

  let connecting = $state(false)
  let connectionStart = $state(null)

  // Undo/Redo functionality
  function saveToHistory() {
    const state = { nodes: [...nodes], edges: [...edges] }
    history = history.slice(0, historyIndex + 1)
    history.push(JSON.parse(JSON.stringify(state)))
    historyIndex = history.length - 1
    if (history.length > 50) { // Limit history size
      history = history.slice(-50)
      historyIndex = history.length - 1
    }
  }

  function undo() {
    if (historyIndex > 0) {
      historyIndex--
      const state = history[historyIndex]
      nodes = JSON.parse(JSON.stringify(state.nodes))
      edges = JSON.parse(JSON.stringify(state.edges))
      dispatch("flowsheetUpdate", { nodes, edges })
    }
  }

  function redo() {
    if (historyIndex < history.length - 1) {
      historyIndex++
      const state = history[historyIndex]
      nodes = JSON.parse(JSON.stringify(state.nodes))
      edges = JSON.parse(JSON.stringify(state.edges))
      dispatch("flowsheetUpdate", { nodes, edges })
    }
  }

  // Context menu functions
  function showContextMenu(event, target) {
    event.preventDefault()
    contextMenu = {
      visible: true,
      x: event.clientX,
      y: event.clientY,
      target
    }
  }

  function hideContextMenu() {
    contextMenu = { visible: false, x: 0, y: 0, target: null }
  }

  function handleContextMenuAction(action) {
    if (!contextMenu.target) return

    const { type, data } = contextMenu.target

    switch (action) {
      case "configure":
        if (type === "unit") {
          unitWizard = { open: true, unitType: data.type, config: data }
        }
        break
      case "properties":
        if (type === "stream") {
          streamDialog = { open: true, streamData: data }
        }
        break
      case "results":
        if (type === "unit") {
          // In a real implementation, this would fetch results from the backend
          resultsPanel = { visible: true, results: {}, unitType: data.type, unitId: data.id }
        }
        break
      case "delete":
        if (type === "unit") {
          nodes = nodes.filter(n => n.id !== data.id)
          edges = edges.filter(e => e.source !== data.id && e.target !== data.id)
        } else if (type === "stream") {
          edges = edges.filter(e => e.id !== data.id)
        }
        dispatch("flowsheetUpdate", { nodes, edges })
        break
    }

    hideContextMenu()
  }

  // Keyboard event handlers
  function handleKeyDown(event) {
    keysPressed.add(event.key.toLowerCase())

    if (keysPressed.has("control") || keysPressed.has("meta")) {
      if (event.key.toLowerCase() === "z" && !keysPressed.has("shift")) {
        event.preventDefault()
        undo()
      } else if ((event.key.toLowerCase() === "y") || (event.key.toLowerCase() === "z" && keysPressed.has("shift"))) {
        event.preventDefault()
        redo()
      }
    }

    if (event.key === "Delete" || event.key === "Backspace") {
      // Delete selected items
      // Implementation would go here
    }
  }

  function handleKeyUp(event) {
    keysPressed.delete(event.key.toLowerCase())
  }
  function onConnect(event) {
    const { source, target, sourceHandle, targetHandle } = event.detail
    const newEdge = {
      id: `edge_${source}_${target}_${Date.now()}`,
      source,
      target,
      sourceHandle,
      targetHandle,
      type: 'default'
    }
    edges = [...edges, newEdge]
    saveToHistory()
    dispatch("flowsheetUpdate", { nodes, edges })

    // Add default stream data
    const streamData = {
      id: newEdge.id,
      name: `Stream ${newEdge.id}`,
      temperature: 298.15,
      pressure: 101325,
      mass_flow_rate: 0.0,
      composition: {}
    }

    if (!flowsheetData.streams) {
      flowsheetData.streams = []
    }
    flowsheetData.streams = [...flowsheetData.streams, streamData]

    updateFlowsheet()
  }

  function onConnectStart(event) {
    connecting = true
    connectionStart = event.detail
  }

  function onConnectEnd(event) {
    connecting = false
    connectionStart = null
  }

  function onEdgeClick(event) {
    if (event.detail.event?.button === 2) { // Right click
      showContextMenu(event.detail.event, { type: "stream", data: event.detail })
      return
    }
    selectedEdge = event.detail
    selectedNode = null  // Clear node selection
    dispatch('edgeSelect', { edge: selectedEdge })
  }

  function onEdgeDelete(event) {
    const edgeId = event.detail
    edges = edges.filter(edge => edge.id !== edgeId)
    updateFlowsheet()
  }

  const nodeTypes = {
    unitNode: UnitNode,
    streamNode: StreamNode
  }

  let selectedNode = $state(null)
  let selectedEdge = $state(null)
</script>
<!-- Context Menu -->
{#if contextMenu.visible}
  <div 
    class="context-menu" 
    style="left: {contextMenu.x}px; top: {contextMenu.y}px" 
    on:click|stopPropagation={hideContextMenu}
  >
    {#if contextMenu.target?.type === "unit"}
      <div class="context-menu-item" onclick={() => handleContextMenuAction("configure")}>Configure</div>
      <div class="context-menu-item" onclick={() => handleContextMenuAction("results")}>View Results</div>
      <div class="context-menu-separator"></div>
      <div class="context-menu-item delete" onclick={() => handleContextMenuAction("delete")}>Delete</div>
    {:else if contextMenu.target?.type === "stream"}
      <div class="context-menu-item" onclick={() => handleContextMenuAction("properties")}>Properties</div>
      <div class="context-menu-separator"></div>
      <div class="context-menu-item delete" onclick={() => handleContextMenuAction("delete")}>Delete</div>
    {/if}
  </div>
{/if}

<!-- Dialogs -->
<StreamPropertyDialog 
  isOpen={streamDialog.open} 
  streamData={streamDialog.streamData} 
  onSave={(data) => {
    streamDialog = { open: false, streamData: null }
    // Update stream data in flowsheet
    dispatch("updateStream", { streamId: streamDialog.streamData.id, data })
  }} 
  onCancel={() => streamDialog = { open: false, streamData: null }} 
/>

<UnitConfigWizard 
  isOpen={unitWizard.open} 
  unitType={unitWizard.unitType} 
  currentConfig={unitWizard.config} 
  onSave={(config) => {
    unitWizard = { open: false, unitType: "", config: {} }
    // Update unit configuration
    dispatch("updateUnit", { unitId: unitWizard.config.id, config })
  }} 
  onCancel={() => unitWizard = { open: false, unitType: "", config: {} }} 
/>

{#if resultsPanel.visible}
  <div class="results-modal-overlay" onclick={() => resultsPanel = { visible: false, results: null, unitType: "", unitId: "" }}> 
    <div class="results-modal" onclick={(e) => e.stopPropagation()}> 
      <div class="results-modal-header"> 
        <h3>Results for {resultsPanel.unitType} ({resultsPanel.unitId})</h3> 
        <button onclick={() => resultsPanel = { visible: false, results: null, unitType: "", unitId: "" }}>×</button> 
      </div> 
      <ResultsVisualization results={resultsPanel.results} unitType={resultsPanel.unitType} unitId={resultsPanel.unitId} /> 
    </div> 
  </div> 
{/if}

<svelte:window on:keydown={handleKeyDown} on:keyup={handleKeyUp} on:click={hideContextMenu} />
<div class="flowsheet-canvas">
  <SvelteFlow
    {nodes}
    {edges}
    {nodeTypes}
    on:nodeClick={onNodeClick}
    on:connect={onConnect}
    on:connectStart={onConnectStart}
    on:connectEnd={onConnectEnd}
    on:edgeClick={onEdgeClick}
    on:edgeDelete={onEdgeDelete}
    ondrop={onDrop}
    ondragover={onDragOver}
    fitViewOnInit={true}
  >
    <Controls />
    <Background variant={BackgroundVariant.Dots} />
    <MiniMap />
  </SvelteFlow>
</div>

<style>
  .flowsheet-canvas {
    flex: 1;
    height: 100%;
    background: #ffffff;
    border-radius: 0;
  }
</style>\
  /* Context Menu Styles */\
  .context-menu {\
    position: fixed;\
    background: white;\
    border: 1px solid #d1d5db;\
    border-radius: 6px;\
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);\
    z-index: 1000;\
    min-width: 160px;\
    overflow: hidden;\
  }\
\
  .context-menu-item {\
    padding: 8px 16px;\
    cursor: pointer;\
    font-size: 14px;\
    color: #374151;\
    transition: background-color 0.2s;\
  }\
\
  .context-menu-item:hover {\
    background-color: #f3f4f6;\
  }\
\
  .context-menu-item.delete {\
    color: #dc2626;\
  }\
\
  .context-menu-item.delete:hover {\
    background-color: #fef2f2;\
  }\
\
  .context-menu-separator {\
    height: 1px;\
    background-color: #e5e7eb;\
    margin: 4px 0;\
  }\
\
  /* Results Modal Styles */\
  .results-modal-overlay {\
    position: fixed;\
    top: 0;\
    left: 0;\
    right: 0;\
    bottom: 0;\
    background: rgba(0, 0, 0, 0.5);\
    display: flex;\
    align-items: center;\
    justify-content: center;\
    z-index: 1000;\
  }\
\
  .results-modal {\
    background: white;\
    border-radius: 8px;\
    max-width: 800px;\
    width: 90%;\
    max-height: 80vh;\
    overflow: hidden;\
    display: flex;\
    flex-direction: column;\
  }\
\
  .results-modal-header {\
    display: flex;\
    justify-content: space-between;\
    align-items: center;\
    padding: 20px;\
    border-bottom: 1px solid #e5e7eb;\
  }\
\
  .results-modal-header h3 {\
    margin: 0;\
    font-size: 18px;\
    font-weight: 600;\
  }\
\
  .results-modal-header button {\
    background: none;\
    border: none;\
    font-size: 24px;\
    cursor: pointer;\
    color: #6b7280;\
    padding: 0;\
    width: 30px;\
    height: 30px;\
    display: flex;\
    align-items: center;\
    justify-content: center;\
  }
