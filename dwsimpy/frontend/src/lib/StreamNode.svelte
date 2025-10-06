<script lang="ts">
	import type { NodeProps } from '@xyflow/svelte';
	import { Handle, Position } from '@xyflow/svelte';

	interface StreamData {
		id: string;
		name?: string;
		temperature?: number;
		pressure?: number;
		mass_flow_rate?: number;
		composition?: Record<string, number>;
	}

	let { data, selected }: { data: StreamData; selected?: boolean } = $props();
</script>

<div class="stream-node" class:selected>
	<!-- Connection handles for streams -->
	<Handle
		id="source"
		type="source"
		position={Position.Left}
		class="stream-handle"
	/>
	<Handle
		id="target"
		type="target"
		position={Position.Right}
		class="stream-handle"
	/>

	<!-- Stream P&ID symbol -->
	<svg class="stream-symbol" viewBox="0 0 80 40" xmlns="http://www.w3.org/2000/svg">
		<!-- Main stream line -->
		<path d="M10 20 L70 20" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
		<!-- Arrowhead -->
		<path d="M65 15 L70 20 L65 25" fill="#2563eb"/>
		<!-- Flow direction indicator -->
		<circle cx="40" cy="20" r="3" fill="#2563eb"/>
	</svg>

	<!-- Stream info -->
	<div class="stream-info">
		<div class="stream-name">{data.name || `Stream ${data.id}`}</div>
		<div class="stream-details">
			{data.mass_flow_rate ? `${data.mass_flow_rate.toFixed(2)} kg/s` : ''}
		</div>
	</div>
</div>

<style>
	.stream-node {
		background: #fef3c7;
		border: 2px dashed #f59e0b;
		border-radius: 8px;
		padding: 8px;
		min-width: 120px;
		min-height: 50px;
		display: flex;
		align-items: center;
		gap: 8px;
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.stream-node.selected {
		border-color: #d97706;
		box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2), 0 4px 8px rgba(0, 0, 0, 0.15);
		background: #fde68a;
	}

	.stream-symbol {
		width: 60px;
		height: 30px;
		flex-shrink: 0;
	}

	.stream-info {
		flex: 1;
		min-width: 0;
	}

	.stream-name {
		font-size: 0.75rem;
		font-weight: 600;
		color: #92400e;
		margin-bottom: 2px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.stream-details {
		font-size: 0.625rem;
		color: #a16207;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	/* Custom stream handle styling */
	:global(.stream-handle) {
		width: 10px;
		height: 10px;
		background: #f59e0b;
		border: 2px solid white;
		border-radius: 50%;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
	}

	:global(.stream-handle:hover) {
		background: #d97706;
		transform: scale(1.2);
	}

	:global(.stream-handle.react-flow__handle-valid) {
		background: #10b981;
	}

	:global(.stream-handle.react-flow__handle-connecting) {
		background: #f59e0b;
		animation: stream-pulse 1.5s infinite;
	}

	@keyframes stream-pulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.3);
		}
	}
</style>