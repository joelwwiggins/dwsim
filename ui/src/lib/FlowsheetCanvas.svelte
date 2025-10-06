<script>
  import { createEventDispatcher } from 'svelte'
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    MiniMap
  } from '@xyflow/svelte'
  import UnitNode from './UnitNode.svelte'

  const dispatch = createEventDispatcher()

  export let flowsheetData = { nodes: [], edges: [] }

  let nodes = $state(flowsheetData.nodes)
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

  function createNode(type, position) {
    const unitType = unitTypes[type]
    const nodeId = `${type}_${Date.now()}`

    const newNode = {
      id: nodeId,
      type: 'unitNode',
      position,
      data: {
        label: unitType.label,
        color: unitType.color,
        inputs: unitType.inputs,
        outputs: unitType.outputs,
        unitType: type
      },
      style: { '--node-color': unitType.color }
    }

    nodes = [...nodes, newNode]
    updateFlowsheet()
  }

  function updateFlowsheet() {
    flowsheetData = { nodes, edges, streams: flowsheetData.streams || [] }
    dispatch('flowsheetUpdate', flowsheetData)
  }

  function onDrop(event) {
    event.preventDefault()
    const type = event.dataTransfer.getData('unitType')
    const rect = event.currentTarget.getBoundingClientRect()
    const position = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    }
    createNode(type, position)
    // Auto-connect to nearby units after creating the node
    autoConnectNode(nodes[nodes.length - 1])
  }

  function autoConnectNode(newNode) {
    const CONNECTION_THRESHOLD = 100 // pixels
    const newNodeData = unitTypes[newNode.data.unitType]

    // Check connections for each existing node
    for (const existingNode of nodes) {
      if (existingNode.id === newNode.id) continue

      const distance = Math.sqrt(
        Math.pow(newNode.position.x - existingNode.position.x, 2) +
        Math.pow(newNode.position.y - existingNode.position.y, 2)
      )

      if (distance < CONNECTION_THRESHOLD) {
        // Check if connection makes sense (output to input)
        const existingData = unitTypes[existingNode.data.unitType]

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
    const node = event.detail
    selectedNode = node
    selectedEdge = null  // Clear edge selection
    dispatch('nodeSelect', { node })
  }

  let connecting = $state(false)
  let connectionStart = $state(null)

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
    unitNode: UnitNode
  }

  let selectedNode = $state(null)
  let selectedEdge = $state(null)
</script>

<div class="flowsheet-canvas" on:drop={onDrop} on:dragover={onDragOver}>
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
  }
</style>