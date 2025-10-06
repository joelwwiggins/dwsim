<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface DistillationColumnData {
		label: string;
		unitType: string;
		number_of_stages: number;
		feed_stage: number;
		reflux_ratio?: number;
		distillate_rate?: number;
		bottoms_rate?: number;
		condenser_type: 'total' | 'partial';
		reboiler_type: 'kettle' | 'thermosiphon';
	}

	interface Props {
		unit: DistillationColumnData;
		isOpen: boolean;
		onClose: () => void;
		onSave: (data: DistillationColumnData) => void;
	}

	let { unit, isOpen, onClose, onSave }: Props = $props();

	let editedUnit: DistillationColumnData = $state(null);

	// Reactive statement to update editedUnit when unit prop changes
	$effect(() => {
		if (unit) {
			editedUnit = { ...unit };
		} else {
			editedUnit = {
				label: '',
				unitType: 'distillation_column',
				number_of_stages: 10,
				feed_stage: 5,
				reflux_ratio: 2.0,
				condenser_type: 'total',
				reboiler_type: 'kettle'
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
				<h2>Distillation Column Properties</h2>
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
							placeholder="Column name"
						/>
					</div>
					<div class="form-row">
						<label for="stages">Number of Stages:</label>
						<input
							id="stages"
							type="number"
							min="2"
							max="100"
							bind:value={editedUnit.number_of_stages}
						/>
					</div>
					<div class="form-row">
						<label for="feed-stage">Feed Stage:</label>
						<input
							id="feed-stage"
							type="number"
							min="1"
							max={editedUnit.number_of_stages}
							bind:value={editedUnit.feed_stage}
						/>
					</div>
				</div>

				<div class="form-section">
					<h3>Specifications</h3>
					<div class="form-row">
						<label for="reflux-ratio">Reflux Ratio:</label>
						<input
							id="reflux-ratio"
							type="number"
							min="0"
							step="0.1"
							bind:value={editedUnit.reflux_ratio}
							placeholder="L/D"
						/>
					</div>
					<div class="form-row">
						<label for="distillate-rate">Distillate Rate (kmol/h):</label>
						<input
							id="distillate-rate"
							type="number"
							min="0"
							step="0.1"
							bind:value={editedUnit.distillate_rate}
							placeholder="Optional"
						/>
					</div>
					<div class="form-row">
						<label for="bottoms-rate">Bottoms Rate (kmol/h):</label>
						<input
							id="bottoms-rate"
							type="number"
							min="0"
							step="0.1"
							bind:value={editedUnit.bottoms_rate}
							placeholder="Optional"
						/>
					</div>
				</div>

				<div class="form-section">
					<h3>Equipment Types</h3>
					<div class="form-row">
						<label for="condenser-type">Condenser Type:</label>
						<select id="condenser-type" bind:value={editedUnit.condenser_type}>
							<option value="total">Total Condenser</option>
							<option value="partial">Partial Condenser</option>
						</select>
					</div>
					<div class="form-row">
						<label for="reboiler-type">Reboiler Type:</label>
						<select id="reboiler-type" bind:value={editedUnit.reboiler_type}>
							<option value="kettle">Kettle Reboiler</option>
							<option value="thermosiphon">Thermosiphon Reboiler</option>
						</select>
					</div>
				</div>

				<div class="info-section">
					<p><strong>Note:</strong> The distillation column uses a simplified multi-stage flash calculation. For rigorous design, additional specifications may be needed.</p>
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
