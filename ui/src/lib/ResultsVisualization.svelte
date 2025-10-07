<script>
  import { onMount } from 'svelte'
  
  let { 
    results = null, 
    unitType = '', 
    unitId = '' 
  } = $props()

  let chartCanvas = null
  let chart = null

  onMount(() => {
    if (chartCanvas && results) {
      initializeChart()
    }
  })

  $effect(() => {
    if (chartCanvas && results) {
      initializeChart()
    }
  })

  function initializeChart() {
    if (!chartCanvas || !results) return

    // Clean up existing chart
    if (chart) {
      chart.destroy()
    }

    const ctx = chartCanvas.getContext('2d')
    
    // Create chart based on unit type and results
    const chartConfig = getChartConfig(unitType, results)
    
    // Using a simple canvas-based chart (in a real app, you'd use Chart.js or similar)
    drawSimpleChart(ctx, chartConfig)
  }

  function getChartConfig(unitType, results) {
    switch (unitType) {
      case 'distillation_column':
        return {
          type: 'profile',
          title: 'Column Temperature Profile',
          data: results.stage_temperatures || [],
          labels: results.stage_numbers || []
        }
      case 'heat_exchanger':
        return {
          type: 'line',
          title: 'Temperature vs Position',
          data: [
            { name: 'Hot Stream', values: results.hot_stream_temps || [] },
            { name: 'Cold Stream', values: results.cold_stream_temps || [] }
          ],
          labels: results.positions || []
        }
      case 'absorption_column':
      case 'stripping_column':
        return {
          type: 'profile',
          title: 'Component Concentration Profile',
          data: results.concentration_profile || [],
          labels: results.stage_numbers || []
        }
      default:
        return {
          type: 'bar',
          title: 'Results Overview',
          data: Object.values(results).filter(val => typeof val === 'number'),
          labels: Object.keys(results).filter(key => typeof results[key] === 'number')
        }
    }
  }

  function drawSimpleChart(ctx, config) {
    const { width, height } = chartCanvas
    ctx.clearRect(0, 0, width, height)
    
    // Simple chart drawing - in a real implementation, use a proper charting library
    ctx.fillStyle = '#f3f4f6'
    ctx.fillRect(0, 0, width, height)
    
    ctx.fillStyle = '#374151'
    ctx.font = '16px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(config.title, width / 2, 30)
    
    // Draw axes
    ctx.strokeStyle = '#6b7280'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(50, 50)
    ctx.lineTo(50, height - 50)
    ctx.lineTo(width - 50, height - 50)
    ctx.stroke()
    
    // Draw data points (simplified)
    if (config.data && config.data.length > 0) {
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 2
      ctx.beginPath()
      
      const data = Array.isArray(config.data) ? config.data : [config.data]
      const maxVal = Math.max(...data.flat().filter(val => typeof val === 'number'))
      const minVal = Math.min(...data.flat().filter(val => typeof val === 'number'))
      const range = maxVal - minVal || 1
      
      data.forEach((series, seriesIndex) => {
        if (Array.isArray(series)) {
          series.forEach((value, index) => {
            if (typeof value === 'number') {
              const x = 50 + (index / (series.length - 1 || 1)) * (width - 100)
              const y = height - 50 - ((value - minVal) / range) * (height - 100)
              
              if (index === 0) {
                ctx.moveTo(x, y)
              } else {
                ctx.lineTo(x, y)
              }
            }
          })
        }
      })
      
      ctx.stroke()
    }
  }

  function exportResults() {
    if (!results) return
    
    const dataStr = JSON.stringify(results, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `${unitType}_${unitId}_results.json`
    link.click()
    
    URL.revokeObjectURL(url)
  }
</script>

<div class="results-visualization">
  <div class="results-header">
    <h3>Simulation Results</h3>
    {#if results}
      <button class="export-btn" onclick={exportResults}>
        Export Results
      </button>
    {/if}
  </div>
  
  {#if results}
    <div class="results-content">
      <div class="chart-section">
        <canvas 
          bind:this={chartCanvas} 
          width="600" 
          height="300"
        ></canvas>
      </div>
      
      <div class="table-section">
        <h4>Results Summary</h4>
        <div class="results-table">
          {#each Object.entries(results) as [key, value]}
            {#if typeof value === 'number' || typeof value === 'string'}
              <div class="table-row">
                <div class="table-cell key-cell">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</div>
                <div class="table-cell value-cell">
                  {#if typeof value === 'number'}
                    {value.toFixed(4)}
                  {:else}
                    {value}
                  {/if}
                </div>
              </div>
            {/if}
          {/each}
        </div>
      </div>
      
      {#if unitType === 'distillation_column' && results.stage_temperatures}
        <div class="detailed-section">
          <h4>Stage-by-Stage Results</h4>
          <div class="stage-table">
            <div class="table-header">
              <div>Stage</div>
              <div>Temperature (K)</div>
              <div>Liquid Flow (kmol/h)</div>
              <div>Vapor Flow (kmol/h)</div>
            </div>
            {#each results.stage_numbers || [] as stage, index}
              <div class="table-row">
                <div>{stage}</div>
                <div>{(results.stage_temperatures[index] || 0).toFixed(2)}</div>
                <div>{(results.liquid_flows?.[index] || 0).toFixed(2)}</div>
                <div>{(results.vapor_flows?.[index] || 0).toFixed(2)}</div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {:else}
    <div class="no-results">
      <p>No simulation results available. Run the simulation first.</p>
    </div>
  {/if}
</div>

<style>
  .results-visualization {
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e5e7eb;
  }

  .results-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }

  .export-btn {
    padding: 8px 16px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  }

  .results-content {
    padding: 20px;
  }

  .chart-section {
    margin-bottom: 30px;
    display: flex;
    justify-content: center;
  }

  canvas {
    border: 1px solid #e5e7eb;
    border-radius: 4px;
  }

  .table-section h4,
  .detailed-section h4 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }

  .results-table,
  .stage-table {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    overflow: hidden;
  }

  .table-header {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    background: #f9fafb;
    font-weight: 600;
    color: #374151;
  }

  .table-header > div,
  .table-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
  }

  .table-row {
    border-bottom: 1px solid #e5e7eb;
  }

  .table-row:last-child {
    border-bottom: none;
  }

  .table-cell {
    padding: 12px;
    text-align: left;
  }

  .key-cell {
    font-weight: 500;
    color: #6b7280;
  }

  .value-cell {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  }

  .detailed-section {
    margin-top: 30px;
  }

  .no-results {
    padding: 40px;
    text-align: center;
    color: #6b7280;
  }

  .no-results p {
    margin: 0;
    font-size: 16px;
  }
</style>
