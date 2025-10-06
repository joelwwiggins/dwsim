<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface PipeData {
		label: string;
		unitType: string;
		length: number;
		diameter: number;
		roughness: number;
		elevation_change: number;
		ambient_temperature: number;
		heat_transfer_coeff_outside: number;
		insulation_thickness: number;
		insulation_conductivity: number;
		flow_regime: 'laminar' | 'transitional' | 'turbulent';
	}

	interface Props {
		unit: PipeData;
		isOpen: boolean;
		onClose: () => void;
		onSave: (data: PipeData) => void;
	}

	let { unit, isOpen, onClose, onSave }: Props = $props();

	let editedUnit: PipeData = $state(null);

	// Reactive statement to update editedUnit when unit prop changes
	$effect(() => {
		if (unit) {
			editedUnit = { ...unit };
		} else {
			editedUnit = {
				label: '',
				unitType: 'pipe',
				length: 100.0,
				diameter: 0.1,
				roughness: 0.000046,
				elevation_change: 0.0,
				ambient_temperature: 298.15,
				heat_transfer_coeff_outside: 5.0,
				insulation_thickness: 0.0,
				insulation_conductivity: 0.04,
				flow_regime: 'turbulent'
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
				<h2>Pipe Properties</h2>
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
							placeholder="Pipe name"
						/>
					</div>
					<div class="form-row">
						<label for="flow-regime">Flow Regime:</label>
						<select id="flow-regime" bind:value={editedUnit.flow_regime}>
							<option value="laminar">Laminar</option>
							<option value="transitional">Transitional</option>
							<option value="turbulent">Turbulent</option>
						</select>
					</div>
				</div>

				<div class="form-section">
					<h3>Pipe Dimensions</h3>
					<div class="form-row">
						<label for="length">Length (m):</label>
						<input
							id="length"
							type="number"
							step="0.1"
							min="0.1"
							bind:value={editedUnit.length}
						/>
					</div>
					<div class="form-row">
						<label for="diameter">Diameter (m):</label>
						<input
							id="diameter"
							type="number"
							step="0.001"
							min="0.001"
							bind:value={editedUnit.diameter}
						/>
					</div>
					<div class="form-row">
						<label for="roughness">Roughness (m):</label>
						<input
							id="roughness"
							type="number"
							step="0.000001"
							min="0"
							bind:value={editedUnit.roughness}
						/>
					</div>
					<div class="form-row">
						<label for="elevation">Elevation Change (m):</label>
						<input
							id="elevation"
							type="number"
							step="0.1"
							bind:value={editedUnit.elevation_change}
						/>
					</div>
				</div>

				<div class="form-section">
					<h3>Heat Transfer</h3>
					<div class="form-row">
						<label for="ambient-temp">Ambient Temperature (K):</label>
						<input
							id="ambient-temp"
							type="number"
							step="0.01"
							bind:value={editedUnit.ambient_temperature}
						/>
					</div>
					<div class="form-row">
						<label for="htc-outside">Outside Heat Transfer Coefficient (W/m²·K):</label>
						<input
							id="htc-outside"
							type="number"
							step="0.1"
							min="0"
							bind:value={editedUnit.heat_transfer_coeff_outside}
						/>
					</div>
					<div class="form-row">
						<label for="insulation-thickness">Insulation Thickness (m):</label>
						<input
							id="insulation-thickness"
							type="number"
							step="0.001"
							min="0"
							bind:value={editedUnit.insulation_thickness}
						/>
					</div>
					<div class="form-row">
						<label for="insulation-k">Insulation Thermal Conductivity (W/m·K):</label>
						<input
							id="insulation-k"
							type="number"
							step="0.001"
							min="0.001"
							bind:value={editedUnit.insulation_conductivity}
						/>
					</div>
				</div>

				<div class="info-section">
					<p><strong>Note:</strong> Pipe calculations include pressure drop due to friction, elevation changes, and heat loss/gain to ambient.</p>
					<p><strong>Flow regimes:</strong></p>
					<ul>
						<li><strong>Laminar:</strong> Re < 2100 (smooth, predictable flow)</li>
						<li><strong>Transitional:</strong> 2100 < Re < 4000 (unstable flow)</li>
						<li><strong>Turbulent:</strong> Re > 4000 (chaotic, efficient mixing)</li>
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
		max-width: 600px;
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
		min-width: 220px;
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
