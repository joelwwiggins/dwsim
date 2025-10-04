<script>
  const unitTypes = [
    { id: 'mixer', label: 'Mixer', icon: '🔄', color: '#ff6b6b' },
    { id: 'heater', label: 'Heater', icon: '🔥', color: '#4ecdc4' },
    { id: 'cooler', label: 'Cooler', icon: '❄️', color: '#74b9ff' },
    { id: 'valve', label: 'Valve', icon: '⚙️', color: '#45b7d1' },
    { id: 'pump', label: 'Pump', icon: '💧', color: '#96ceb4' },
    { id: 'splitter', label: 'Splitter', icon: '↗️', color: '#ffeaa7' },
    { id: 'tank', label: 'Tank', icon: '🪣', color: '#a29bfe' },
    { id: 'compressor', label: 'Compressor', icon: '🗜️', color: '#fd79a8' },
    { id: 'expander', label: 'Expander', icon: '💨', color: '#00b894' },
    { id: 'heat_exchanger', label: 'Heat Exchanger', icon: '🔄', color: '#e17055' },
    { id: 'pipe', label: 'Pipe', icon: '📏', color: '#636e72' },
    { id: 'vessel', label: 'Vessel', icon: '🏭', color: '#a29bfe' },
    { id: 'component_separator', label: 'Component Separator', icon: '⚗️', color: '#fdcb6e' },
    { id: 'filter', label: 'Filter', icon: '🔍', color: '#e84393' },
    { id: 'orifice_plate', label: 'Orifice Plate', icon: '⭕', color: '#00cec9' },
    { id: 'relief_valve', label: 'Relief Valve', icon: '🚨', color: '#d63031' }
  ]

  function onDragStart(event, unitType) {
    event.dataTransfer.setData('unitType', unitType.id)
    event.dataTransfer.effectAllowed = 'copy'
  }
</script>

<div class="unit-palette">
  <h3>Unit Operations</h3>
  <div class="unit-list">
    {#each unitTypes as unitType (unitType.id)}
      <div
        class="unit-item"
        draggable="true"
        on:dragstart={(event) => onDragStart(event, unitType)}
        style="background-color: {unitType.color}"
      >
        <span class="unit-icon">{unitType.icon}</span>
        <span class="unit-label">{unitType.label}</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .unit-palette {
    width: 200px;
    background: #f8f9fa;
    border-right: 1px solid #e9ecef;
    padding: 16px;
    display: flex;
    flex-direction: column;
  }

  .unit-palette h3 {
    margin: 0 0 16px 0;
    font-size: 14px;
    font-weight: 600;
    color: #495057;
  }

  .unit-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .unit-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: grab;
    color: white;
    font-weight: 500;
    transition: transform 0.1s ease;
  }

  .unit-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .unit-item:active {
    cursor: grabbing;
  }

  .unit-icon {
    font-size: 16px;
  }

  .unit-label {
    font-size: 14px;
  }
</style>