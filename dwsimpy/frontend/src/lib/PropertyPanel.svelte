<script lang="ts">
	import type { Node } from '@xyflow/svelte';

	interface UnitData extends Record<string, unknown> {
		label: string;
		unitType: string;
		icon: string;
		properties: Record<string, any>;
	}

	interface Props {
		selectedNode: Node<UnitData> | null;
	}

	let { selectedNode }: Props = $props();

	// Property definitions for different unit types
	const propertyDefinitions: Record<string, Array<{key: string, label: string, type: string, default: any}>> = {
		mixer: [
			{ key: 'pressure_drop', label: 'Pressure Drop (Pa)', type: 'number', default: 0 },
		],
		heater: [
			{ key: 'heat_duty', label: 'Heat Duty (kW)', type: 'number', default: 100 },
			{ key: 'outlet_temperature', label: 'Outlet Temperature (°C)', type: 'number', default: 100 },
		],
		cooler: [
			{ key: 'heat_duty', label: 'Heat Duty (kW)', type: 'number', default: -100 },
			{ key: 'outlet_temperature', label: 'Outlet Temperature (°C)', type: 'number', default: 25 },
		],
		valve: [
			{ key: 'pressure_drop', label: 'Pressure Drop (Pa)', type: 'number', default: 100000 },
		],
		pump: [
			{ key: 'pressure_increase', label: 'Pressure Increase (Pa)', type: 'number', default: 200000 },
			{ key: 'efficiency', label: 'Efficiency (%)', type: 'number', default: 75 },
		],
		splitter: [
			{ key: 'split_ratio', label: 'Split Ratio', type: 'number', default: 0.5 },
		],
		compressor: [
			{ key: 'pressure_ratio', label: 'Pressure Ratio', type: 'number', default: 3.0 },
			{ key: 'efficiency', label: 'Efficiency (%)', type: 'number', default: 75 },
		],
		heat_exchanger: [
			{ key: 'heat_transfer_area', label: 'Heat Transfer Area (m²)', type: 'number', default: 10 },
			{ key: 'overall_heat_transfer_coeff', label: 'U (W/m²·K)', type: 'number', default: 500 },
		],
		pipe: [
			{ key: 'length', label: 'Length (m)', type: 'number', default: 100 },
			{ key: 'diameter', label: 'Diameter (m)', type: 'number', default: 0.1 },
		],
		vessel: [
			{ key: 'volume', label: 'Volume (m³)', type: 'number', default: 1.0 },
			{ key: 'pressure', label: 'Design Pressure (Pa)', type: 'number', default: 101325 },
		],
	};

	function updateProperty(key: string, value: any) {
		if (!selectedNode) return;

		selectedNode.data = {
			...selectedNode.data,
			properties: {
				...selectedNode.data.properties,
				[key]: value
			}
		};
	}

	// Use $derived for reactive properties
	let properties = $derived(selectedNode?.data?.unitType ?
		propertyDefinitions[selectedNode.data.unitType] || [] : []);
</script>

<div class="property-panel">
	{#if selectedNode}
		<div class="panel-header">
			<h3 class="panel-title">
				<span class="unit-icon">{selectedNode.data.icon}</span>
				{selectedNode.data.label}
			</h3>
			<p class="unit-id">{selectedNode.id}</p>
		</div>

		<div class="properties-list">
			{#each properties as prop (prop.key)}
				<div class="property-item">
					<label class="property-label" for={prop.key}>
						{prop.label}
					</label>
					{#if prop.type === 'number'}
						<input
							type="number"
							id={prop.key}
							class="property-input"
							value={selectedNode.data.properties?.[prop.key] ?? prop.default}
							oninput={(e) => updateProperty(prop.key, parseFloat((e.target as HTMLInputElement).value) || 0)}
						/>
					{:else if prop.type === 'text'}
						<input
							type="text"
							id={prop.key}
							class="property-input"
							value={selectedNode.data.properties?.[prop.key] ?? prop.default}
							oninput={(e) => updateProperty(prop.key, (e.target as HTMLInputElement).value)}
						/>
					{:else if prop.type === 'boolean'}
						<input
							type="checkbox"
							id={prop.key}
							class="property-checkbox"
							checked={selectedNode.data.properties?.[prop.key] ?? prop.default}
							onchange={(e) => updateProperty(prop.key, (e.target as HTMLInputElement).checked)}
						/>
					{/if}
				</div>
			{/each}
		</div>
	{:else}
		<div class="no-selection">
			<p>Select a unit operation to view its properties</p>
		</div>
	{/if}
</div>

<style>
	.property-panel {
		width: 300px;
		background: white;
		border-left: 1px solid #e5e7eb;
		padding: 1rem;
		display: flex;
		flex-direction: column;
	}

	.panel-header {
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.panel-title {
		font-size: 1.125rem;
		font-weight: 600;
		color: #374151;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.25rem;
	}

	.unit-icon {
		font-size: 1.25rem;
	}

	.unit-id {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0;
	}

	.properties-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		flex: 1;
		overflow-y: auto;
	}

	.property-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.property-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
	}

	.property-input {
		padding: 0.5rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		font-size: 0.875rem;
	}

	.property-input:focus {
		outline: none;
		border-color: #2563eb;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.property-checkbox {
		width: 1rem;
		height: 1rem;
		border: 1px solid #d1d5db;
		border-radius: 0.25rem;
	}

	.no-selection {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: #6b7280;
		text-align: center;
	}

	.no-selection p {
		margin: 0;
		font-size: 0.875rem;
	}
</style>