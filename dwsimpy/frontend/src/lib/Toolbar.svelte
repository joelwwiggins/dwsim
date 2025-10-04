<script lang="ts">
	interface Props {
		onNew: () => void;
		onSave: () => void;
		onLoad: () => void;
		onRun: () => void;
		onToggleResults: () => void;
		showResults: boolean;
	}

	let { onNew, onSave, onLoad, onRun, onToggleResults, showResults }: Props = $props();
</script>

<div class="toolbar">
	<div class="toolbar-section">
		<h1 class="app-title">🧪 DWSIMpy</h1>
	</div>

	<div class="toolbar-section">
		<button class="toolbar-button" onclick={onNew} title="New Flowsheet">
			<span class="button-icon">📄</span>
			New
		</button>

		<button class="toolbar-button" onclick={onLoad} title="Load Flowsheet">
			<span class="button-icon">📁</span>
			Load
		</button>

		<button class="toolbar-button" onclick={onSave} title="Save Flowsheet">
			<span class="button-icon">💾</span>
			Save
		</button>
	</div>

	<div class="toolbar-section">
		<button class="toolbar-button primary" onclick={onRun} title="Run Simulation">
			<span class="button-icon">▶️</span>
			Run Simulation
		</button>

		<button class="toolbar-button" onclick={onToggleResults} title={showResults ? "Hide Results" : "Show Results"}>
			<span class="button-icon">📊</span>
			{showResults ? "Hide Results" : "Show Results"}
		</button>
	</div>
</div>

<style>
	.toolbar {
		height: 60px;
		background: white;
		border-bottom: 1px solid #e5e7eb;
		display: flex;
		align-items: center;
		padding: 0 1rem;
		gap: 2rem;
		box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
	}

	.toolbar-section {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.app-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: #2563eb;
		margin: 0;
	}

	.toolbar-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		border: 1px solid #d1d5db;
		border-radius: 0.375rem;
		background: white;
		color: #374151;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.toolbar-button:hover {
		background: #f9fafb;
		border-color: #9ca3af;
	}

	.toolbar-button.primary {
		background: #2563eb;
		color: white;
		border-color: #2563eb;
	}

	.toolbar-button.primary:hover {
		background: #1d4ed8;
		border-color: #1d4ed8;
	}

	.button-icon {
		font-size: 1rem;
	}
</style>