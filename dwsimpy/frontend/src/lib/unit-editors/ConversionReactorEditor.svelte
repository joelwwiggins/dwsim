<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface ReactionData {
		id: string;
		name?: string;
		stoichiometry: Record<string, number>;
		conversion: number;
	}

	interface ConversionReactorData {
		label: string;
		unitType: string;
		operation_mode: 'isothermal' | 'adiabatic' | 'heat_duty';
		target_temperature?: number;
		heat_duty?: number;
		pressure_drop: number;
		reactions: ReactionData[];
	}

	interface Props {
		unit: ConversionReactorData;
		isOpen: boolean;
		onClose: () => void;
		onSave: (data: ConversionReactorData) => void;
	}

	let { unit, isOpen, onClose, onSave }: Props = $props();

	let editedUnit: ConversionReactorData = $state(null);

	// Available compounds for reactions
	const availableCompounds = [
		{ id: 'methane', name: 'Methane', formula: 'CH₄' },
		{ id: 'ethane', name: 'Ethane', formula: 'C₂H₆' },
		{ id: 'propane', name: 'Propane', formula: 'C₃H₈' },
		{ id: 'butane', name: 'Butane', formula: 'C₄H₁₀' },
		{ id: 'hydrogen', name: 'Hydrogen', formula: 'H₂' },
		{ id: 'oxygen', name: 'Oxygen', formula: 'O₂' },
		{ id: 'nitrogen', name: 'Nitrogen', formula: 'N₂' },
		{ id: 'carbon_dioxide', name: 'Carbon Dioxide', formula: 'CO₂' },
		{ id: 'water', name: 'Water', formula: 'H₂O' },
		{ id: 'carbon_monoxide', name: 'Carbon Monoxide', formula: 'CO' }
	];

	// Reactive statement to update editedUnit when unit prop changes
	$effect(() => {
		if (unit) {
			editedUnit = {
				...unit,
				reactions: unit.reactions ? [...unit.reactions] : []
			};
		} else {
			editedUnit = {
				label: '',
				unitType: 'conversion_reactor',
				operation_mode: 'adiabatic',
				pressure_drop: 0,
				reactions: []
			};
		}
	});

	function handleSave() {
		if (editedUnit) {
			onSave(editedUnit);
			onClose();
		}
	}

	function addReaction() {
		if (editedUnit) {
			const newReaction: ReactionData = {
				id: `reaction_${Date.now()}`,
				name: `Reaction ${editedUnit.reactions.length + 1}`,
				stoichiometry: {},
				conversion: 0.5
			};
			editedUnit.reactions = [...editedUnit.reactions, newReaction];
		}
	}

	function removeReaction(index: number) {
		if (editedUnit) {
			editedUnit.reactions = editedUnit.reactions.filter((_, i) => i !== index);
		}
	}

	function updateStoichiometry(reactionIndex: number, compoundId: string, coefficient: number) {
		if (editedUnit && editedUnit.reactions[reactionIndex]) {
			editedUnit.reactions[reactionIndex].stoichiometry[compoundId] = coefficient;
			editedUnit.reactions = [...editedUnit.reactions]; // Trigger reactivity
		}
	}

	function removeCompoundFromReaction(reactionIndex: number, compoundId: string) {
		if (editedUnit && editedUnit.reactions[reactionIndex]) {
			delete editedUnit.reactions[reactionIndex].stoichiometry[compoundId];
			editedUnit.reactions = [...editedUnit.reactions]; // Trigger reactivity
		}
	}

	function addCompoundToReaction(reactionIndex: number, compoundId: string) {
		if (editedUnit && editedUnit.reactions[reactionIndex]) {
			if (!(compoundId in editedUnit.reactions[reactionIndex].stoichiometry)) {
				editedUnit.reactions[reactionIndex].stoichiometry[compoundId] = 1.0;
				editedUnit.reactions = [...editedUnit.reactions]; // Trigger reactivity
			}
		}
	}
</script>

