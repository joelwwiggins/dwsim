<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface StreamData {
		id: string;
		name?: string;
		temperature?: number;
		pressure?: number;
		mass_flow_rate?: number;
		composition?: Record<string, number>;
		volumetric_flow_rate?: number;
		molar_flow_rate?: number;
		phase?: 'liquid' | 'vapor' | 'mixed';
		enthalpy?: number;
		entropy?: number;
		density?: number;
		viscosity?: number;
		thermal_conductivity?: number;
	}

	interface Props {
		stream: StreamData | null;
		isOpen: boolean;
		onClose: () => void;
		onSave: (streamData: StreamData) => void;
	}

	let { stream, isOpen, onClose, onSave }: Props = $props();

	let editedStream: StreamData = $state(null);

	// Available compounds for composition
	const availableCompounds = [
		{ id: 'water', name: 'Water', formula: 'H₂O' },
		{ id: 'methane', name: 'Methane', formula: 'CH₄' },
		{ id: 'ethane', name: 'Ethane', formula: 'C₂H₆' },
		{ id: 'propane', name: 'Propane', formula: 'C₃H₈' },
		{ id: 'butane', name: 'Butane', formula: 'C₄H₁₀' },
		{ id: 'ethanol', name: 'Ethanol', formula: 'C₂H₅OH' },
		{ id: 'methanol', name: 'Methanol', formula: 'CH₃OH' },
		{ id: 'benzene', name: 'Benzene', formula: 'C₆H₆' },
		{ id: 'toluene', name: 'Toluene', formula: 'C₇H₈' },
		{ id: 'oxygen', name: 'Oxygen', formula: 'O₂' },
		{ id: 'nitrogen', name: 'Nitrogen', formula: 'N₂' },
		{ id: 'carbon_dioxide', name: 'Carbon Dioxide', formula: 'CO₂' }
	];

	// Units for different properties
	const temperatureUnits = ['K', '°C', '°F'];
	const pressureUnits = ['Pa', 'kPa', 'MPa', 'bar', 'atm', 'psi'];
	const flowUnits = ['kg/s', 'kg/h', 'kg/day', 'mol/s', 'mol/h', 'm³/s', 'm³/h', 'ft³/s'];
	const propertyUnits = {
		enthalpy: ['J/kg', 'kJ/kg', 'BTU/lb', 'cal/g'],
		entropy: ['J/kg·K', 'kJ/kg·K', 'BTU/lb·°F'],
		density: ['kg/m³', 'g/cm³', 'lb/ft³'],
		viscosity: ['Pa·s', 'cP', 'lb/ft·s'],
		thermal_conductivity: ['W/m·K', 'BTU/hr·ft·°F']
	};

	let selectedTempUnit = $state('K');
	let selectedPressureUnit = $state('Pa');
	let selectedFlowUnit = $state('kg/s');

	// Reactive statement to update editedStream when stream prop changes
	$effect(() => {
		if (stream) {
			editedStream = { ...stream };
		} else {
			editedStream = {
				id: '',
				name: '',
				temperature: 298.15,
				pressure: 101325,
				mass_flow_rate: 1.0,
				composition: { water: 1.0 },
				phase: 'liquid'
			};
		}
	});

	function handleSave() {
		if (editedStream) {
			onSave(editedStream);
			onClose();
		}
	}

	function updateComposition(compoundId: string, value: number) {
		if (editedStream) {
			editedStream.composition = { ...editedStream.composition, [compoundId]: value };
			normalizeComposition();
		}
	}

	function normalizeComposition() {
		if (!editedStream?.composition) return;

		const total = Object.values(editedStream.composition).reduce((sum, val) => sum + val, 0);
		if (total > 0) {
			Object.keys(editedStream.composition).forEach(key => {
				editedStream.composition![key] = editedStream.composition![key] / total;
			});
		}
	}

	function addCompound(compoundId: string) {
		if (editedStream && !editedStream.composition?.[compoundId]) {
			editedStream.composition = { ...editedStream.composition, [compoundId]: 0.0 };
		}
	}

	function removeCompound(compoundId: string) {
		if (editedStream?.composition) {
			const newComposition = { ...editedStream.composition };
			delete newComposition[compoundId];
			editedStream.composition = newComposition;
			normalizeComposition();
		}
	}

	function convertTemperature(value: number, fromUnit: string, toUnit: string): number {
		if (fromUnit === toUnit) return value;

		// Convert to Kelvin first
		let kelvin = value;
		if (fromUnit === '°C') kelvin = value + 273.15;
		else if (fromUnit === '°F') kelvin = (value - 32) * 5/9 + 273.15;

		// Convert from Kelvin to target unit
		if (toUnit === '°C') return kelvin - 273.15;
		else if (toUnit === '°F') return (kelvin - 273.15) * 9/5 + 32;
		return kelvin;
	}

	function convertPressure(value: number, fromUnit: string, toUnit: string): number {
		if (fromUnit === toUnit) return value;

		const conversions = {
			Pa: 1,
			kPa: 1000,
			MPa: 1000000,
			bar: 100000,
			atm: 101325,
			psi: 6894.76
		};

		return value * conversions[fromUnit as keyof typeof conversions] / conversions[toUnit as keyof typeof conversions];
	}
