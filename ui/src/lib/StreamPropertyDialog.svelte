<script>
  import { createEventDispatcher } from 'svelte'
  
  let { 
    isOpen = false, 
    streamData = null, 
    onSave = null, 
    onCancel = null 
  } = $props()

  const dispatch = createEventDispatcher()

  let localStreamData = $state({})
  let compositionString = $state('{}')
  let newComponentName = $state('')
  let newComponentFraction = $state(0.0)

  $effect(() => {
    if (streamData && isOpen) {
      localStreamData = { ...streamData }
      compositionString = JSON.stringify(streamData.composition || {}, null, 2)
    }
  })

  function updateComposition() {
    try {
      const parsed = JSON.parse(compositionString)
      localStreamData.composition = parsed
    } catch (e) {
      // Invalid JSON
    }
  }

  function addComponent() {
    if (!newComponentName.trim()) return
    
    if (!localStreamData.composition) {
      localStreamData.composition = {}
    }
    
    localStreamData.composition[newComponentName] = newComponentFraction
    compositionString = JSON.stringify(localStreamData.composition, null, 2)
    newComponentName = ''
    newComponentFraction = 0.0
  }

  function removeComponent(componentName) {
    if (localStreamData.composition) {
      delete localStreamData.composition[componentName]
      compositionString = JSON.stringify(localStreamData.composition, null, 2)
    }
  }

  function normalizeComposition() {
    if (!localStreamData.composition) return
    
    const total = Object.values(localStreamData.composition).reduce((sum, val) => sum + val, 0)
    if (total > 0) {
      for (const key in localStreamData.composition) {
        localStreamData.composition[key] /= total
      }
      compositionString = JSON.stringify(localStreamData.composition, null, 2)
    }
  }

  function handleSave() {
    updateComposition()
    dispatch('save', localStreamData)
    if (onSave) onSave(localStreamData)
  }

  function handleCancel() {
    dispatch('cancel')
    if (onCancel) onCancel()
  }
</script>

{#if isOpen}
  <div class="modal-overlay" onclick={handleCancel}>
    <div class="modal-content" onclick={(e) => e.stopPropagation()}>
      <div class="modal-header">
        <h2>Stream Properties</h2>
        <button class="close-button" onclick={handleCancel}>×</button>
      </div>
      
      <div class="modal-body">
        <div class="properties-grid">
          <div class="property-group">
            <h3>Basic Properties</h3>
            <div class="property-row">
              <label>Temperature (K):</label>
              <input 
                type="number" 
                step="0.01"
                bind:value={localStreamData.temperature} 
              />
            </div>
            <div class="property-row">
              <label>Pressure (Pa):</label>
              <input 
                type="number" 
                step="100"
                bind:value={localStreamData.pressure} 
              />
            </div>
            <div class="property-row">
              <label>Mass Flow Rate (kg/s):</label>
              <input 
                type="number" 
                step="0.0001"
                bind:value={localStreamData.mass_flow_rate} 
              />
            </div>
          </div>
          
          <div class="property-group">
            <h3>Composition</h3>
            <div class="composition-editor">
              <div class="json-editor">
                <label>JSON Format:</label>
                <textarea 
                  bind:value={compositionString}
                  oninput={updateComposition}
                  rows="6"
                  placeholder='{"water": 0.8, "ethanol": 0.2}'
                ></textarea>
              </div>
              
              <div class="component-tools">
                <h4>Add Component</h4>
                <div class="add-component-row">
                  <input 
                    type="text" 
                    placeholder="Component name"
                    bind:value={newComponentName}
                  />
                  <input 
                    type="number" 
                    step="0.001"
                    placeholder="Fraction"
                    bind:value={newComponentFraction}
                  />
                  <button onclick={addComponent}>Add</button>
                </div>
                
                <button class="normalize-btn" onclick={normalizeComposition}>
                  Normalize to 1.0
                </button>
              </div>
              
              {#if localStreamData.composition}
                <div class="component-list">
                  <h4>Components</h4>
                  {#each Object.entries(localStreamData.composition) as [name, fraction]}
                    <div class="component-item">
                      <span>{name}: {fraction.toFixed(4)}</span>
                      <button onclick={() => removeComponent(name)}>Remove</button>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="cancel-btn" onclick={handleCancel}>Cancel</button>
        <button class="save-btn" onclick={handleSave}>Save Changes</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    max-width: 700px;
    width: 90%;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e5e7eb;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6b7280;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
  }

  .modal-footer {
    padding: 20px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }

  .properties-grid {
    display: grid;
    gap: 24px;
  }

  .property-group h3 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }

  .property-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .property-row label {
    min-width: 140px;
    font-weight: 500;
    color: #374151;
  }

  .property-row input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 14px;
  }

  .composition-editor {
    display: grid;
    gap: 16px;
  }

  .json-editor textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
    resize: vertical;
  }

  .component-tools {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 16px;
    background: #f9fafb;
  }

  .add-component-row {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }

  .add-component-row input {
    padding: 6px 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 13px;
  }

  .add-component-row input:first-child {
    flex: 2;
  }

  .add-component-row input:nth-child(2) {
    flex: 1;
  }

  .add-component-row button {
    padding: 6px 12px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .normalize-btn {
    width: 100%;
    padding: 8px;
    background: #10b981;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .component-list {
    margin-top: 16px;
  }

  .component-list h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: 600;
  }

  .component-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 8px;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    margin-bottom: 4px;
  }

  .component-item button {
    padding: 2px 6px;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 3px;
    font-size: 11px;
    cursor: pointer;
  }

  .cancel-btn {
    padding: 8px 16px;
    background: #6b7280;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .save-btn {
    padding: 8px 16px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
</style>
