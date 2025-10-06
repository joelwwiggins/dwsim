<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface HeatExchangerData {
		label: string;
		unitType: string;
		calculation_mode: 'heat_duty' | 'outlet_temperatures' | 'area';
		heat_transfer_area: number;
		overall_heat_transfer_coeff: number;
		fouling_factor: number;
		minimum_temperature_approach: number;
		hot_stream_outlet_temp?: number;
		cold_stream_outlet_temp?: number;
		heat_duty: number;
		flow_direction: 'counter_current' | 'co_current';
		equipment_type: 'shell_and_tube' | 'double_pipe' | 'plate';
		hot_side_pressure_drop: number;
		cold_side_pressure_drop: number;
	}

	interface Props {
		unit: HeatExchangerData;
		isOpen: boolean;
		onClose: () => void;
		onSave: (data: HeatExchangerData) => void;
	}

	let { unit, isOpen, onClose, onSave }: Props = $props();

	let editedUnit: HeatExchangerData = $state(null);

	// Reactive statement to update editedUnit when unit prop changes
	$effect(() => {
		if (unit) {
			editedUnit = { ...unit };
		} else {
			editedUnit = {
				label: '',
				unitType: 'heat_exchanger',
				calculation_mode: 'heat_duty',
				heat_transfer_area: 10.0,
				overall_heat_transfer_coeff: 500.0,
				fouling_factor: 0.0001,
				minimum_temperature_approach: 10.0,
				heat_duty: 100000.0,
				flow_direction: 'counter_current',
				equipment_type: 'shell_and_tube',
				hot_side_pressure_drop: 10000,
				cold_side_pressure_drop: 10000
			};
		}
	});

	function handleSave() {
		if (editedUnit) {
			onSave(editedUnit);
			onClose();
		}
	}
</script>

{#if isOpen && editedUnit}
	<div class="modal-overlay" onclick={onClose}>
		<div class="modal-content" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Heat Exchanger Properties</h2>
				<button class="close-button" onclick={onClose}>×</button>
			</div>

			<div class="modal-body">
				<div class="form-section">
					<h3>General</h3>
					<div class="form-row">
						<label for="label">Label:</label>
						<input
							id="label"
							type="text"
							bind:value={editedUnit.label}
							placeholder="Heat exchanger name"
						/>
					</div>
					<div class="form-row">
						<label for="calculation-mode">Calculation Mode:</label>
						<select id="calculation-mode" bind:value={editedUnit.calculation_mode}>
							<option value="heat_duty">Heat Duty</option>
							<option value="outlet_temperatures">Outlet Temperatures</option>
							<option value="area">Heat Transfer Area</option>
						</select>
					</div>
					<div class="form-row">
						<label for="equipment-type">Equipment Type:</label>
						<select id="equipment-type" bind:value={editedUnit.equipment_type}>
							<option value="shell_and_tube">Shell and Tube</option>
							<option value="double_pipe">Double Pipe</option>
							<option value="plate">Plate and Frame</option>
						</select>
					</div>
					<div class="form-row">
						<label for="flow-direction">Flow Direction:</label>
						<select id="flow-direction" bind:value={editedUnit.flow_direction}>
							<option value="counter_current">Counter-Current</option>
							<option value="co_current">Co-Current</option>
						</select>
					</div>
				</div>

				<div class="form-section">
					<h3>Heat Transfer Parameters</h3>
					<div class="form-row">
						<label for="area">Heat Transfer Area (m²):</label>
						<input
							id="area"
							type="number"
							step="0.1"
							min="0.1"
							bind:value={editedUnit.heat_transfer_area}
						/>
					</div>
					<div class="form-row">
						<label for="htc">Overall Heat Transfer Coefficient (W/m²·K):</label>
						<input
							id="htc"
							type="number"
							step="10"
							min="1"
							bind:value={editedUnit.overall_heat_transfer_coeff}
						/>
					</div>
					<div class="form-row">
						<label for="fouling">Fouling Factor (m²·K/W):</label>
						<input
							id="fouling"
							type="number"
							step="0.00001"
							min="0"
							bind:value={editedUnit.fouling_factor}
						/>
					</div>
					<div class="form-row">
						<label for="min-approach">Minimum Temperature Approach (K):</label>
						<input
							id="min-approach"
							type="number"
							step="0.1"
							min="0.1"
							bind:value={editedUnit.minimum_temperature_approach}
						/>
					</div>
				</div>

				{#if editedUnit.calculation_mode === 'heat_duty'}
					<div class="form-section">
						<h3>Heat Duty Specification</h3>
						<div class="form-row">
							<label for="heat-duty">Heat Duty (kW):</label>
							<input
								id="heat-duty"
								type="number"
								step="10"
								bind:value={editedUnit.heat_duty}
							/>
						</div>
					</div>
				{/if}

				{#if editedUnit.calculation_mode === 'outlet_temperatures'}
					<div class="form-section">
						<h3>Outlet Temperature Specifications</h3>
						<div class="form-row">
							<label for="hot-outlet-temp">Hot Stream Outlet Temperature (K):</label>
							<input
								id="hot-outlet-temp"
								type="number"
								step="0.1"
								bind:value={editedUnit.hot_stream_outlet_temp}
								placeholder="Optional"
							/>
						</div>
						<div class="form-row">
							<label for="cold-outlet-temp">Cold Stream Outlet Temperature (K):</label>
							<input
								id="cold-outlet-temp"
								type="number"
								step="0.1"
								bind:value={editedUnit.cold_stream_outlet_temp}
								placeholder="Optional"
							/>
						</div>
					</div>
				{/if}

				<div class="form-section">
					<h3>Pressure Drops</h3>
					<div class="form-row">
						<label for="hot-dp">Hot Side Pressure Drop (Pa):</label>
						<input
							id="hot-dp"
							type="number"
							step="100"
							min="0"
							bind:value={editedUnit.hot_side_pressure_drop}
						/>
					</div>
					<div class="form-row">
						<label for="cold-dp">Cold Side Pressure Drop (Pa):</label>
						<input
							id="cold-dp"
							type="number"
							step="100"
							min="0"
							bind:value={editedUnit.cold_side_pressure_drop}
						/>
					</div>
				</div>

				<div class="info-section">
					<p><strong>Note:</strong> Connect the hot stream (higher temperature) to the top inlet and cold stream (lower temperature) to the bottom inlet.</p>
					<p><strong>Calculation modes:</strong></p>
					<ul>
						<li><strong>Heat Duty:</strong> Calculate outlet temperatures from specified heat transfer rate</li>
						<li><strong>Outlet Temperatures:</strong> Calculate required heat duty from specified outlet temperatures</li>
						<li><strong>Area:</strong> Calculate required heat transfer area for assumed temperature changes</li>
					</ul>
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

	.form-section {
		margin-bottom: 24px;
	}

	.form-section h3 {
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
		min-width: 200px;
		font-weight: 500;
		color: #374151;
		margin-right: 12px;
	}

	.form-row input, .form-row select {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 14px;
		flex: 1;
		min-width: 120px;
	}

	.form-row input:focus, .form-row select:focus {
		outline: none;
		border-color: #2563eb;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.info-section {
		background: #fef3c7;
		border: 1px solid #f59e0b;
		border-radius: 4px;
		padding: 12px;
		margin-top: 16px;
	}

	.info-section p {
		margin: 0 0 8px 0;
		font-size: 14px;
		color: #92400e;
	}

	.info-section ul {
		margin: 8px 0 0 20px;
		padding: 0;
	}

	.info-section li {
		margin-bottom: 4px;
		font-size: 14px;
		color: #92400e;
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
</style>
