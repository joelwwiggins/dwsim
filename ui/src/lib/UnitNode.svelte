<script>
  import { Handle, Position } from '@xyflow/svelte'

  let { data, selected = false } = $props()
</script>

<div class="unit-node" class:selected>
  <div class="node-label">{data.label}</div>

  <!-- Input handles -->
  {#each Array(data.inputs) as _, i}
    <Handle
      type="target"
      position={Position.Left}
      id="input-{i}"
      style="top: {20 + i * 20}px"
    />
  {/each}

  <!-- Output handles -->
  {#each Array(data.outputs) as _, i}
    <Handle
      type="source"
      position={Position.Right}
      id="output-{i}"
      style="top: {20 + i * 20}px"
    />
  {/each}
</div>

<style>
  .unit-node {
    background-color: var(--node-color);
    color: white;
    padding: 10px;
    border-radius: 8px;
    border: 2px solid #333;
    min-width: 120px;
    text-align: center;
    font-weight: bold;
    position: relative;
  }

  .unit-node.selected {
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
  }

  .node-label {
    margin-bottom: 8px;
  }
</style>