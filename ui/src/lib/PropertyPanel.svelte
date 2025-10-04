<script>
  export let selectedNode = null

  let properties = {}

  $: if (selectedNode) {
    // Initialize properties based on node type
    properties = getDefaultProperties(selectedNode.data.type)
  }

  function getDefaultProperties(type) {
    const defaults = {
      mixer: {
        pressureDrop: 0,
        efficiency: 100
      },
      heater: {
        duty: 0,
        outletTemperature: 298.15
      },
      cooler: {
        duty: 0,
        outletTemperature: 298.15
      },
      valve: {
        pressureDrop: 0,
        cv: 1.0
      },
      pump: {
        head: 10,
        efficiency: 75
      },
      splitter: {
        splitRatio: 0.5
      },
      tank: {
        volume: 1.0,
        initialLevel: 0.5
      },
      compressor: {
        pressureRatio: 2.0,
        efficiency: 75
      },
      expander: {
        pressureRatio: 0.5,
        efficiency: 75
      },
      heat_exchanger: {
        duty: 0,
        ua: 100
      },
      pipe: {
        length: 10,
        diameter: 0.1
      },
      vessel: {
        volume: 1.0,
        pressure: 101325
      },
      component_separator: {
        splitRatio: 0.5
      },
      filter: {
        pressureDrop: 0
      },
      orifice_plate: {
        beta: 0.5
      },
      relief_valve: {
        setPressure: 200000
      }
    }
    return defaults[type] || {}
  }

  function updateProperty(key, value) {
    properties[key] = value
    // Here we would update the node data and notify the backend
  }
</script>

<div class="property-panel">
  <h3>Properties</h3>
  {#if selectedNode}
    <div class="properties">
      <div class="property-group">
        <h4>General</h4>
        <div class="property-item">
          <label>Name:</label>
          <input type="text" bind:value={selectedNode.data.label} />
        </div>
        <div class="property-item">
          <label>Type:</label>
          <span>{selectedNode.type}</span>
        </div>
        <div class="property-item">
          <label>ID:</label>
          <span>{selectedNode.id}</span>
        </div>
      </div>

      <div class="property-group">
        <h4>Connections</h4>
        <div class="property-item">
          <label>Inputs:</label>
          <span>{selectedNode.data.inputs}</span>
        </div>
        <div class="property-item">
          <label>Outputs:</label>
          <span>{selectedNode.data.outputs}</span>
        </div>
      </div>

      <div class="property-group">
        <h4>Position</h4>
        <div class="property-item">
          <label>X:</label>
          <span>{Math.round(selectedNode.position.x)}</span>
        </div>
        <div class="property-item">
          <label>Y:</label>
          <span>{Math.round(selectedNode.position.y)}</span>
        </div>
      </div>

      <div class="property-group">
        <h4>Node Specific</h4>
        {#each Object.entries(properties) as [key, value]}
          <div class="property-item">
            <label for={key}>{key.replace(/([A-Z])/g, ' $1').toLowerCase()}</label>
            <input
              id={key}
              type="number"
              bind:value
              on:input={() => updateProperty(key, value)}
            />
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="no-selection">
      Select a unit operation to view its properties
    </div>
  {/if}
</div>

<style>
  .property-panel {
    width: 250px;
    background: #f8f9fa;
    border-left: 1px solid #e9ecef;
    padding: 16px;
    overflow-y: auto;
  }

  .property-panel h3 {
    margin: 0 0 16px 0;
    font-size: 14px;
    font-weight: 600;
    color: #495057;
  }

  .properties {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .property-group {
    border-bottom: 1px solid #e9ecef;
    padding-bottom: 12px;
  }

  .property-group:last-child {
    border-bottom: none;
  }

  .property-group h4 {
    margin: 0 0 8px 0;
    font-size: 12px;
    font-weight: 600;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .property-item {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }

  .property-item label {
    min-width: 60px;
    font-size: 12px;
    color: #495057;
    font-weight: 500;
  }

  .property-item input {
    flex: 1;
    padding: 4px 8px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 12px;
  }

  .property-item span {
    font-size: 12px;
    color: #6c757d;
  }

  .no-selection {
    color: #6c757d;
    font-style: italic;
    text-align: center;
    padding: 40px 20px;
  }
</style>