</script>

{#if isOpen && editedStream}
	<div class="modal-overlay" onclick={onClose}>
		<div class="modal-content" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Material Stream Properties</h2>
				<button class="close-button" onclick={onClose}>×</button>
			</div>

			<div class="modal-body">
				<!-- Basic Properties Tab -->
				<div class="tab-content active">
					<div class="property-section">
						<h3>Stream Information</h3>
						<div class="form-row">
							<label for="stream-name">Name:</label>
							<input
								id="stream-name"
								type="text"
								bind:value={editedStream.name}
								placeholder="Enter stream name"
							/>
						</div>
						<div class="form-row">
							<label for="stream-id">ID:</label>
							<input
								id="stream-id"
								type="text"
								bind:value={editedStream.id}
								readonly
							/>
						</div>
					</div>

					<div class="property-section">
						<h3>Operating Conditions</h3>
						<div class="form-row">
							<label for="temperature">Temperature:</label>
							<div class="input-group">
								<input
									id="temperature"
									type="number"
									step="0.01"
									bind:value={editedStream.temperature}
								/>
								<select bind:value={selectedTempUnit}>
									{#each temperatureUnits as unit}
										<option value={unit}>{unit}</option>
									{/each}
								</select>
							</div>
						</div>
						<div class="form-row">
							<label for="pressure">Pressure:</label>
							<div class="input-group">
								<input
									id="pressure"
									type="number"
									step="0.01"
									bind:value={editedStream.pressure}
								/>
								<select bind:value={selectedPressureUnit}>
									{#each pressureUnits as unit}
										<option value={unit}>{unit}</option>
									{/each}
								</select>
							</div>
						</div>
					</div>

					<div class="property-section">
						<h3>Flow Rates</h3>
						<div class="form-row">
							<label for="mass-flow">Mass Flow Rate:</label>
							<div class="input-group">
								<input
									id="mass-flow"
									type="number"
									step="0.001"
									bind:value={editedStream.mass_flow_rate}
								/>
								<select bind:value={selectedFlowUnit}>
									{#each flowUnits as unit}
										<option value={unit}>{unit}</option>
									{/each}
								</select>
							</div>
						</div>
						<div class="form-row">
							<label for="molar-flow">Molar Flow Rate:</label>
							<div class="input-group">
								<input
									id="molar-flow"
									type="number"
									step="0.001"
									bind:value={editedStream.molar_flow_rate}
									readonly
								/>
								<span class="unit-label">mol/s</span>
							</div>
						</div>
						<div class="form-row">
							<label for="volumetric-flow">Volumetric Flow Rate:</label>
							<div class="input-group">
								<input
									id="volumetric-flow"
									type="number"
									step="0.001"
									bind:value={editedStream.volumetric_flow_rate}
									readonly
								/>
								<span class="unit-label">m³/s</span>
							</div>
						</div>
					</div>

					<div class="property-section">
						<h3>Composition</h3>
						<div class="composition-controls">
							<select onchange={(e) => addCompound(e.target.value)}>
								<option value="">Add Compound...</option>
								{#each availableCompounds as compound}
									{#if !editedStream.composition?.[compound.id]}
										<option value={compound.id}>{compound.name} ({compound.formula})</option>
									{/if}
								{/each}
							</select>
						</div>
						<div class="composition-table">
							<div class="table-header">
								<span>Compound</span>
								<span>Mole Fraction</span>
								<span>Mass Fraction</span>
								<span>Actions</span>
							</div>
							{#each Object.entries(editedStream.composition || {}) as [compoundId, moleFraction]}
								{@const compound = availableCompounds.find(c => c.id === compoundId)}
								<div class="table-row">
									<span class="compound-name">
										{compound?.name || compoundId} ({compound?.formula || compoundId})
									</span>
									<input
										type="number"
										min="0"
										max="1"
										step="0.001"
										value={moleFraction.toFixed(4)}
										oninput={(e) => updateComposition(compoundId, parseFloat(e.target.value) || 0)}
									/>
									<span class="mass-fraction">--</span>
									<button
										class="remove-btn"
										onclick={() => removeCompound(compoundId)}
										title="Remove compound"
									>×</button>
								</div>
							{/each}
						</div>
					</div>

					<div class="property-section">
						<h3>Physical Properties</h3>
						<div class="properties-grid">
							<div class="property-item">
								<label>Phase:</label>
								<select bind:value={editedStream.phase}>
									<option value="liquid">Liquid</option>
									<option value="vapor">Vapor</option>
									<option value="mixed">Mixed</option>
								</select>
							</div>
							<div class="property-item">
								<label>Density:</label>
								<div class="input-group">
									<input
										type="number"
										step="0.001"
										bind:value={editedStream.density}
										readonly
									/>
									<span class="unit-label">kg/m³</span>
								</div>
							</div>
							<div class="property-item">
								<label>Viscosity:</label>
								<div class="input-group">
									<input
										type="number"
										step="0.000001"
										bind:value={editedStream.viscosity}
										readonly
									/>
									<span class="unit-label">Pa·s</span>
								</div>
							</div>
							<div class="property-item">
								<label>Thermal Conductivity:</label>
								<div class="input-group">
									<input
										type="number"
										step="0.001"
										bind:value={editedStream.thermal_conductivity}
										readonly
									/>
									<span class="unit-label">W/m·K</span>
								</div>
							</div>
							<div class="property-item">
								<label>Enthalpy:</label>
								<div class="input-group">
									<input
										type="number"
										step="0.001"
										bind:value={editedStream.enthalpy}
										readonly
									/>
									<span class="unit-label">kJ/kg</span>
								</div>
							</div>
							<div class="property-item">
								<label>Entropy:</label>
								<div class="input-group">
									<input
										type="number"
										step="0.001"
										bind:value={editedStream.entropy}
										readonly
									/>
									<span class="unit-label">kJ/kg·K</span>
								</div>
							</div>
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
		max-width: 900px;
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
		min-width: 60px;
		text-align: center;
	}

	.composition-controls {
		margin-bottom: 16px;
	}

	.composition-controls select {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 14px;
		min-width: 200px;
	}

	.composition-table {
		border: 1px solid #e5e7eb;
		border-radius: 4px;
		overflow: hidden;
	}

	.table-header {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr 80px;
		gap: 12px;
		padding: 12px 16px;
		background: #f9fafb;
		border-bottom: 1px solid #e5e7eb;
		font-weight: 600;
		font-size: 14px;
		color: #374151;
	}

	.table-row {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr 80px;
		gap: 12px;
		padding: 12px 16px;
		border-bottom: 1px solid #f3f4f6;
		align-items: center;
	}

	.table-row:last-child {
		border-bottom: none;
	}

	.compound-name {
		font-weight: 500;
		color: #374151;
	}

	.table-row input {
		padding: 6px 8px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 14px;
		text-align: center;
	}

	.mass-fraction {
		text-align: center;
		color: #6b7280;
		font-size: 14px;
	}

	.remove-btn {
		background: #ef4444;
		color: white;
		border: none;
		border-radius: 4px;
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		font-size: 16px;
		font-weight: bold;
	}

	.remove-btn:hover {
		background: #dc2626;
	}

	.properties-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 16px;
	}

	.property-item {
		display: flex;
		align-items: center;
	}

	.property-item label {
		min-width: 120px;
		font-weight: 500;
		color: #374151;
		margin-right: 12px;
	}

	.property-item select {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 14px;
		flex: 1;
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

		.properties-grid {
			grid-template-columns: 1fr;
		}

		.table-header,
		.table-row {
			grid-template-columns: 1fr;
			gap: 8px;
		}

		.table-row {
			padding: 8px 12px;
		}
	}
</style>