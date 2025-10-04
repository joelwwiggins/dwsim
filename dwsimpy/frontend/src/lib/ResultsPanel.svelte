<script lang="ts">
	interface Props {
		results: any;
		isVisible: boolean;
	}

	let { results, isVisible }: Props = $props();

	// Format results for display
	let formattedResults = $derived(() => {
		if (!results) return null;

		const formatted = {
			status: results.status || 'Unknown',
			messages: results.messages || [],
			streamResults: [] as any[],
			unitResults: [] as any[]
		};

		// Process stream results
		if (results.streams) {
			formatted.streamResults = Object.entries(results.streams).map(([id, data]: [string, any]) => ({
				id,
				name: data.name || id,
				temperature: data.temperature?.toFixed(2),
				pressure: data.pressure?.toFixed(0),
				massFlowRate: data.mass_flow_rate?.toFixed(3),
				composition: data.composition ? Object.entries(data.composition).map(([comp, frac]: [string, any]) =>
					`${comp}: ${(frac * 100).toFixed(1)}%`
				).join(', ') : 'N/A'
			}));
		}

		// Process unit operation results
		if (results.units) {
			formatted.unitResults = Object.entries(results.units).map(([id, data]: [string, any]) => ({
				id,
				type: data.type || 'Unknown',
				status: data.status || 'Completed',
				properties: data.properties || {}
			}));
		}

		return formatted;
	});
</script>

{#if isVisible}
	<div class="results-panel">
		{#if formattedResults()}
			<div class="panel-header">
				<h3>Simulation Results</h3>
				<span class="status-badge" class:success={formattedResults()!.status === 'success'} class:error={formattedResults()!.status === 'error'}>
					{formattedResults()!.status}
				</span>
			</div>

			{#if formattedResults()!.messages && formattedResults()!.messages.length > 0}
				<div class="messages-section">
					<h4>Messages</h4>
					<ul class="message-list">
						{#each formattedResults()!.messages as message}
							<li class="message-item">{message}</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if formattedResults()!.streamResults && formattedResults()!.streamResults.length > 0}
				<div class="results-section">
					<h4>Stream Results</h4>
					<div class="table-container">
						<table class="results-table">
							<thead>
								<tr>
									<th>Stream</th>
									<th>Temperature (°C)</th>
									<th>Pressure (Pa)</th>
									<th>Mass Flow (kg/s)</th>
									<th>Composition</th>
								</tr>
							</thead>
							<tbody>
								{#each formattedResults()!.streamResults as stream}
									<tr>
										<td class="stream-name">{stream.name}</td>
										<td>{stream.temperature}</td>
										<td>{stream.pressure}</td>
										<td>{stream.massFlowRate}</td>
										<td class="composition-cell">{stream.composition}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{/if}

			{#if formattedResults()!.unitResults && formattedResults()!.unitResults.length > 0}
				<div class="results-section">
					<h4>Unit Operation Results</h4>
					<div class="unit-results">
						{#each formattedResults()!.unitResults as unit}
							<div class="unit-result-card">
								<div class="unit-header">
									<span class="unit-id">{unit.id}</span>
									<span class="unit-type">{unit.type}</span>
									<span class="unit-status" class:completed={unit.status === 'Completed'} class:failed={unit.status === 'Failed'}>
										{unit.status}
									</span>
								</div>
								{#if Object.keys(unit.properties).length > 0}
									<div class="unit-properties">
										{#each Object.entries(unit.properties) as [key, value]}
											<div class="property-row">
												<span class="property-key">{key}:</span>
												<span class="property-value">{String(value)}</span>
											</div>
										{/each}
									</div>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			{/if}

			{#if (!formattedResults()!.streamResults || formattedResults()!.streamResults.length === 0) && (!formattedResults()!.unitResults || formattedResults()!.unitResults.length === 0)}
				<div class="no-results">
					<p>No results available. Run a simulation to see results here.</p>
				</div>
			{/if}
		{:else}
			<div class="no-results">
				<p>No simulation results available.</p>
			</div>
		{/if}
	</div>
{/if}

<style>
	.results-panel {
		position: fixed;
		top: 60px;
		right: 0;
		bottom: 0;
		width: 400px;
		background: white;
		border-left: 1px solid #e5e7eb;
		display: flex;
		flex-direction: column;
		z-index: 100;
		box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
	}

	.panel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		border-bottom: 1px solid #e5e7eb;
		background: #f9fafb;
	}

	.panel-header h3 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #374151;
	}

	.status-badge {
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
	}

	.status-badge.success {
		background: #dcfce7;
		color: #166534;
	}

	.status-badge.error {
		background: #fee2e2;
		color: #991b1b;
	}

	.messages-section {
		padding: 1rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.messages-section h4 {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
		font-weight: 600;
		color: #374151;
	}

	.message-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.message-item {
		padding: 0.5rem;
		background: #fef3c7;
		border-left: 4px solid #f59e0b;
		margin-bottom: 0.5rem;
		font-size: 0.875rem;
		color: #92400e;
	}

	.results-section {
		padding: 1rem;
		flex: 1;
		overflow-y: auto;
	}

	.results-section h4 {
		margin: 0 0 1rem 0;
		font-size: 1rem;
		font-weight: 600;
		color: #374151;
	}

	.table-container {
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		overflow: hidden;
	}

	.results-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.875rem;
	}

	.results-table th {
		background: #f9fafb;
		padding: 0.75rem;
		text-align: left;
		font-weight: 600;
		color: #374151;
		border-bottom: 1px solid #e5e7eb;
	}

	.results-table td {
		padding: 0.75rem;
		border-bottom: 1px solid #f1f5f9;
	}

	.stream-name {
		font-weight: 500;
		color: #2563eb;
	}

	.composition-cell {
		font-family: monospace;
		font-size: 0.75rem;
		line-height: 1.4;
	}

	.unit-results {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.unit-result-card {
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		padding: 1rem;
		background: #f9fafb;
	}

	.unit-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
	}

	.unit-id {
		font-weight: 600;
		color: #2563eb;
	}

	.unit-type {
		font-size: 0.875rem;
		color: #6b7280;
	}

	.unit-status {
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
	}

	.unit-status.completed {
		background: #dcfce7;
		color: #166534;
	}

	.unit-status.failed {
		background: #fee2e2;
		color: #991b1b;
	}

	.unit-properties {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.property-row {
		display: flex;
		justify-content: space-between;
		font-size: 0.875rem;
	}

	.property-key {
		color: #6b7280;
	}

	.property-value {
		font-weight: 500;
		color: #374151;
	}

	.no-results {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: #6b7280;
		text-align: center;
	}

	.no-results p {
		margin: 0;
		font-size: 0.875rem;
	}
</style>