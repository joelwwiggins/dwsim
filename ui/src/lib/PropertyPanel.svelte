<script>
  import { createEventDispatcher } from 'svelte'
  
  let { selectedNode = null, selectedEdge = null, flowsheetData = null } = $props()

  const dispatch = createEventDispatcher()

  let properties = $state({})
  let streamProperties = $state({})

  $effect(() => {
    if (selectedNode) {
      // Initialize properties based on node type
      properties = getDefaultProperties(selectedNode.data.type)
    }
  })

  $effect(() => {
    if (selectedEdge) {
      // Initialize stream properties from flowsheet data
      streamProperties = getDefaultStreamProperties()
      // Try to find existing stream data
      const streamData = findStreamData(selectedEdge.id)
      if (streamData) {
        streamProperties = { ...streamProperties, ...streamData }
      }
    }
  })

  // Create a derived value for composition string
  let compositionString = $derived(streamProperties.composition ? JSON.stringify(streamProperties.composition, null, 2) : '{}')

  function findStreamData(edgeId) {
    if (flowsheetData && flowsheetData.streams) {
      return flowsheetData.streams.find(stream => stream.id === edgeId)
    }
    return null
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
        efficiency: 0.95
      },
      filter: {
        pressureDrop: 0
      },
      orifice_plate: {
        beta: 0.5
      },
      relief_valve: {
      absorption_column: {
        numberOfStages: 10,
        feedStage: 1,
        solventFlowRate: 1.0,
        absorptionEfficiency: 0.95,
        feedPressure: 101325,
        columnPressureDrop: 0,
        targetComponent: "CO2"
      },
      stripping_column: {
        numberOfStages: 10,
        feedStage: 5,
        strippingGasFlowRate: 0.5,
        strippingEfficiency: 0.95,
        feedPressure: 101325,
        columnPressureDrop: 0,
        targetComponent: "CO2"
      },
      condenser: {
        condenserType: "total",
        condenserPressure: 101325,
        condenserTemperature: null,
        heatDuty: null,
        vaporFraction: 0.0,
        overallHeatTransferCoeff: 500.0,
        heatTransferArea: null,
        pressureDrop: 10000
      },
      reboiler: {
        reboilerType: "kettle",
        reboilerPressure: 101325,
        reboilerTemperature: null,
        heatDuty: null,
        vaporFraction: 0.1,
        overallHeatTransferCoeff: 1000.0,
        heatTransferArea: null,
        pressureDrop: 5000
      }
        setPressure: 200000
      }
    }
    return defaults[type] || {}
  }

  function getDefaultStreamProperties() {
    return {
      temperature: 298.15,
      pressure: 101325,
      massFlowRate: 0.0,
    }
  }
  
  function updateProperty(key, value) {
    properties[key] = value
    // Dispatch event to update node data
    dispatch('updateNode', { nodeId: selectedNode.id, key, value })
  }

  function updateComposition() {
    try {
      const parsed = JSON.parse(compositionString)
      streamProperties.composition = parsed
      updateStreamProperty("composition", parsed)
    } catch (e) {
      // Invalid JSON, keep current value
    }
  }
  function updateStreamProperty(key, value) {
    streamProperties[key] = value
    // Dispatch event to update stream data
    dispatch('updateStream', { streamId: selectedEdge.id, key, value })
  }
</script>