{#if isOpen && editedUnit}
	<div class="modal-overlay" onclick={onClose}>
		<div class="modal-content" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Conversion Reactor Properties</h2>
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
							placeholder="Reactor name"
						/>
					</div>
					<div class="form-row">
						<label for="operation-mode">Operation Mode:</label>
						<select id="operation-mode" bind:value={editedUnit.operation_mode}>
							<option value="isothermal">Isothermal</option>
							<option value="adiabatic">Adiabatic</option>
							<option value="heat_duty">Heat Duty</option>
						</select>
					</div>
					{#if editedUnit.operation_mode === 'isothermal'}
						<div class="form-row">
							<label for="target-temperature">Target Temperature (K):</label>
							<input
								id="target-temperature"
								type="number"
								step="0.1"
								bind:value={editedUnit.target_temperature}
							/>
						</div>
					{/if}
					{#if editedUnit.operation_mode === 'heat_duty'}
						<div class="form-row">
							<label for="heat-duty">Heat Duty (kW):</label>
							<input
								id="heat-duty"
								type="number"
								step="0.1"
								bind:value={editedUnit.heat_duty}
							/>
						</div>
					{/if}
					<div class="form-row">
						<label for="pressure-drop">Pressure Drop (Pa):</label>
						<input
							id="pressure-drop"
							type="number"
							step="1"
							bind:value={editedUnit.pressure_drop}
						/>
					</div>
				</div>

				<div class="form-section">
					<h3>Reactions</h3>
					<div class="reactions-list">
						{#each editedUnit.reactions as reaction, reactionIndex (reaction.id)}
							<div class="reaction-item">
								<div class="reaction-header">
									<input
										type="text"
										placeholder="Reaction name"
										bind:value={reaction.name}
										class="reaction-name"
									/>
									<div class="reaction-controls">
										<label>Conversion:</label>
										<input
											type="number"
											min="0"
											max="1"
											step="0.01"
											bind:value={reaction.conversion}
											class="conversion-input"
										/>
										<button
											class="remove-btn"
											onclick={() => removeReaction(reactionIndex)}
											title="Remove reaction"
										>×</button>
									</div>
								</div>

								<div class="stoichiometry">
									<h4>Stoichiometry</h4>
									<div class="stoichiometry-grid">
										{#each Object.entries(reaction.stoichiometry) as [compoundId, coeff]}
											{@const compound = availableCompounds.find(c => c.id === compoundId)}
											<div class="stoichiometry-row">
												<span class="compound-name">
													{compound?.name || compoundId} ({compound?.formula || compoundId})
												</span>
												<input
													type="number"
													step="0.1"
													value={coeff}
													oninput={(e) => updateStoichiometry(reactionIndex, compoundId, parseFloat(e.target.value) || 0)}
													class="coeff-input"
												/>
												<button
													class="remove-compound-btn"
													onclick={() => removeCompoundFromReaction(reactionIndex, compoundId)}
													title="Remove compound"
												>−</button>
											</div>
										{/each}
									</div>

									<div class="add-compound">
										<select onchange={(e) => {
											const compoundId = e.target.value;
											if (compoundId) {
												addCompoundToReaction(reactionIndex, compoundId);
												e.target.value = '';
											}
										}}>
											<option value="">Add Compound...</option>
											{#each availableCompounds as compound}
												{#if !(compound.id in reaction.stoichiometry)}
													<option value={compound.id}>{compound.name} ({compound.formula})</option>
												{/if}
											{/each}
										</select>
									</div>
								</div>
							</div>
						{/each}
					</div>

					<button class="add-reaction-btn" onclick={addReaction}>
						+ Add Reaction
					</button>
				</div>

				<div class="info-section">
					<p><strong>Note:</strong> Coefficients should be negative for reactants and positive for products. Conversion is the fraction of limiting reactant that reacts.</p>
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
		max-width: 800px;
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
		min-width: 150px;
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

	.reactions-list {
		margin-bottom: 16px;
	}

	.reaction-item {
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		padding: 16px;
		margin-bottom: 12px;
		background: #f9fafb;
	}

	.reaction-header {
		display: flex;
		align-items: center;
		margin-bottom: 12px;
		gap: 12px;
	}

	.reaction-name {
		flex: 1;
		padding: 6px 8px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 14px;
	}

	.reaction-controls {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.conversion-input {
		width: 80px;
		padding: 4px 6px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 12px;
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

	.stoichiometry h4 {
		margin: 0 0 8px 0;
		font-size: 0.9rem;
		font-weight: 600;
		color: #374151;
	}

	.stoichiometry-grid {
		margin-bottom: 8px;
	}

	.stoichiometry-row {
		display: flex;
		align-items: center;
		margin-bottom: 4px;
		gap: 8px;
	}

	.compound-name {
		flex: 1;
		font-size: 14px;
		color: #374151;
	}

	.coeff-input {
		width: 80px;
		padding: 4px 6px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 12px;
		text-align: center;
	}

	.remove-compound-btn {
		background: #f3f4f6;
		color: #6b7280;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		width: 20px;
		height: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		font-size: 12px;
	}

	.remove-compound-btn:hover {
		background: #e5e7eb;
		color: #374151;
	}

	.add-compound select {
		width: 100%;
		padding: 6px 8px;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		font-size: 12px;
	}

	.add-reaction-btn {
		background: #2563eb;
		color: white;
		border: none;
		border-radius: 4px;
		padding: 8px 16px;
		cursor: pointer;
		font-size: 14px;
		font-weight: 500;
	}

	.add-reaction-btn:hover {
		background: #1d4ed8;
	}

	.info-section {
		background: #fef3c7;
		border: 1px solid #f59e0b;
		border-radius: 4px;
		padding: 12px;
		margin-top: 16px;
	}

	.info-section p {
		margin: 0;
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
