<script>
  import { createEventDispatcher } from 'svelte'
  
  let { 
    isOpen = false, 
    unitType = '', 
    currentConfig = {}, 
    onSave = null, 
    onCancel = null 
  } = $props()

  const dispatch = createEventDispatcher()

  let wizardConfig = $state({})
  let currentStep = $state(0)

  $effect(() => {
    if (unitType && isOpen) {
      wizardConfig = { ...currentConfig }
      currentStep = 0
    }
  })

  // Wizard steps for different unit types
  const wizardSteps = {
    distillation_column: [
      { title: 'Column Setup', fields: ['numberOfStages', 'feedStage', 'condenserType', 'reboilerType'] },
      { title: 'Operating Conditions', fields: ['feedPressure', 'columnPressureDrop', 'condenserPressure'] },
      { title: 'Specifications', fields: ['refluxRatio', 'distillateRate', 'bottomsRate', 'reboilerDuty', 'condenserDuty'] }
    ],
    absorption_column: [
      { title: 'Column Setup', fields: ['numberOfStages', 'feedStage'] },
      { title: 'Operating Conditions', fields: ['feedPressure', 'columnPressureDrop'] },
      { title: 'Process Specifications', fields: ['solventFlowRate', 'absorptionEfficiency', 'targetComponent'] }
    ],
    stripping_column: [
      { title: 'Column Setup', fields: ['numberOfStages', 'feedStage'] },
      { title: 'Operating Conditions', fields: ['feedPressure', 'columnPressureDrop'] },
      { title: 'Process Specifications', fields: ['strippingGasFlowRate', 'strippingEfficiency', 'targetComponent'] }
    ],
    heat_exchanger: [
      { title: 'Configuration', fields: ['calculationMode', 'heatTransferArea', 'overallHeatTransferCoeff'] },
      { title: 'Stream Temperatures', fields: ['hotStreamInletTemp', 'coldStreamInletTemp', 'hotStreamOutletTemp', 'coldStreamOutletTemp'] },
      { title: 'Operating Conditions', fields: ['heatDuty', 'minimumTemperatureApproach', 'flowDirection', 'equipmentType'] }
    ],
    condenser: [
      { title: 'Type & Pressure', fields: ['condenserType', 'condenserPressure'] },
      { title: 'Temperature Control', fields: ['condenserTemperature', 'vaporFraction'] },
      { title: 'Heat Transfer', fields: ['heatDuty', 'overallHeatTransferCoeff', 'heatTransferArea'] }
    ],
    reboiler: [
      { title: 'Type & Pressure', fields: ['reboilerType', 'reboilerPressure'] },
      { title: 'Temperature Control', fields: ['reboilerTemperature', 'vaporFraction'] },
      { title: 'Heat Transfer', fields: ['heatDuty', 'overallHeatTransferCoeff', 'heatTransferArea'] }
    ]
  }

  function getFieldLabel(field) {
    const labels = {
      numberOfStages: 'Number of Stages',
      feedStage: 'Feed Stage',
      condenserType: 'Condenser Type',
      reboilerType: 'Reboiler Type',
      feedPressure: 'Feed Pressure (Pa)',
      columnPressureDrop: 'Column Pressure Drop (Pa)',
      condenserPressure: 'Condenser Pressure (Pa)',
      refluxRatio: 'Reflux Ratio',
      distillateRate: 'Distillate Rate (kmol/h)',
      bottomsRate: 'Bottoms Rate (kmol/h)',
      reboilerDuty: 'Reboiler Duty (kW)',
      condenserDuty: 'Condenser Duty (kW)',
      solventFlowRate: 'Solvent Flow Rate (kmol/h)',
      absorptionEfficiency: 'Absorption Efficiency',
      strippingGasFlowRate: 'Stripping Gas Flow Rate (kmol/h)',
      strippingEfficiency: 'Stripping Efficiency',
      targetComponent: 'Target Component',
      calculationMode: 'Calculation Mode',
      heatTransferArea: 'Heat Transfer Area (m²)',
      overallHeatTransferCoeff: 'Overall Heat Transfer Coefficient (W/m²·K)',
      hotStreamInletTemp: 'Hot Stream Inlet Temperature (K)',
      coldStreamInletTemp: 'Cold Stream Inlet Temperature (K)',
      hotStreamOutletTemp: 'Hot Stream Outlet Temperature (K)',
      coldStreamOutletTemp: 'Cold Stream Outlet Temperature (K)',
      heatDuty: 'Heat Duty (W)',
      minimumTemperatureApproach: 'Minimum Temperature Approach (K)',
      flowDirection: 'Flow Direction',
      equipmentType: 'Equipment Type',
      condenserTemperature: 'Condenser Temperature (K)',
      reboilerTemperature: 'Reboiler Temperature (K)',
      vaporFraction: 'Vapor Fraction'
    }
    return labels[field] || field.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())
  }

  function getFieldType(field) {
    const types = {
      condenserType: 'select',
      reboilerType: 'select',
      calculationMode: 'select',
      flowDirection: 'select',
      equipmentType: 'select'
    }
    return types[field] || 'number'
  }

  function getFieldOptions(field) {
    const options = {
      condenserType: ['total', 'partial'],
      reboilerType: ['kettle', 'thermosiphon'],
      calculationMode: ['heat_duty', 'outlet_temperatures', 'area'],
      flowDirection: ['counter_current', 'co_current'],
      equipmentType: ['shell_and_tube', 'double_pipe', 'plate']
    }
    return options[field] || []
  }

  function nextStep() {
    if (currentStep < getSteps().length - 1) {
      currentStep++
    }
  }

  function prevStep() {
    if (currentStep > 0) {
      currentStep--
    }
  }

  function getSteps() {
    return wizardSteps[unitType] || []
  }

  function handleSave() {
    dispatch('save', wizardConfig)
    if (onSave) onSave(wizardConfig)
  }

  function handleCancel() {
    dispatch('cancel')
    if (onCancel) onCancel()
  }
