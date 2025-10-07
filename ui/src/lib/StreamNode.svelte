<script>
  import { Handle, Position } from '@xyflow/svelte'

  let { data, selected = false } = $props()
</script>

<div class="stream-node" class:selected>
  <div class="node-label">{data.label}</div>

  <!-- Input handle (left) -->
  <Handle
    type="target"
    position={Position.Left}
    id="input"
    style="top: 50%"
  />

  <!-- Output handle (right) -->
  <Handle
    type="source"
    position={Position.Right}
    id="output"
    style="top: 50%"
  />
</div>

<style>
  .stream-node {
    background-color: var(--node-color);
    color: white;
    padding: 8px 12px;
    border-radius: 20px;
    border: 2px solid #333;
    min-width: 100px;
    text-align: center;
    font-weight: bold;
    position: relative;
  }

  .stream-node.selected {
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
  }

  .node-label {
    font-size: 12px;
  }
</style>