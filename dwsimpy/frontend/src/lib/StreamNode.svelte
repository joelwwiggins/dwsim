<script lang="ts">
	import type { NodeProps } from '@xyflow/svelte';

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
	<div class="stream-icon">🌊</div>
	<div class="stream-name">{data.name || `Stream ${data.id}`}</div>
	<div class="stream-info">
		{data.mass_flow_rate?.toFixed(2) || '0.00'} kg/s
	</div>
</div>

<style>
	.stream-node {
		background: #fef3c7;
		border: 2px dashed #f59e0b;
		border-radius: 8px;
		padding: 8px;
		min-width: 100px;
		min-height: 60px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		cursor: pointer;
		transition: all 0.2s;
	}

	.stream-node.selected {
		border-color: #d97706;
		box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
	}

	.stream-icon {
		font-size: 1.5rem;
		margin-bottom: 4px;
	}

	.stream-name {
		font-size: 0.75rem;
		font-weight: 600;
		color: #92400e;
		margin-bottom: 2px;
	}

	.stream-info {
		font-size: 0.625rem;
		color: #a16207;
	}
</style>