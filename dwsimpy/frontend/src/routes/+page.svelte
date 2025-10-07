<script lang="ts">
	import type { Edge, Node } from "@xyflow/svelte";
	import { Background, Controls, MiniMap, SvelteFlow } from "@xyflow/svelte";
	import { onMount } from "svelte";
	import PropertyPanel from "../lib/PropertyPanel.svelte";
	import ResultsPanel from "../lib/ResultsPanel.svelte";
	import StreamDialog from "../lib/StreamDialog.svelte";
	import UnitPalette from "../lib/UnitPalette.svelte";
	import { startConnectionPolling } from "../lib/api/client";
	import { unitTypes } from "../lib/constants/unitTypes";
	import {
		addStreamNode,
		edges,
		nodes,
		runSimulation,
		simulationResults,
	} from "../lib/stores/flowsheet";
	import {
		ConversionReactorEditor,
		DistillationColumnEditor,
		EquilibriumReactorEditor,
		HeaterEditor,
		HeatExchangerEditor,
		PumpEditor,
		ValveEditor,
		type ConversionReactorData,
		type DistillationColumnData,
		type EquilibriumReactorData,
		type HeaterData,
		type HeatExchangerData,
		type PumpData,
		type ValveData,
	} from "../lib/unit-editors";

	// Local UI state (editors, selection, tabs)
	let selectedNodeId: string | null = $state(null);
	let showStreamDialog: boolean = $state(false);
	let selectedStream: any = $state(null);
	let showResultsPanel: boolean = $state(false);

	let showHeaterEditor = $state(false);
	let showPumpEditor = $state(false);
	let showValveEditor = $state(false);
	let showDistillationColumnEditor = $state(false);
	let showConversionReactorEditor = $state(false);
	let showEquilibriumReactorEditor = $state(false);
	let showHeatExchangerEditor = $state(false);
	let showPipeEditor = $state(false);
	let selectedUnitData:
		| HeaterData
		| PumpData
		| ValveData
		| DistillationColumnData
		| ConversionReactorData
		| EquilibriumReactorData
		| HeatExchangerData
		| null = $state(null);

	let activeTab = $state("Flowsheet");

	onMount(() => {
		startConnectionPolling();
	});

	function onNodeClick(event: any) {
		const clickedNode = event.detail.node;
		selectedNodeId = clickedNode.id;

		// If it's a stream node, open the stream dialog
		if (!clickedNode.data.unitType) {
			openStreamDialog(clickedNode);
			return;
		}

		// If it's a unit operation, open the appropriate editor
		const unitType = clickedNode.data.unitType;
		selectedUnitData = clickedNode.data as
			| HeaterData
			| PumpData
			| ValveData;

		switch (unitType) {
			case "heater":
				showHeaterEditor = true;
				break;
			case "pump":
				showPumpEditor = true;
				break;
			case "valve":
				showValveEditor = true;
				break;
			default:
				// For other unit types, keep the old property panel behavior
				break;
		}
	}

	function onPaneClick() {
		selectedNodeId = null;
	}

	function onConnect(event: any) {
		const newEdge = {
			...event.detail.edge,
			id: `edge_${event.detail.edge.source}_${event.detail.edge.target}`,
			type: "default",
		};
		// update edges store
		edges.update((list) => [...list, newEdge]);
		createStreamForEdge(newEdge);
	}

	function createStreamForEdge(edge: Edge) {
		const streamId = `stream_${edge.source}_${edge.target}`;
		let currentNodes: any[];
		nodes.subscribe((v) => (currentNodes = v))();
		if (currentNodes.find((n) => n.id === streamId)) return;
		const sourceNode = currentNodes.find((n) => n.id === edge.source);
		const targetNode = currentNodes.find((n) => n.id === edge.target);
		if (!(sourceNode && targetNode)) return;
		const streamPosition = {
			x: (sourceNode.position.x + targetNode.position.x) / 2,
			y: (sourceNode.position.y + targetNode.position.y) / 2,
		};
		nodes.update((list) => [
			...list,
			{
				id: streamId,
				type: "default",
				position: streamPosition,
				class: "stream-node",
				data: {
					label: `🌊 ${streamId}`,
					id: streamId,
					name: `Stream ${streamId}`,
					temperature: 298.15,
					pressure: 101325,
					mass_flow_rate: 1.0,
					composition: { water: 1.0 },
				},
			},
		]);
	}

	function openStreamDialog(stream: Node<StreamData>) {
		selectedStream = stream;
		showStreamDialog = true;
	}

	function closeStreamDialog() {
		showStreamDialog = false;
		selectedStream = null;
	}

	function saveStreamData(streamData: StreamData) {
		if (selectedStream) {
			selectedStream.data = { ...selectedStream.data, ...streamData };
			nodes.update((n) => n); // Trigger reactivity
		}
	}

	function saveHeaterData(unitData: HeaterData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n); // Trigger reactivity
			}
		}
		showHeaterEditor = false;
	}

	function savePumpData(unitData: PumpData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n); // Trigger reactivity
			}
		}
		showPumpEditor = false;
	}

	function saveValveData(unitData: ValveData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n);
			}
		}
		showValveEditor = false;
	}

	function saveDistillationColumnData(unitData: DistillationColumnData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n);
			}
		}
		showDistillationColumnEditor = false;
	}

	function saveConversionReactorData(unitData: ConversionReactorData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n);
			}
		}
		showConversionReactorEditor = false;
	}

	function saveEquilibriumReactorData(unitData: EquilibriumReactorData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n);
			}
		}
		showEquilibriumReactorEditor = false;
	}

	function saveHeatExchangerData(unitData: HeatExchangerData) {
		if (selectedNodeId) {
			const node = nodes.find((n) => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes.update((n) => n);
			}
		}
		showHeatExchangerEditor = false;
	}

	// Derived selected node
	let selectedNode = $derived(
		nodes.find((n) => n.id === selectedNodeId) || null,
	);

	// Add a simple material stream
	function addStream() {
		addStreamNode();
	}

	function switchTab(tab: string) {
		activeTab = tab;
	}

	function ondragover(e: DragEvent) {
		e.preventDefault();
	}
	function ondrop(_e: DragEvent) {
		/* Placeholder for future drag/drop logic */
	}

	async function runSimAndShow() {
		await runSimulation();
		let res: any;
		simulationResults.subscribe((v) => (res = v))();
		showResultsPanel = true;
	}
