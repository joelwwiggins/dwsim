<script lang="ts">
	import type { NodeProps } from '@xyflow/svelte';
	import { Handle, Position } from '@xyflow/svelte';

	interface UnitData {
		label: string;
		unitType: string;
		icon: string;
		properties: Record<string, any>;
	}

	let { data, selected }: { data: UnitData; selected?: boolean } = $props();

	// Define connection handles for different unit types
	const getHandles = (unitType: string) => {
		const handles = [];

		switch (unitType) {
			case 'mixer':
				handles.push(
					{ id: 'in1', type: 'target', position: Position.Left, style: 'top: 25%' },
					{ id: 'in2', type: 'target', position: Position.Left, style: 'top: 75%' },
					{ id: 'out', type: 'source', position: Position.Right, style: 'top: 50%' }
				);
				break;
			case 'splitter':
				handles.push(
					{ id: 'in', type: 'target', position: Position.Left, style: 'top: 50%' },
					{ id: 'out1', type: 'source', position: Position.Right, style: 'top: 25%' },
					{ id: 'out2', type: 'source', position: Position.Right, style: 'top: 75%' }
				);
				break;
			case 'heater':
			case 'cooler':
				handles.push(
					{ id: 'in', type: 'target', position: Position.Left, style: 'top: 50%' },
					{ id: 'out', type: 'source', position: Position.Right, style: 'top: 50%' },
					{ id: 'energy', type: 'target', position: Position.Top, style: 'left: 50%' }
				);
				break;
			case 'pump':
			case 'compressor':
				handles.push(
					{ id: 'in', type: 'target', position: Position.Left, style: 'top: 50%' },
					{ id: 'out', type: 'source', position: Position.Right, style: 'top: 50%' },
					{ id: 'energy', type: 'target', position: Position.Top, style: 'left: 50%' }
				);
				break;
			case 'valve':
				handles.push(
					{ id: 'in', type: 'target', position: Position.Left, style: 'top: 50%' },
					{ id: 'out', type: 'source', position: Position.Right, style: 'top: 50%' }
				);
				break;
			case 'heat_exchanger':
				handles.push(
					{ id: 'hot_in', type: 'target', position: Position.Left, style: 'top: 25%' },
					{ id: 'hot_out', type: 'source', position: Position.Right, style: 'top: 25%' },
					{ id: 'cold_in', type: 'target', position: Position.Left, style: 'top: 75%' },
					{ id: 'cold_out', type: 'source', position: Position.Right, style: 'top: 75%' }
				);
				break;
			case 'tank':
			case 'vessel':
				handles.push(
					{ id: 'in', type: 'target', position: Position.Top, style: 'left: 50%' },
					{ id: 'out', type: 'source', position: Position.Bottom, style: 'left: 50%' }
				);
				break;
			case 'pipe':
				handles.push(
					{ id: 'in', type: 'target', position: Position.Left, style: 'top: 50%' },
					{ id: 'out', type: 'source', position: Position.Right, style: 'top: 50%' }
				);
				break;
			default:
				// Default handles for other units
				handles.push(
					{ id: 'in', type: 'target', position: Position.Left, style: 'top: 50%' },
					{ id: 'out', type: 'source', position: Position.Right, style: 'top: 50%' }
				);
		}

		return handles;
	};

	// Get P&ID symbol for unit type
	const getSymbol = (unitType: string) => {
		switch (unitType) {
			case 'mixer':
				return `
					<circle cx="40" cy="40" r="35" fill="none" stroke="#2563eb" stroke-width="3"/>
					<path d="M15 40 L65 40 M40 15 L40 65" stroke="#2563eb" stroke-width="3"/>
					<circle cx="40" cy="40" r="8" fill="#2563eb"/>
				`;
			case 'splitter':
				return `
					<circle cx="40" cy="40" r="35" fill="none" stroke="#2563eb" stroke-width="3"/>
					<path d="M15 40 L65 40 M40 15 L40 65" stroke="#2563eb" stroke-width="3"/>
				`;
			case 'heater':
				return `
					<rect x="10" y="20" width="60" height="40" fill="none" stroke="#2563eb" stroke-width="3" rx="5"/>
					<path d="M15 35 L25 35 M15 45 L25 45" stroke="#2563eb" stroke-width="2"/>
					<text x="40" y="42" text-anchor="middle" font-size="16" fill="#2563eb">H</text>
				`;
			case 'cooler':
				return `
					<rect x="10" y="20" width="60" height="40" fill="none" stroke="#2563eb" stroke-width="3" rx="5"/>
					<path d="M15 35 L25 35 M15 45 L25 45" stroke="#2563eb" stroke-width="2"/>
					<text x="40" y="42" text-anchor="middle" font-size="16" fill="#2563eb">C</text>
				`;
			case 'pump':
				return `
					<circle cx="40" cy="40" r="30" fill="none" stroke="#2563eb" stroke-width="3"/>
					<path d="M25 40 L55 40 M40 25 L40 55" stroke="#2563eb" stroke-width="3"/>
					<circle cx="40" cy="40" r="15" fill="none" stroke="#2563eb" stroke-width="2"/>
				`;
			case 'compressor':
				return `
					<rect x="15" y="25" width="50" height="30" fill="none" stroke="#2563eb" stroke-width="3" rx="3"/>
					<path d="M20 35 L25 30 M25 30 L30 35 M30 35 L35 30 M35 30 L40 35 M40 35 L45 30 M45 30 L50 35 M50 35 L55 30" stroke="#2563eb" stroke-width="2"/>
				`;
			case 'valve':
				return `
					<path d="M20 25 L60 25 L60 55 L20 55 Z" fill="none" stroke="#2563eb" stroke-width="3"/>
					<circle cx="40" cy="40" r="8" fill="#2563eb"/>
				`;
			case 'heat_exchanger':
				return `
					<rect x="15" y="15" width="50" height="50" fill="none" stroke="#2563eb" stroke-width="3"/>
					<path d="M15 25 L65 25 M15 35 L65 35 M15 45 L65 45 M15 55 L65 55" stroke="#2563eb" stroke-width="2"/>
				`;
			case 'tank':
				return `
					<path d="M15 20 L65 20 L65 60 L15 60 Z" fill="none" stroke="#2563eb" stroke-width="3"/>
					<ellipse cx="40" cy="20" rx="25" ry="8" fill="none" stroke="#2563eb" stroke-width="3"/>
					<ellipse cx="40" cy="60" rx="25" ry="8" fill="none" stroke="#2563eb" stroke-width="3"/>
				`;
			case 'vessel':
				return `
					<ellipse cx="40" cy="25" rx="25" ry="15" fill="none" stroke="#2563eb" stroke-width="3"/>
					<rect x="15" y="25" width="50" height="30" fill="none" stroke="#2563eb" stroke-width="3"/>
					<ellipse cx="40" cy="55" rx="25" ry="15" fill="none" stroke="#2563eb" stroke-width="3"/>
				`;
			case 'pipe':
				return `
					<path d="M10 40 L70 40" stroke="#2563eb" stroke-width="6"/>
				`;
			default:
				return `
					<rect x="15" y="15" width="50" height="50" fill="none" stroke="#2563eb" stroke-width="3" rx="5"/>
					<text x="40" y="42" text-anchor="middle" font-size="20" fill="#2563eb">?</text>
				`;
		}
	};
