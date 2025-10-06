<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface HeaterData {
		id: string;
		name?: string;
		pressure_drop?: number;
		efficiency?: number;
		heat_duty?: number;
		outlet_temperature?: number;
		calculation_mode?: 'heat_duty' | 'outlet_temperature';
		pressure_drop_unit?: string;
		heat_duty_unit?: string;
		temperature_unit?: string;
	}

	interface Props {
		unit: HeaterData | null;
		isOpen: boolean;
		onClose: () => void;
		onSave: (unitData: HeaterData) => void;
	}

	let { unit, isOpen, onClose, onSave }: Props = $props();

	let editedUnit: HeaterData = $state(null);

	// Units for different properties
	const pressureUnits = ['Pa', 'kPa', 'MPa', 'bar', 'psi'];
	const heatUnits = ['W', 'kW', 'MW', 'BTU/hr', 'kcal/hr'];
	const temperatureUnits = ['K', '°C', '°F'];

	let selectedPressureUnit = $state('Pa');
	let selectedHeatUnit = $state('kW');
	let selectedTempUnit = $state('°C');

	// Reactive statement to update editedUnit when unit prop changes
	$effect(() => {
		if (unit) {
			editedUnit = { ...unit };
		} else {
			editedUnit = {
				id: '',
				name: '',
				pressure_drop: 0,
				efficiency: 100,
				heat_duty: 100,
				outlet_temperature: 100,
				calculation_mode: 'heat_duty',
				pressure_drop_unit: 'Pa',
				heat_duty_unit: 'kW',
				temperature_unit: '°C'
			};
		}
	});

	function handleSave() {
		if (editedUnit) {
			onSave(editedUnit);
			onClose();
		}
	}

	function updateCalculationMode(mode: 'heat_duty' | 'outlet_temperature') {
		if (editedUnit) {
			editedUnit.calculation_mode = mode;
		}
	}
</script>

