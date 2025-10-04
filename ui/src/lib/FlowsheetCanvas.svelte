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
    valve: { label: 'Valve', color: '#45b7d1', inputs: 1, outputs: 1 },
    pump: { label: 'Pump', color: '#96ceb4', inputs: 1, outputs: 1 },
    splitter: { label: 'Splitter', color: '#ffeaa7', inputs: 1, outputs: 2 }
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
    flowsheetData = { nodes, edges }
    dispatch('flowsheetUpdate', flowsheetData)
  }

  function onDrop(event) {
    event.preventDefault()
    const type = event.dataTransfer.getData('unitType')
    const position = {
      x: event.clientX - event.currentTarget.getBoundingClientRect().left,
      y: event.clientY - event.currentTarget.getBoundingClientRect().top
    }
    createNode(type, position)
  }

  function onDragOver(event) {
    event.preventDefault()
  }

  function onNodeClick(event) {
    const node = event.detail
    dispatch('nodeSelect', { node })
  }

  const nodeTypes = {
    unitNode: UnitNode
  }
</script>

<div class="flowsheet-canvas" on:drop={onDrop} on:dragover={onDragOver}>
  <SvelteFlow
    {nodes}
    {edges}
    {nodeTypes}
    on:nodeClick={onNodeClick}
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