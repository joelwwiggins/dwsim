<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface UnitType {
		id: string;
		name: string;
		icon: string;
	}

	interface Props {
		unitTypes: UnitType[];
		onAddStream?: () => void;
	}

	let { unitTypes, onAddStream }: Props = $props();

	function onDragStart(event: DragEvent, unitType: UnitType) {
		event.dataTransfer?.setData('application/unit-type', unitType.id);
		event.dataTransfer!.effectAllowed = 'copy';
	}
</script>

<div class="unit-palette">
	<h3 class="palette-title">Unit Operations</h3>
	<div class="unit-list">
		{#if onAddStream}
			<button class="add-stream-button" onclick={onAddStream}>
				<span class="unit-icon">🌊</span>
				<span class="unit-name">Add Stream</span>
			</button>
		{/if}
		{#each unitTypes as unitType (unitType.id)}
			<div
				class="unit-item"
				draggable="true"
				ondragstart={(e) => onDragStart(e, unitType)}
				role="button"
				tabindex="0"
			>
				<span class="unit-icon">{unitType.icon}</span>
				<span class="unit-name">{unitType.name}</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.unit-palette {
		width: 250px;
		background: white;
		border-right: 1px solid #e5e7eb;
		padding: 1rem;
		display: flex;
		flex-direction: column;
	}

	.palette-title {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: 1rem;
		color: #374151;
	}

	.unit-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		flex: 1;
		overflow-y: auto;
	}

	.unit-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		background: white;
		cursor: grab;
		transition: all 0.2s;
	}

	.unit-item:hover {
		background: #f9fafb;
		border-color: #d1d5db;
		box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
	}

	.unit-item:active {
		cursor: grabbing;
	}

	.unit-icon {
		font-size: 1.25rem;
	}

	.unit-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
		flex: 1;
	}

	.add-stream-button {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		background: #f9fafb;
		color: #374151;
		cursor: pointer;
		transition: all 0.2s;
		width: 100%;
		font-size: 0.875rem;
		font-weight: 500;
		margin-bottom: 1rem;
	}

	.add-stream-button:hover {
		background: #f3f4f6;
		border-color: #d1d5db;
	}
</style>