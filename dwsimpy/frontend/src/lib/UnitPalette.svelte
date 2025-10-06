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

	function getPidSymbol(unitType: UnitType) {
		switch (unitType.id) {
			case 'pump':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="15" fill="none" stroke="#374151" stroke-width="2"/><path d="M15 15 L25 20 L15 25 Z" fill="#374151"/></svg>`;
			case 'heater':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="5" width="30" height="30" fill="none" stroke="#374151" stroke-width="2"/><path d="M10 10 L30 30" stroke="#374151" stroke-width="2"/><path d="M30 10 L10 30" stroke="#374151" stroke-width="2"/></svg>`;
			case 'valve':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M10 20 L30 20" stroke="#374151" stroke-width="3"/><circle cx="20" cy="20" r="8" fill="none" stroke="#374151" stroke-width="2"/><path d="M16 16 L24 24" stroke="#374151" stroke-width="2"/><path d="M24 16 L16 24" stroke="#374151" stroke-width="2"/></svg>`;
			case 'mixer':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="15" fill="none" stroke="#374151" stroke-width="2"/><path d="M5 20 L15 15 M5 20 L15 25" stroke="#374151" stroke-width="2"/><path d="M35 20 L25 15 M35 20 L25 25" stroke="#374151" stroke-width="2"/><circle cx="20" cy="20" r="3" fill="#374151"/></svg>`;
			case 'separator':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="5" width="30" height="30" fill="none" stroke="#374151" stroke-width="2"/><path d="M5 20 L35 20" stroke="#374151" stroke-width="2"/><path d="M20 5 L20 35" stroke="#374151" stroke-width="2"/></svg>`;
			case 'reactor':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="5" width="30" height="30" fill="none" stroke="#374151" stroke-width="2"/><circle cx="20" cy="20" r="8" fill="none" stroke="#374151" stroke-width="2"/><text x="20" y="24" text-anchor="middle" font-size="8" fill="#374151">R</text></svg>`;
			case 'compressor':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="15" fill="none" stroke="#374151" stroke-width="2"/><path d="M10 15 Q20 10 30 15 Q20 20 10 15 Z" fill="#374151"/><path d="M10 25 Q20 30 30 25 Q20 20 10 25 Z" fill="none" stroke="#374151" stroke-width="2"/></svg>`;
			case 'turbine':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="15" fill="none" stroke="#374151" stroke-width="2"/><path d="M10 15 Q20 10 30 15 Q20 20 10 15 Z" fill="none" stroke="#374151" stroke-width="2"/><path d="M10 25 Q20 30 30 25 Q20 20 10 25 Z" fill="#374151"/></svg>`;
			case 'heat-exchanger':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="5" width="30" height="30" fill="none" stroke="#374151" stroke-width="2"/><path d="M10 10 L30 10 M10 15 L30 15 M10 20 L30 20 M10 25 L30 25 M10 30 L30 30" stroke="#374151" stroke-width="1"/></svg>`;
			case 'cooler':
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="5" width="30" height="30" fill="none" stroke="#374151" stroke-width="2"/><path d="M10 10 L30 30" stroke="#374151" stroke-width="2"/><path d="M30 10 L10 30" stroke="#374151" stroke-width="2"/><circle cx="15" cy="15" r="2" fill="#374151"/><circle cx="25" cy="25" r="2" fill="#374151"/></svg>`;
			default:
				return `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><rect x="5" y="5" width="30" height="30" fill="none" stroke="#374151" stroke-width="2"/><text x="20" y="24" text-anchor="middle" font-size="8" fill="#374151">?</text></svg>`;
		}
	}
</script>

<div class="unit-palette">
	<h3 class="palette-title">Unit Operations</h3>
	<div class="unit-list">
		{#if onAddStream}
			<button class="add-stream-button" onclick={onAddStream}>
				<span class="unit-icon">
					<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
						<path d="M10 20 L30 20" stroke="#374151" stroke-width="4" stroke-linecap="round"/>
						<path d="M25 15 L30 20 L25 25" fill="#374151"/>
						<circle cx="20" cy="20" r="3" fill="#374151"/>
					</svg>
				</span>
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
				<span class="unit-icon">
					{@html getPidSymbol(unitType)}
				</span>
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
		width: 2rem;
		height: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.unit-icon svg {
		width: 100%;
		height: 100%;
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

	.add-stream-button .unit-icon svg {
		width: 2rem;
		height: 2rem;
	}
</style>