<div class="property-panel">
  <div class="panel-header">
    <h2>Properties</h2>
    <p>Configure selected item</p>
  </div>

  {#if selectedNode}
    <div class="properties-content">
      <div class="item-header">
        <div class="item-icon" style="background-color: {selectedNode.data.color || '#64748b'}">
          {selectedNode.data.label?.charAt(0) || 'U'}
        </div>
        <div class="item-info">
          <h3>{selectedNode.data.label || 'Unit Operation'}</h3>
          <p>{selectedNode.data.unitType || 'Unknown'}</p>
        </div>
      </div>

      <div class="properties-section">
        <h4>General</h4>
        <div class="property-grid">
          <div class="property-item">
            <label for="node-name">Name</label>
            <input
              id="node-name"
              type="text"
              value={selectedNode.data.label || ''}
              placeholder="Enter name"
            />
          </div>
        </div>
      </div>

      <div class="properties-section">
        <h4>Node Specific</h4>
        <div class="property-grid">
          {#each Object.entries(properties) as [key, value]}
            <div class="property-item">
              <label for={key}>{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</label>
              <input
                id={key}
                type="number"
                bind:value={properties[key]}
                oninput={() => updateProperty(key, properties[key])}
                step="any"
              />
            </div>
          {/each}
        </div>
      </div>
    </div>
  {:else if selectedEdge}
    <div class="properties-content">
      <div class="item-header">
        <div class="item-icon" style="background-color: #64748b">
          🔗
        </div>
        <div class="item-info">
          <h3>Stream Connection</h3>
          <p>{selectedEdge.source} → {selectedEdge.target}</p>
        </div>
      </div>

      <div class="properties-section">
        <h4>Stream Properties</h4>
        <div class="property-grid">
          {#if streamProperties.stream_type === 'energy'}
            <div class="property-item">
              <label for="energy-flow">Energy Flow (kW)</label>
              <input
                id="energy-flow"
                type="number"
                bind:value={streamProperties.energy_flow_kw}
                oninput={() => updateStreamProperty('energy_flow_kw', streamProperties.energy_flow_kw)}
                step="0.01"
              />
            </div>
            <div class="property-item">
              <label for="temp-low">Temperature Low (K)</label>
              <input
                id="temp-low"
                type="number"
                bind:value={streamProperties.temperature_low}
                oninput={() => updateStreamProperty('temperature_low', streamProperties.temperature_low)}
                step="0.1"
              />
            </div>
            <div class="property-item">
              <label for="temp-high">Temperature High (K)</label>
              <input
                id="temp-high"
                type="number"
                bind:value={streamProperties.temperature_high}
                oninput={() => updateStreamProperty('temperature_high', streamProperties.temperature_high)}
                step="0.1"
              />
            </div>
          {:else}
            <div class="property-item">
              <label for="temperature">Temperature (K)</label>
              <input
                id="temperature"
                type="number"
                bind:value={streamProperties.temperature}
                oninput={() => updateStreamProperty('temperature', streamProperties.temperature)}
                step="0.01"
              />
            </div>
            <div class="property-item">
              <label for="pressure">Pressure (Pa)</label>
              <input
                id="pressure"
                type="number"
                bind:value={streamProperties.pressure}
                oninput={() => updateStreamProperty('pressure', streamProperties.pressure)}
                step="100"
              />
            </div>
            <div class="property-item">
              <label for="mass-flow">Mass Flow (kg/s)</label>
              <input
                id="mass-flow"
                type="number"
                bind:value={streamProperties.mass_flow_rate}
                oninput={() => updateStreamProperty('mass_flow_rate', streamProperties.mass_flow_rate)}
                step="0.0001"
              />
            </div>
            <div class="property-item full-width">
              <label for="composition">Composition</label>
              <textarea
                id="composition"
                bind:value={compositionString}
                oninput={() => updateComposition()}
                rows="4"
                placeholder='{"component1": 0.5, "component2": 0.5}'
              ></textarea>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {:else}
    <div class="no-selection">
      <div class="no-selection-icon">📋</div>
      <h3>No Selection</h3>
      <p>Select a unit operation or stream to view and edit its properties</p>
    </div>
  {/if}
</div>

<style>
  .property-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    border-left: 1px solid #e2e8f0;
  }

  .panel-header {
    padding: 20px 16px 16px;
    border-bottom: 1px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  }

  .panel-header h2 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
  }

  .panel-header p {
    margin: 0;
    font-size: 12px;
    color: #64748b;
  }

  .properties-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .item-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid #e2e8f0;
  }

  .item-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: 600;
  }

  .item-info h3 {
    margin: 0 0 2px 0;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
  }

  .item-info p {
    margin: 0;
    font-size: 12px;
    color: #64748b;
  }

  .properties-section {
    margin-bottom: 24px;
  }

  .properties-section h4 {
    margin: 0 0 12px 0;
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .property-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .property-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .property-item.full-width {
    /* Full width for textarea */
  }

  .property-item label {
    font-size: 12px;
    font-weight: 600;
    color: #374151;
    text-transform: capitalize;
  }

  .property-item input,
  .property-item textarea {
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 13px;
    background: #ffffff;
    transition: border-color 0.2s ease;
  }

  .property-item input:focus,
  .property-item textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .property-item textarea {
    resize: vertical;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    line-height: 1.4;
  }

  .no-selection {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 40px 20px;
    color: #6b7280;
  }

  .no-selection-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .no-selection h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }

  .no-selection p {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
  }
</style>