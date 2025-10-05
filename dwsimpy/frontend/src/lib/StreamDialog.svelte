<script lang="ts">
	import type { Node } from 'svelte-flow';

	interface StreamData extends Record<string, unknown> {
		id: string;
		name?: string;
		temperature?: number;
		pressure?: number;
		mass_flow_rate?: number;
		composition?: Record<string, number>;
	}

	interface Props {
		stream: Node<StreamData> | null;
		isOpen: boolean;
		onClose: () => void;
		onSave: (streamData: StreamData) => void;
	}

	let { stream, isOpen, onClose, onSave }: Props = $props();

	let localStream: StreamData = $state({
		id: '',
		name: '',
		temperature: 298.15,
		pressure: 101325,
		mass_flow_rate: 1.0,
		composition: { water: 1.0 }
	});

	// Update local stream when stream prop changes
	$effect(() => {
		if (stream) {
			localStream = {
				...stream.data,
				temperature: stream.data.temperature ?? 298.15,
				pressure: stream.data.pressure ?? 101325,
				mass_flow_rate: stream.data.mass_flow_rate ?? 1.0,
				composition: stream.data.composition ?? { water: 1.0 }
			};
		}
	});

	function updateComposition(component: string, value: number) {
		localStream.composition = {
			...localStream.composition,
			[component]: value
		};
	}

	function addComponent() {
		const component = prompt('Enter component name:');
		if (component && !localStream.composition![component]) {
			updateComposition(component, 0);
		}
	}

	function removeComponent(component: string) {
		const newComposition = { ...localStream.composition };
		delete newComposition[component];
		localStream.composition = newComposition;
	}

	function normalizeComposition() {
		const total = Object.values(localStream.composition!).reduce((sum, val) => sum + val, 0);
		if (total > 0) {
			const normalized: Record<string, number> = {};
			for (const [comp, val] of Object.entries(localStream.composition!)) {
				normalized[comp] = val / total;
			}
			localStream.composition = normalized;
		}
	}

	function handleSave() {
		normalizeComposition();
		onSave(localStream);
		onClose();
	}

	// Calculate total composition
	let totalComposition = $derived(() => {
		return Object.values(localStream.composition!).reduce((sum, val) => sum + val, 0);
	});
</script>

{#if isOpen && stream}
	<div class="dialog-overlay" onclick={onClose} onkeydown={(e) => { if (e.key === 'Escape') onClose(); }} role="dialog" aria-modal="true" aria-labelledby="dialog-title">
		<div class="dialog" onclick={(e) => e.stopPropagation()}>
			<div class="dialog-header">
				<h3 id="dialog-title">Edit Stream Properties</h3>
				<button class="close-button" onclick={onClose} aria-label="Close dialog">×</button>
			</div>

			<div class="dialog-body">
				<div class="form-group">
					<label for="stream-name">Stream Name:</label>
					<input
						id="stream-name"
						type="text"
						bind:value={localStream.name}
						placeholder="Enter stream name"
					/>
				</div>

				<div class="form-group">
					<label for="temperature">Temperature (°C):</label>
					<input
						id="temperature"
						type="number"
						step="0.1"
						bind:value={localStream.temperature}
					/>
				</div>

				<div class="form-group">
					<label for="pressure">Pressure (Pa):</label>
					<input
						id="pressure"
						type="number"
						step="100"
						bind:value={localStream.pressure}
					/>
				</div>

				<div class="form-group">
					<label for="mass-flow">Mass Flow Rate (kg/s):</label>
					<input
						id="mass-flow"
						type="number"
						step="0.1"
						bind:value={localStream.mass_flow_rate}
					/>
				</div>

				<div class="composition-section">
					<div class="composition-header">
						<h4>Composition (mass fractions)</h4>
						<div class="composition-actions">
							<button class="action-button" onclick={addComponent}>Add Component</button>
							<button class="action-button" onclick={normalizeComposition}>Normalize</button>
						</div>
					</div>

					<div class="total-composition">
						Total: {totalComposition().toFixed(3)}
						{#if Math.abs(totalComposition() - 1.0) > 0.001}
							<span class="warning">(should be 1.0)</span>
						{/if}
					</div>

					<div class="composition-list">
						{#each Object.entries(localStream.composition!) as [component, fraction] (component)}
							<div class="composition-item">
								<span class="component-name">{component}:</span>
								<input
									type="number"
									step="0.01"
									min="0"
									max="1"
									value={fraction}
									oninput={(e) => updateComposition(component, parseFloat((e.target as HTMLInputElement).value) || 0)}
								/>
								<button class="remove-button" onclick={() => removeComponent(component)}>×</button>
							</div>
						{/each}
					</div>
				</div>
			</div>

			<div class="dialog-footer">
				<button class="cancel-button" onclick={onClose}>Cancel</button>
				<button class="save-button" onclick={handleSave}>Save</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.dialog-overlay {
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

	.dialog {
		background: white;
		border-radius: 8px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
		max-width: 500px;
		width: 90%;
		max-height: 80vh;
		overflow-y: auto;
	}

	.dialog-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.dialog-header h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #374151;
	}

	.close-button {
		background: none;
		border: none;
		font-size: 1.5rem;
		cursor: pointer;
		color: #6b7280;
		padding: 0;
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.close-button:hover {
		color: #374151;
	}

	.dialog-body {
		padding: 1.5rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #374151;
	}

	.form-group input {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		font-size: 0.875rem;
	}

	.form-group input:focus {
		outline: none;
		border-color: #2563eb;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
	}

	.composition-section {
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.composition-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.composition-header h4 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: #374151;
	}

	.composition-actions {
		display: flex;
		gap: 0.5rem;
	}

	.action-button {
		padding: 0.25rem 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		background: white;
		color: #374151;
		font-size: 0.75rem;
		cursor: pointer;
	}

	.action-button:hover {
		background: #f9fafb;
		border-color: #9ca3af;
	}

	.total-composition {
		font-size: 0.875rem;
		color: #6b7280;
		margin-bottom: 1rem;
	}

	.warning {
		color: #dc2626;
		font-weight: 500;
	}

	.composition-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.composition-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.component-name {
		min-width: 80px;
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
	}

	.composition-item input {
		flex: 1;
		padding: 0.25rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		font-size: 0.875rem;
	}

	.remove-button {
		background: #dc2626;
		color: white;
		border: none;
		border-radius: 0.375rem;
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		font-size: 0.75rem;
	}

	.remove-button:hover {
		background: #b91c1c;
	}

	.dialog-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1rem 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.cancel-button {
		padding: 0.5rem 1rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		background: white;
		color: #374151;
		cursor: pointer;
	}

	.cancel-button:hover {
		background: #f9fafb;
	}

	.save-button {
		padding: 0.5rem 1rem;
		border: 1px solid #2563eb;
		border-radius: 0.375rem;
		background: #2563eb;
		color: white;
		cursor: pointer;
	}

	.save-button:hover {
		background: #1d4ed8;
	}
</style>