</script>

<div class="dwsim-window">
	<!-- Title Bar -->
	<div class="title-bar">
		<span class="title">DWSIM — Process Simulation</span>
		<span class="path"
			>[C:\Users\user\source\repos\DWSIM-Web\bin\Debug\process_simulation.dwxml]</span
		>
		<div class="window-controls">
			<button title="Minimize">−</button>
			<button title="Maximize">□</button>
			<button title="Close">×</button>
		</div>
	</div>

	<!-- Menu Bar -->
	<div class="menu-bar">
		<ul>
			<li>File</li>
			<li>Edit</li>
			<li>Insert</li>
			<li>Tools</li>
			<li>Dynamics</li>
			<li>Utilities</li>
			<li>Optimization</li>
			<li>Results</li>
			<li>Plugins</li>
			<li>Spreadsheet</li>
			<li>Windows</li>
			<li>View</li>
			<li>Help</li>
		</ul>
	</div>

	<!-- Toolbar -->
	<div class="toolbar">
		<div class="toolbar-section">
			<button title="Material Stream" onclick={addStream}>📊</button>
			<button title="Energy Stream">⚡</button>
			<button title="Pressure Changers">🔧</button>
			<button title="Separators/Tanks">🛢️</button>
			<button title="Mixers/Splitters">🔀</button>
			<button title="Exchangers">🔄</button>
			<button title="Reactors">⚗️</button>
			<button title="Columns">📈</button>
			<button title="Solids">⛏️</button>
			<button title="CAPE-OPEN User Models">🔌</button>
			<button title="Logical Ops">🔍</button>
			<button title="Indicators">📊</button>
			<button title="Controllers">🎛️</button>
			<button title="Other">❓</button>
		</div>
	</div>

	<!-- Tab Bar -->
	<div class="tab-bar">
		<div class="tabs">
			<button
				class={activeTab === "Material Streams" ? "active" : ""}
				onclick={() => switchTab("Material Streams")}
				>Material Streams</button
			>
			<button
				class={activeTab === "Spreadsheet" ? "active" : ""}
				onclick={() => switchTab("Spreadsheet")}>Spreadsheet</button
			>
			<button
				class={activeTab === "Charts" ? "active" : ""}
				onclick={() => switchTab("Charts")}>Charts</button
			>
			<button
				class={activeTab === "Settings" ? "active" : ""}
				onclick={() => switchTab("Settings")}>Settings</button
			>
			<button
				class={activeTab === "Flowsheet" ? "active" : ""}
				onclick={() => switchTab("Flowsheet")}>Flowsheet</button
			>
		</div>
		<div class="tab-actions">
			<button title="Solve Flowsheet (F5)" onclick={runSimAndShow}
				>▶️</button
			>
			<button title="Abort Solver (Pause)">⏸️</button>
			<div class="search-box">
				<input type="text" placeholder="Search..." />
			</div>
		</div>
	</div>

	<!-- Control Panel Mode -->
	<div class="control-panel">
		<span>Control Panel Mode</span>
	</div>

	<!-- Main Content Area -->
	<div class="main-content">
		{#if activeTab === "Flowsheet"}
			<div class="flowsheet-container">
				<UnitPalette {unitTypes} onAddStream={addStream} />

				<div
					class="flow-container"
					{ondragover}
					{ondrop}
					role="application"
				>
					<SvelteFlow
						{nodes}
						{edges}
						on:nodeClick={onNodeClick}
						on:paneClick={onPaneClick}
						on:connect={onConnect}
					>
						<Controls />
						<Background />
						<MiniMap />
					</SvelteFlow>
				</div>

				<PropertyPanel
					selectedNode={selectedNode &&
					!["heater", "pump", "valve"].includes(
						selectedNode.data.unitType,
					)
						? selectedNode
						: null}
				/>
			</div>
		{:else if activeTab === "Material Streams"}
			<div class="tab-content">
				<h2>Material Streams</h2>
				<p>Material streams management interface would go here.</p>
				<div class="streams-list">
					{#each nodes.filter((node) => !node.data.unitType) as stream (stream.id)}
						<div
							class="stream-item"
							onclick={() => openStreamDialog(stream)}
							role="button"
							tabindex="0"
							onkeydown={(e) => {
								if (e.key === "Enter" || e.key === " ") {
									e.preventDefault();
									openStreamDialog(stream);
								}
							}}
							aria-label="Edit stream {stream.data.name ||
								stream.id}"
						>
							<strong>{stream.data.name || stream.id}</strong>
							<span
								>T: {stream.data.temperature?.toFixed(1)} K</span
							>
							<span>P: {stream.data.pressure?.toFixed(0)} Pa</span
							>
							<span
								>Flow: {stream.data.mass_flow_rate?.toFixed(2)} kg/s</span
							>
						</div>
					{/each}
				</div>
			</div>
		{:else if activeTab === "Spreadsheet"}
			<div class="tab-content">
				<h2>Spreadsheet</h2>
				<p>Spreadsheet interface for calculations would go here.</p>
			</div>
		{:else if activeTab === "Charts"}
			<div class="tab-content">
				<h2>Charts</h2>
				<p>Charts and visualization interface would go here.</p>
			</div>
		{:else if activeTab === "Settings"}
			<div class="tab-content">
				<h2>Settings</h2>
				<p>Application settings interface would go here.</p>
			</div>
		{/if}
	</div>

	<!-- Status Bar -->
	<div class="status-bar">
		<span>Ready</span>
		<span class="status-right">
			<span>{new Date().toLocaleTimeString()}</span>
			<span>{new Date().toLocaleDateString()}</span>
		</span>
	</div>
</div>

<StreamDialog
	stream={selectedStream}
	isOpen={showStreamDialog}
	onClose={closeStreamDialog}
	onSave={saveStreamData}
/>

<ResultsPanel results={simulationResults} isVisible={showResultsPanel} />

<HeaterEditor
	unit={selectedUnitData as HeaterData}
	isOpen={showHeaterEditor}
	onClose={() => (showHeaterEditor = false)}
	onSave={saveHeaterData}
/>

<PumpEditor
	unit={selectedUnitData as PumpData}
	isOpen={showPumpEditor}
	onClose={() => (showPumpEditor = false)}
	onSave={savePumpData}
/>

<ValveEditor
	unit={selectedUnitData as ValveData}
	isOpen={showValveEditor}
	onClose={() => (showValveEditor = false)}
	onSave={saveValveData}
/>

<HeatExchangerEditor
	unit={selectedUnitData as HeatExchangerData}
	isOpen={showHeatExchangerEditor}
	onClose={() => (showHeatExchangerEditor = false)}
	onSave={saveHeatExchangerData}
/>

<EquilibriumReactorEditor
	unit={selectedUnitData as EquilibriumReactorData}
	isOpen={showEquilibriumReactorEditor}
	onClose={() => (showEquilibriumReactorEditor = false)}
	onSave={saveEquilibriumReactorData}
/>

<ConversionReactorEditor
	unit={selectedUnitData as ConversionReactorData}
	isOpen={showConversionReactorEditor}
	onClose={() => (showConversionReactorEditor = false)}
	onSave={saveConversionReactorData}
/>

<DistillationColumnEditor
	unit={selectedUnitData as DistillationColumnData}
	isOpen={showDistillationColumnEditor}
	onClose={() => (showDistillationColumnEditor = false)}
	onSave={saveDistillationColumnData}
/>

<style>
	.dwsim-window {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		height: 100vh;
		display: flex;
		flex-direction: column;
		background-color: #f0f0f0;
	}

	.title-bar {
		height: 30px;
		background: linear-gradient(to right, #e0e0e0, #d0d0d0);
		display: flex;
		align-items: center;
		padding: 0 10px;
		border-bottom: 1px solid #ccc;
		font-size: 12px;
	}

	.title {
		font-weight: bold;
	}

	.path {
		margin-left: auto;
		color: #666;
	}

	.window-controls {
		margin-left: auto;
	}

	.window-controls button {
		width: 30px;
		height: 20px;
		border: none;
		background: none;
		font-size: 16px;
		cursor: pointer;
	}

	.menu-bar {
		height: 25px;
		background: #c0c0c0;
		display: flex;
		align-items: center;
		padding: 0 5px;
	}

	.menu-bar ul {
		list-style: none;
		display: flex;
		margin: 0;
		padding: 0;
		gap: 10px;
	}

	.menu-bar li {
		padding: 4px 8px;
		cursor: pointer;
	}

	.menu-bar li:hover {
		background: #a0a0a0;
	}

	.toolbar {
		height: 40px;
		background: #e8e8e8;
		display: flex;
		align-items: center;
		padding: 0 10px;
		border-bottom: 1px solid #ccc;
	}

	.toolbar-section button {
		width: 30px;
		height: 30px;
		margin-right: 5px;
		border: 1px solid #ccc;
		background: white;
		cursor: pointer;
		font-size: 14px;
	}

	.toolbar-section button:hover {
		background: #f0f0f0;
	}

	.tab-bar {
		height: 35px;
		background: #f8f8f8;
		display: flex;
		align-items: center;
		padding: 0 10px;
		border-bottom: 1px solid #ccc;
	}

	.tabs {
		display: flex;
		gap: 5px;
	}

	.tabs button {
		padding: 6px 12px;
		border: 1px solid #ccc;
		background: white;
		cursor: pointer;
		font-size: 12px;
	}

	.tabs button.active {
		background: #e0e0e0;
		border-bottom: none;
	}

	.tabs button:hover {
		background: #f0f0f0;
	}

	.tab-actions {
		margin-left: auto;
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.tab-actions button {
		width: 30px;
		height: 30px;
		border: 1px solid #ccc;
		background: white;
		cursor: pointer;
		font-size: 14px;
	}

	.tab-actions button:hover {
		background: #f0f0f0;
	}

	.search-box input {
		padding: 4px 8px;
		border: 1px solid #ccc;
		border-radius: 3px;
		font-size: 12px;
	}

	.control-panel {
		height: 25px;
		background: #d8d8d8;
		display: flex;
		align-items: center;
		padding: 0 10px;
		font-size: 12px;
		border-bottom: 1px solid #ccc;
	}

	.main-content {
		flex: 1;
		display: flex;
		overflow: hidden;
	}

	.flowsheet-container {
		flex: 1;
		display: flex;
		background: #f0f0f0;
	}

	.flow-container {
		flex: 1;
		position: relative;
	}

	.tab-content {
		flex: 1;
		padding: 20px;
		background: white;
		overflow-y: auto;
	}

	.streams-list {
		margin-top: 20px;
	}

	.stream-item {
		padding: 10px;
		border: 1px solid #ddd;
		margin-bottom: 5px;
		cursor: pointer;
		background: #f9f9f9;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.stream-item:hover {
		background: #f0f0f0;
	}

	.status-bar {
		height: 20px;
		background: #e0e0e0;
		display: flex;
		align-items: center;
		padding: 0 10px;
		font-size: 12px;
		border-top: 1px solid #ccc;
	}

	.status-right {
		margin-left: auto;
		display: flex;
		gap: 20px;
	}

	/* Svelte Flow Styles */
	:global(.svelte-flow) {
		height: 100%;
	}

	:global(.svelte-flow__node) {
		border-radius: 8px;
		border: 2px solid #ddd;
		background: white;
		padding: 8px;
		min-width: 120px;
		text-align: center;
	}

	:global(.svelte-flow__node.selected) {
		border-color: #2563eb;
		box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
	}

	/* Style for unit operation nodes */
	:global(.unit-node) {
		background: #f8fafc;
		border-color: #2563eb;
		min-height: 60px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	/* Style for stream nodes */
	:global(.stream-node) {
		background: #fef3c7;
		border-color: #f59e0b;
		border-style: dashed;
		min-height: 40px;
		font-size: 0.875rem;
	}

	:global(.svelte-flow__edge.selected) {
		z-index: 10;
	}

	:global(.svelte-flow__controls) {
		bottom: 20px;
		left: 20px;
	}

	:global(.svelte-flow__minimap) {
		bottom: 20px;
		right: 20px;
	}
</style>