</script>

{#if isOpen && unitType}
  {@const steps = getSteps()}
  {@const currentStepData = steps[currentStep]}

  <div class="wizard-overlay" onclick={handleCancel}>
    <div class="wizard-content" onclick={(e) => e.stopPropagation()}>
      <div class="wizard-header">
        <h2>Configure {unitType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h2>
        <button class="close-button" onclick={handleCancel}>×</button>
      </div>
      
      <div class="wizard-progress">
        {#each steps as step, index}
          <div class="step-indicator" class:active={index === currentStep} class:completed={index < currentStep}>
            <div class="step-number">{index + 1}</div>
            <div class="step-title">{step.title}</div>
          </div>
        {/each}
      </div>
      
      <div class="wizard-body">
        {#if currentStepData}
          <h3>{currentStepData.title}</h3>
          <div class="fields-grid">
            {#each currentStepData.fields as field}
              <div class="field-row">
                <label for={field}>{getFieldLabel(field)}:</label>
                {#if getFieldType(field) === 'select'}
                  <select id={field} bind:value={wizardConfig[field]}>
                    {#each getFieldOptions(field) as option}
                      <option value={option}>{option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>
                    {/each}
                  </select>
                {:else}
                  <input 
                    id={field}
                    type={getFieldType(field)}
                    step="any"
                    bind:value={wizardConfig[field]}
                    placeholder="Enter value"
                  />
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
      
      <div class="wizard-footer">
        <button class="prev-btn" onclick={prevStep} disabled={currentStep === 0}>
          Previous
        </button>
        
        <div class="step-counter">
          Step {currentStep + 1} of {steps.length}
        </div>
        
        {#if currentStep < steps.length - 1}
          <button class="next-btn" onclick={nextStep}>
            Next
          </button>
        {:else}
          <button class="save-btn" onclick={handleSave}>
            Save Configuration
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .wizard-overlay {
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

  .wizard-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .wizard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e5e7eb;
  }

  .wizard-header h2 {
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

  .wizard-progress {
    display: flex;
    padding: 20px;
    gap: 12px;
    border-bottom: 1px solid #e5e7eb;
  }

  .step-indicator {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    opacity: 0.5;
  }

  .step-indicator.active {
    opacity: 1;
  }

  .step-indicator.completed {
    opacity: 0.8;
  }

  .step-number {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
  }

  .step-indicator.active .step-number {
    background: #3b82f6;
    color: white;
  }

  .step-indicator.completed .step-number {
    background: #10b981;
    color: white;
  }

  .step-title {
    font-size: 11px;
    text-align: center;
    color: #6b7280;
  }

  .wizard-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
  }

  .wizard-body h3 {
    margin: 0 0 20px 0;
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }

  .fields-grid {
    display: grid;
    gap: 16px;
  }

  .field-row {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .field-row label {
    font-weight: 500;
    color: #374151;
    font-size: 14px;
  }

  .field-row input,
  .field-row select {
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 14px;
  }

  .wizard-footer {
    padding: 20px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .prev-btn,
  .next-btn,
  .save-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .prev-btn {
    background: #6b7280;
    color: white;
  }

  .prev-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .next-btn {
    background: #3b82f6;
    color: white;
  }

  .save-btn {
    background: #10b981;
    color: white;
  }

  .step-counter {
    font-size: 14px;
    color: #6b7280;
  }
</style>
