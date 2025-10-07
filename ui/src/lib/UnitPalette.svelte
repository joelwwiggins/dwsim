<script>
  const unitCategories = [
    {
      title: 'Streams',
      items: [
        { id: 'material_stream', label: 'Material Stream', icon: '🌊', color: '#3498db', description: 'Flow of material with composition' },
        { id: 'energy_stream', label: 'Energy Stream', icon: '⚡', color: '#e74c3c', description: 'Heat or energy transfer' }
      ]
    },
    {
      title: 'Unit Operations',
      items: [
        { id: 'mixer', label: 'Mixer', icon: '🔄', color: '#ff6b6b', description: 'Mix multiple streams' },
        { id: 'heater', label: 'Heater', icon: '🔥', color: '#4ecdc4', description: 'Add heat to stream' },
        { id: 'cooler', label: 'Cooler', icon: '❄️', color: '#74b9ff', description: 'Remove heat from stream' },
        { id: 'valve', label: 'Valve', icon: '⚙️', color: '#45b7d1', description: 'Control flow rate' },
        { id: 'pump', label: 'Pump', icon: '💧', color: '#96ceb4', description: 'Increase pressure' },
        { id: 'splitter', label: 'Splitter', icon: '↗️', color: '#ffeaa7', description: 'Split stream into multiple' },
        { id: 'tank', label: 'Tank', icon: '🪣', color: '#a29bfe', description: 'Liquid storage' },
        { id: 'compressor', label: 'Compressor', icon: '🗜️', color: '#fd79a8', description: 'Gas compression' },
        { id: 'expander', label: 'Expander', icon: '💨', color: '#00b894', description: 'Pressure reduction' },
        { id: 'heat_exchanger', label: 'Heat Exchanger', icon: '🔄', color: '#e17055', description: 'Heat transfer between streams' },
        { id: 'pipe', label: 'Pipe', icon: '📏', color: '#636e72', description: 'Flow conduit' },
        { id: 'vessel', label: 'Vessel', icon: '🏭', color: '#a29bfe', description: 'Process vessel' },
        { id: 'component_separator', label: 'Component Separator', icon: '⚗️', color: '#fdcb6e', description: 'Separate components' },
        { id: 'filter', label: 'Filter', icon: '🔍', color: '#e84393', description: 'Solid-liquid separation' },
        { id: 'orifice_plate', label: 'Orifice Plate', icon: '⭕', color: '#00cec9', description: 'Flow measurement' },
        { id: 'relief_valve', label: 'Relief Valve', icon: '🚨', color: '#d63031', description: 'Pressure relief' }
      ]
    }
  ]

  function onDragStart(event, unitType) {
    event.dataTransfer.setData('unitType', unitType.id)
    event.dataTransfer.effectAllowed = 'copy'
  }
</script>

<div class="unit-palette">
  <div class="palette-header">
    <h2>Components</h2>
    <p>Drag items onto the canvas</p>
  </div>

  <div class="palette-content">
    {#each unitCategories as category}
      <div class="category-section">
        <h3 class="category-title">{category.title}</h3>
        <div class="unit-grid">
          {#each category.items as unitType (unitType.id)}
            <div
              class="unit-item"
              draggable="true"
              ondragstart={(event) => onDragStart(event, unitType)}
              style="background-color: {unitType.color}"
              title="{unitType.label}: {unitType.description}"
              role="button"
              tabindex="0"
              aria-label="Drag {unitType.label} onto canvas: {unitType.description}"
            >
              <div class="unit-icon">{unitType.icon}</div>
              <div class="unit-info">
                <div class="unit-label">{unitType.label}</div>
                <div class="unit-desc">{unitType.description}</div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .unit-palette {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #ffffff;
  }

  .palette-header {
    padding: 20px 16px 16px;
    border-bottom: 1px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .palette-header h2 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
  }

  .palette-header p {
    margin: 0;
    font-size: 12px;
    color: #64748b;
  }

  .palette-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .category-section {
    margin-bottom: 24px;
  }

  .category-section:last-child {
    margin-bottom: 0;
  }

  .category-title {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 12px 0;
    padding-left: 4px;
  }

  .unit-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .unit-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    cursor: grab;
    color: white;
    font-weight: 500;
    transition: all 0.2s ease;
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
  }

  .unit-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.1);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .unit-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .unit-item:hover::before {
    opacity: 1;
  }

  .unit-item:active {
    cursor: grabbing;
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .unit-icon {
    font-size: 20px;
    flex-shrink: 0;
    z-index: 1;
  }

  .unit-info {
    flex: 1;
    z-index: 1;
  }

  .unit-label {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 2px;
  }

  .unit-desc {
    font-size: 11px;
    opacity: 0.9;
    line-height: 1.3;
  }
</style>