{#if isOpen && editedUnit}
	<div class="modal-overlay" onclick={onClose}>
		<div class="modal-content" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Heater Properties</h2>
				<button class="close-button" onclick={onClose}>×</button>
			</div>

			<div class="modal-body">
				<!-- Basic Properties -->
				<div class="property-section">
					<h3>Unit Information</h3>
					<div class="form-row">
						<label for="unit-name">Name:</label>
						<input
							id="unit-name"
							type="text"
							bind:value={editedUnit.name}
							placeholder="Enter unit name"
						/>
					</div>
					<div class="form-row">
						<label for="unit-id">ID:</label>
						<input
							id="unit-id"
							type="text"
							bind:value={editedUnit.id}
							readonly
						/>
					</div>
				</div>

				<!-- Calculation Mode -->
				<div class="property-section">
					<h3>Calculation Mode</h3>
					<div class="radio-group">
						<label class="radio-option">
							<input
								type="radio"
								value="heat_duty"
								bind:group={editedUnit.calculation_mode}
								onchange={() => updateCalculationMode('heat_duty')}
							/>
							<span>Specify Heat Duty</span>
						</label>
						<label class="radio-option">
							<input
								type="radio"
								value="outlet_temperature"
								bind:group={editedUnit.calculation_mode}
								onchange={() => updateCalculationMode('outlet_temperature')}
							/>
							<span>Specify Outlet Temperature</span>
						</label>
					</div>
				</div>

				<!-- Operating Parameters -->
				<div class="property-section">
					<h3>Operating Parameters</h3>

					{#if editedUnit.calculation_mode === 'heat_duty'}
						<div class="form-row">
							<label for="heat-duty">Heat Duty:</label>
							<div class="input-group">
								<input
									id="heat-duty"
									type="number"
									step="0.1"
									bind:value={editedUnit.heat_duty}
								/>
								<select bind:value={selectedHeatUnit}>
									{#each heatUnits as unit}
										<option value={unit}>{unit}</option>
									{/each}
								</select>
							</div>
						</div>
					{:else}
						<div class="form-row">
							<label for="outlet-temp">Outlet Temperature:</label>
							<div class="input-group">
								<input
									id="outlet-temp"
									type="number"
									step="0.1"
									bind:value={editedUnit.outlet_temperature}
								/>
								<select bind:value={selectedTempUnit}>
									{#each temperatureUnits as unit}
										<option value={unit}>{unit}</option>
									{/each}
								</select>
							</div>
						</div>
					{/if}

					<div class="form-row">
						<label for="pressure-drop">Pressure Drop:</label>
						<div class="input-group">
							<input
								id="pressure-drop"
								type="number"
								step="0.1"
								bind:value={editedUnit.pressure_drop}
							/>
							<select bind:value={selectedPressureUnit}>
								{#each pressureUnits as unit}
									<option value={unit}>{unit}</option>
								{/each}
							</select>
						</div>
					</div>

					<div class="form-row">
						<label for="efficiency">Efficiency (%):</label>
						<div class="input-group">
							<input
								id="efficiency"
								type="number"
								min="0"
								max="100"
								step="0.1"
								bind:value={editedUnit.efficiency}
							/>
							<span class="unit-label">%</span>
						</div>
					</div>
				</div>

				<!-- Design Parameters -->
				<div class="property-section">
					<h3>Design Parameters</h3>
					<div class="info-grid">
						<div class="info-item">
							<label>Heat Transfer Area:</label>
							<span>-- m²</span>
						</div>
						<div class="info-item">
							<label>Overall HTC:</label>
							<span>-- W/m²·K</span>
						</div>
						<div class="info-item">
							<label>LMTD:</label>
							<span>-- °C</span>
						</div>
						<div class="info-item">
							<label>Fouling Factor:</label>
							<span>-- m²·K/W</span>
						</div>
					</div>
				</div>

				<!-- Connections -->
				<div class="property-section">
					<h3>Connections</h3>
					<div class="connections-grid">
						<div class="connection-item">
							<label>Inlet Stream:</label>
							<span class="connection-status connected">Connected</span>
						</div>
						<div class="connection-item">
							<label>Outlet Stream:</label>
							<span class="connection-status connected">Connected</span>
						</div>
						<div class="connection-item">
							<label>Energy Stream:</label>
							<span class="connection-status not-connected">Not Connected</span>
						</div>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<button class="cancel-btn" onclick={onClose}>Cancel</button>
				<button class="save-btn" onclick={handleSave}>Save</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
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
		max-height: 90vh;
		display: flex;
		flex-direction: column;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px;
		border-bottom: 1px solid #e5e7eb;
		background: #f9fafb;
		border-radius: 8px 8px 0 0;
	}

	.modal-header h2 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827;
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
		border-radius: 4px;
	}

	.close-button:hover {
		background: #e5e7eb;
		color: #374151;
	}

	.modal-body {
		padding: 20px;
		overflow-y: auto;
		flex: 1;
	}

	.property-section {
		margin-bottom: 24px;
	}

	.property-section h3 {
		margin: 0 0 16px 0;
		font-size: 1rem;
		font-weight: 600;
		color: #374151;
		border-bottom: 1px solid #e5e7eb;
		padding-bottom: 8px;
	}

	.form-row {
		display: flex;
		align-items: center;
		margin-bottom: 12px;
	}

	.form-row label {
		min-width: 140px;
		font-weight: 500;
		color: #374151;
		margin-right: 12px;
	}

	.input-group {
		display: flex;
		align-items: center;
	}

	.input-group input {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 4px 0 0 4px;
		font-size: 14px;
		flex: 1;
		min-width: 120px;
	}

	.input-group select {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-left: none;
		border-radius: 0 4px 4px 0;
		background: #f9fafb;
		font-size: 14px;
		min-width: 80px;
	}

	.unit-label {
		padding: 8px 12px;
		background: #f9fafb;
		border: 1px solid #d1d5db;
		border-left: none;
		border-radius: 0 4px 4px 0;
		font-size: 14px;
		color: #6b7280;
		min-width: 40px;
		text-align: center;
	}

	.radio-group {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.radio-option {
		display: flex;
		align-items: center;
		cursor: pointer;
		font-weight: 500;
		color: #374151;
	}

	.radio-option input {
		margin-right: 8px;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 16px;
	}

	.info-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 12px;
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 4px;
	}

	.info-item label {
		font-weight: 500;
		color: #374151;
	}

	.info-item span {
		color: #6b7280;
		font-family: monospace;
	}

	.connections-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 12px;
	}

	.connection-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 12px;
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 4px;
	}

	.connection-item label {
		font-weight: 500;
		color: #374151;
	}

	.connection-status {
		font-size: 12px;
		font-weight: 600;
		padding: 4px 8px;
		border-radius: 12px;
		text-transform: uppercase;
	}

	.connection-status.connected {
		background: #d1fae5;
		color: #065f46;
	}

	.connection-status.not-connected {
		background: #fee2e2;
		color: #991b1b;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		padding: 20px;
		border-top: 1px solid #e5e7eb;
		background: #f9fafb;
		border-radius: 0 0 8px 8px;
	}

	.cancel-btn, .save-btn {
		padding: 10px 20px;
		border: none;
		border-radius: 4px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.cancel-btn {
		background: #f3f4f6;
		color: #374151;
		border: 1px solid #d1d5db;
	}

	.cancel-btn:hover {
		background: #e5e7eb;
	}

	.save-btn {
		background: #2563eb;
		color: white;
	}

	.save-btn:hover {
		background: #1d4ed8;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.modal-content {
			width: 95%;
			max-height: 95vh;
		}

		.form-row {
			flex-direction: column;
			align-items: flex-start;
			gap: 8px;
		}

		.form-row label {
			min-width: auto;
			margin-right: 0;
		}

		.info-grid,
		.connections-grid {
			grid-template-columns: 1fr;
		}
	}
</style>