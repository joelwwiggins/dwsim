<script lang="ts">
	import type { NodeProps } from 'svelte-flow';

	interface UnitData {
		label: string;
		unitType: string;
		icon: string;
		properties: Record<string, any>;
	}

	type Props = NodeProps<UnitData>;

	let { data, selected }: Props = $props();
</script>

<div class="unit-node" class:selected>
	<div class="unit-icon">{data.icon}</div>
	<div class="unit-label">{data.label}</div>
</div>

<style>
	.unit-node {
		background: #f8fafc;
		border: 2px solid #2563eb;
		border-radius: 8px;
		padding: 12px;
		min-width: 120px;
		min-height: 80px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		cursor: pointer;
		transition: all 0.2s;
	}

	.unit-node.selected {
		border-color: #1d4ed8;
		box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
	}

	.unit-icon {
		font-size: 2rem;
		margin-bottom: 8px;
	}

	.unit-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #1f2937;
	}
</style>