</script>

<div class="unit-node" class:selected>
	<!-- Connection handles -->
	{#each getHandles(data.unitType) as handle (handle.id)}
		<Handle
			id={handle.id}
			type={handle.type}
			position={handle.position}
			style={handle.style}
			class="custom-handle"
		/>
	{/each}

	<!-- P&ID Symbol -->
	<svg class="pid-symbol" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
		{@html getSymbol(data.unitType)}
	</svg>

	<!-- Unit label -->
	<div class="unit-label">{data.label.replace(/^[^\s]+\s/, '')}</div>
</div>

<style>
	.unit-node {
		background: white;
		border: 2px solid #2563eb;
		border-radius: 8px;
		padding: 8px;
		min-width: 100px;
		min-height: 80px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.unit-node.selected {
		border-color: #1d4ed8;
		box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2), 0 4px 8px rgba(0, 0, 0, 0.15);
	}

	.pid-symbol {
		width: 60px;
		height: 60px;
		margin-bottom: 4px;
	}

	.unit-label {
		font-size: 0.75rem;
		font-weight: 600;
		color: #1f2937;
		text-align: center;
		line-height: 1.2;
		max-width: 80px;
		word-wrap: break-word;
	}

	/* Custom handle styling */
	:global(.custom-handle) {
		width: 12px;
		height: 12px;
		background: #2563eb;
		border: 2px solid white;
		border-radius: 50%;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
	}

	:global(.custom-handle:hover) {
		background: #1d4ed8;
		transform: scale(1.2);
	}

	:global(.custom-handle.react-flow__handle-valid) {
		background: #10b981;
	}

	:global(.custom-handle.react-flow__handle-connecting) {
		background: #f59e0b;
		animation: pulse 1.5s infinite;
	}

	@keyframes pulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.2);
		}
	}
</style>