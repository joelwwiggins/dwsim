<script lang="ts">
	import { onMount } from 'svelte';
	import { SvelteFlow, Controls, Background, MiniMap } from '@xyflow/svelte';
	import UnitPalette from '../lib/UnitPalette.svelte';
	import PropertyPanel from '../lib/PropertyPanel.svelte';
	import StreamDialog from '../lib/StreamDialog.svelte';
	import ResultsPanel from '../lib/ResultsPanel.svelte';
	import { HeaterEditor, PumpEditor, ValveEditor, HeatExchangerEditor, PipeEditor, EquilibriumReactorEditor, ConversionReactorEditor, DistillationColumnEditor, type HeaterData, type PumpData, type ValveData, type DistillationColumnData, type ConversionReactorData, type EquilibriumReactorData, type HeatExchangerData } from '../lib/unit-editors';
	import type { Node, Edge } from '@xyflow/svelte';

	// Backend API configuration
	let API_BASE = $state('http://localhost:8000/api');

	// Set API base on mount (client-side only)
	onMount(() => {
		API_BASE = `http://${window.location.hostname}:8000/api`;
	});

	interface UnitData extends Record<string, unknown> {
		label: string;
		unitType: string;
		icon: string;
		properties: Record<string, any>;
	}

	interface StreamData extends Record<string, unknown> {
		id: string;
		name?: string;
		temperature?: number;
		pressure?: number;
		mass_flow_rate?: number;
		composition?: Record<string, number>;
	}

	let nodes: Node<UnitData | StreamData>[] = $state([]);
	let edges: Edge[] = $state([]);
	let selectedNodeId: string | null = $state(null);
	let showStreamDialog: boolean = $state(false);
	let selectedStream: Node<StreamData> | null = $state(null);
	let simulationResults: any = $state(null);
	let showResultsPanel: boolean = $state(false);

	// Unit editor states
	let showHeaterEditor: boolean = $state(false);
	let showPumpEditor: boolean = $state(false);
	let showValveEditor: boolean = $state(false);
	let showDistillationColumnEditor: boolean = $state(false);
	let showConversionReactorEditor: boolean = $state(false);
	let showEquilibriumReactorEditor: boolean = $state(false);
	let showHeatExchangerEditor: boolean = $state(false);
	let showPipeEditor: boolean = $state(false);
	let selectedUnitData: HeaterData | PumpData | ValveData | DistillationColumnData | ConversionReactorData | EquilibriumReactorData | HeatExchangerData | null = $state(null);

	// Active tab state
	let activeTab = $state('Flowsheet');

	// Unit operation types available
	const unitTypes = [
		{ id: 'mixer', name: 'Mixer', icon: '🔄' },
		{ id: 'heater', name: 'Heater', icon: '🔥' },
		{ id: 'cooler', name: 'Cooler', icon: '❄️' },
		{ id: 'valve', name: 'Valve', icon: '⚙️' },
		{ id: 'pump', name: 'Pump', icon: '💧' },
		{ id: 'splitter', name: 'Splitter', icon: '↗️' },
		{ id: 'tank', name: 'Tank', icon: '🛢️' },
		{ id: 'compressor', name: 'Compressor', icon: '🗜️' },
		{ id: 'expander', name: 'Expander', icon: '📈' },
		{ id: 'pipe', name: 'Pipe', icon: '📏' },
		{ id: 'heat_exchanger', name: 'Heat Exchanger', icon: '🔄' },
		{ id: 'pipe', name: 'Pipe', icon: '📏' },
		{ id: 'heat_exchanger', name: 'Heat Exchanger', icon: '🔄' },
		{ id: 'equilibrium_reactor', name: 'Equilibrium Reactor', icon: '⚗️' },
		{ id: 'conversion_reactor', name: 'Conversion Reactor', icon: '⚗️' },
		{ id: 'distillation_column', name: 'Distillation Column', icon: '🏭' },
		{ id: 'pipe', name: 'Pipe', icon: '📏' },
		{ id: 'vessel', name: 'Vessel', icon: '🏭' },
		{ id: 'component_separator', name: 'Component Separator', icon: '⚗️' },
		{ id: 'filter', name: 'Filter', icon: '🔍' },
		{ id: 'orifice_plate', name: 'Orifice Plate', icon: '⭕' },
		{ id: 'relief_valve', name: 'Relief Valve', icon: '🚨' }
	];

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
		selectedUnitData = clickedNode.data as HeaterData | PumpData | ValveData;

		switch (unitType) {
			case 'heater':
				showHeaterEditor = true;
				break;
			case 'pump':
				showPumpEditor = true;
				break;
			case 'valve':
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
			type: 'default'
		};
		edges = [...edges, newEdge];

		// Create a stream node for this connection
		createStreamForEdge(newEdge);
	}

	function createStreamForEdge(edge: Edge) {
		const streamId = `stream_${edge.source}_${edge.target}`;
		const existingStream = nodes.find(node => node.id === streamId);

		if (!existingStream) {
			const sourceNode = nodes.find(node => node.id === edge.source);
			const targetNode = nodes.find(node => node.id === edge.target);

			if (sourceNode && targetNode) {
				// Position stream node between source and target
				const streamPosition = {
					x: (sourceNode.position.x + targetNode.position.x) / 2,
					y: (sourceNode.position.y + targetNode.position.y) / 2
				};

				const streamNode: Node<StreamData> = {
					id: streamId,
					type: 'default',
					position: streamPosition,
					class: 'stream-node',
					data: {
						label: `🌊 ${streamId}`,
						id: streamId,
						name: `Stream ${streamId}`,
						temperature: 298.15,
						pressure: 101325,
						mass_flow_rate: 1.0,
						composition: { water: 1.0 }
					}
				};

				nodes = [...nodes, streamNode];
			}
		}
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
			nodes = [...nodes]; // Trigger reactivity
		}
	}

	function saveHeaterData(unitData: HeaterData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes = [...nodes]; // Trigger reactivity
			}
		}
		showHeaterEditor = false;
	}

	function savePumpData(unitData: PumpData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes = [...nodes]; // Trigger reactivity
			}
		}
		showPumpEditor = false;
	}

	function saveValveData(unitData: ValveData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes = [...nodes]; // Trigger reactivity
			}
		}
		showValveEditor = false;
	}
	function saveDistillationColumnData(unitData: DistillationColumnData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
				nodes = [...nodes]; // Trigger reactivity
			}
		}
		showDistillationColumnEditor = false;
	function saveConversionReactorData(unitData: ConversionReactorData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
				node.data = { ...node.data, ...unitData };
	function saveEquilibriumReactorData(unitData: EquilibriumReactorData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
			node.data = { ...node.data, ...unitData };
	function saveHeatExchangerData(unitData: HeatExchangerData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
			node.data = { ...node.data, ...unitData };
	function savePipeData(unitData: PipeData) {
		if (selectedNodeId) {
			const node = nodes.find(n => n.id === selectedNodeId);
			if (node) {
			node.data = { ...node.data, ...unitData };
			nodes = [...nodes]; // Trigger reactivity
			}
		}
		showPipeEditor = false;
	}
			nodes = [...nodes]; // Trigger reactivity
			}
		}
		showHeatExchangerEditor = false;
	}
			nodes = [...nodes]; // Trigger reactivity
			}
		}
		showEquilibriumReactorEditor = false;
	}
				nodes = [...nodes]; // Trigger reactivity
			}
		}
		showConversionReactorEditor = false;
	}
	}

	// Toolbar actions
	function newFlowsheet() {
		nodes = [];
		edges = [];
		selectedNodeId = null;
	}

	function saveFlowsheet() {
		const unitNodes = nodes.filter(node => node.data.unitType);
		const streamNodes = nodes.filter(node => !node.data.unitType);

		const flowsheetData = {
			nodes: unitNodes.map(node => ({
				id: node.id,
				type: node.type,
				position: node.position,
				data: node.data
			})),
			edges: edges.map(edge => ({
				id: edge.id,
				source: edge.source,
				target: edge.target,
				sourceHandle: edge.sourceHandle,
				targetHandle: edge.targetHandle
			})),
			streams: streamNodes.map(node => node.data)
		};

		// Prompt for filename
		const filename = prompt('Enter flowsheet name:', 'my_flowsheet');
		if (!filename) return;

		// Send to backend
		fetch(`${API_BASE}/flowsheet/save?filename=${encodeURIComponent(filename)}`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(flowsheetData)
		})
		.then(response => response.json())
		.then(result => {
			if (result.success) {
				alert(`Flowsheet saved as ${filename}`);
			} else {
				alert(`Failed to save flowsheet: ${result.message}`);
			}
		})
		.catch(error => {
			console.error('Save error:', error);
			alert('Failed to save flowsheet');
		});
	}

	async function loadFlowsheet() {
		try {
			// Get list of saved flowsheets
			const listResponse = await fetch(`${API_BASE}/flowsheet/list`);
			const listData = await listResponse.json();

			if (listData.flowsheets.length === 0) {
				alert('No saved flowsheets found');
				return;
			}

			// Prompt user to select a flowsheet
			const filename = prompt(`Available flowsheets:\n${listData.flowsheets.join('\n')}\n\nEnter flowsheet name to load:`, listData.flowsheets[0]);
			if (!filename) return;

			// Load the flowsheet
			const loadResponse = await fetch(`${API_BASE}/flowsheet/load/${encodeURIComponent(filename)}`);
			if (!loadResponse.ok) {
				throw new Error(`Failed to load flowsheet: ${loadResponse.statusText}`);
			}

			const flowsheetData = await loadResponse.json();

			// Clear current flowsheet
			nodes = [];
			edges = [];
			selectedNodeId = null;

			// Load nodes
			const loadedNodes: Node<UnitData | StreamData>[] = [];

			// Load unit nodes
			if (flowsheetData.nodes) {
				for (const nodeData of flowsheetData.nodes) {
					loadedNodes.push({
						id: nodeData.id,
						type: nodeData.type || 'default',
						position: nodeData.position,
						data: nodeData.data
					});
				}
			}

			// Load stream nodes
			if (flowsheetData.streams) {
				for (const streamData of flowsheetData.streams) {
					loadedNodes.push({
						id: streamData.id,
						type: 'default',
						position: { x: 100, y: 100 }, // Default position, could be improved
						data: streamData
					});
				}
			}

			nodes = loadedNodes;
			edges = flowsheetData.edges || [];

			alert(`Flowsheet "${filename}" loaded successfully!`);

		} catch (error) {
			console.error('Load error:', error);
			alert(`Failed to load flowsheet: ${error instanceof Error ? error.message : String(error)}`);
		}
	}

	async function runSimulation() {
		try {
			const unitNodes = nodes.filter(node => node.data.unitType);
			const streamNodes = nodes.filter(node => !node.data.unitType);

			const flowsheetData = {
				nodes: unitNodes.map(node => ({
					id: node.id,
					type: node.type,
					position: node.position,
					data: node.data
				})),
				edges: edges.map(edge => ({
					id: edge.id,
					source: edge.source,
					target: edge.target,
					sourceHandle: edge.sourceHandle,
					targetHandle: edge.targetHandle
				})),
				streams: streamNodes.map(node => node.data)
			};

			// Load flowsheet
			const loadResponse = await fetch(`${API_BASE}/flowsheet/load`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(flowsheetData)
			});

			if (!loadResponse.ok) {
				throw new Error('Failed to load flowsheet');
			}

			// Run simulation
			const runResponse = await fetch(`${API_BASE}/simulation/run`, {
				method: 'POST'
			});

			const result = await runResponse.json();
			console.log('Simulation result:', result);

			// Store results and show panel
			simulationResults = result.results || result;
			showResultsPanel = true;

			if (result.success) {
				alert('Simulation completed successfully!');
			} else {
				alert(`Simulation failed: ${result.message}`);
			}
		} catch (error) {
			console.error('Simulation error:', error);
			alert('Failed to run simulation');
		}
	}

	// Get selected node data
	let selectedNode = $derived(selectedNodeId ? nodes.find(node => node.id === selectedNodeId && node.data.unitType) as Node<UnitData> | null : null);

	function ondragover(event: DragEvent) {
		event.preventDefault();
	}

	function ondrop(event: DragEvent) {
		event.preventDefault();

		const unitType = event.dataTransfer?.getData('application/unit-type');
		if (!unitType) return;

		const rect = (event.target as HTMLElement).getBoundingClientRect();
		const position = {
			x: event.clientX - rect.left,
			y: event.clientY - rect.top
		};

		const unitTypeData = unitTypes.find(type => type.id === unitType);
		if (!unitTypeData) return;

		const newNode: Node<UnitData> = {
			id: `${unitType}_${Date.now()}`,
			type: 'default',
			position,
			class: 'unit-node',
			data: {
				label: `${unitTypeData.icon} ${unitTypeData.name}`,
				unitType,
				icon: unitTypeData.icon,
				properties: {}
			}
		};

		nodes = [...nodes, newNode];
	}

	function toggleResultsPanel() {
		showResultsPanel = !showResultsPanel;
	}

	function addStream() {
		const streamId = `stream_${Date.now()}`;
		const streamNode: Node<StreamData> = {
			id: streamId,
			type: 'default',
			position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
			class: 'stream-node',
			data: {
				label: `🌊 ${streamId}`,
				id: streamId,
				name: `Stream ${streamId}`,
				temperature: 298.15,
				pressure: 101325,
				mass_flow_rate: 1.0,
				composition: { water: 1.0 }
			}
		};

		nodes = [...nodes, streamNode];
	}

	// Tab switching functions
	function switchTab(tabName: string) {
		activeTab = tabName;
	}

	function openUnitEditor(unit: Node<UnitData>) {
		selectedNodeId = unit.id;
		selectedUnitData = { ...unit.data };

		switch (unit.data.unitType) {
			case 'heater':
				showHeaterEditor = true;
				break;
			case 'pump':
				showPumpEditor = true;
				break;
			case 'valve':
				showValveEditor = true;
				break;
			default:
				break;
		}
	}

	function closeUnitEditor() {
		showHeaterEditor = false;
		showPumpEditor = false;
		showValveEditor = false;
		selectedUnitData = null;
	}

	function saveUnitData(updatedData: HeaterData | PumpData | ValveData) {
		if (selectedNodeId) {
			const nodeIndex = nodes.findIndex(node => node.id === selectedNodeId);
			if (nodeIndex !== -1) {
				nodes[nodeIndex].data = { ...nodes[nodeIndex].data, ...updatedData };
				nodes = [...nodes]; // Trigger reactivity
			}
		}

		closeUnitEditor();
	}
</script>

<div class="dwsim-window">
	<!-- Title Bar -->
	<div class="title-bar">
		<span class="title">DWSIM — Process Simulation</span>
		<span class="path">[C:\Users\user\source\repos\DWSIM-Web\bin\Debug\process_simulation.dwxml]</span>
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
			<button class={activeTab === 'Material Streams' ? 'active' : ''} onclick={() => switchTab('Material Streams')}>Material Streams</button>
			<button class={activeTab === 'Spreadsheet' ? 'active' : ''} onclick={() => switchTab('Spreadsheet')}>Spreadsheet</button>
			<button class={activeTab === 'Charts' ? 'active' : ''} onclick={() => switchTab('Charts')}>Charts</button>
			<button class={activeTab === 'Settings' ? 'active' : ''} onclick={() => switchTab('Settings')}>Settings</button>
			<button class={activeTab === 'Flowsheet' ? 'active' : ''} onclick={() => switchTab('Flowsheet')}>Flowsheet</button>
		</div>
		<div class="tab-actions">
			<button title="Solve Flowsheet (F5)" onclick={runSimulation}>▶️</button>
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
		{#if activeTab === 'Flowsheet'}
			<div class="flowsheet-container">
				<UnitPalette {unitTypes} onAddStream={addStream} />

				<div class="flow-container" ondragover={ondragover} ondrop={ondrop} role="application">
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

				<PropertyPanel selectedNode={selectedNode && !['heater', 'pump', 'valve'].includes(selectedNode.data.unitType) ? selectedNode : null} />
			</div>
		{:else if activeTab === 'Material Streams'}
			<div class="tab-content">
				<h2>Material Streams</h2>
				<p>Material streams management interface would go here.</p>
				<div class="streams-list">
					{#each nodes.filter(node => !node.data.unitType) as stream}
						<div class="stream-item" onclick={() => openStreamDialog(stream)} role="button" tabindex="0" onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openStreamDialog(stream); } }} aria-label="Edit stream {stream.data.name || stream.id}">
							<strong>{stream.data.name || stream.id}</strong>
							<span>T: {stream.data.temperature?.toFixed(1)} K</span>
							<span>P: {stream.data.pressure?.toFixed(0)} Pa</span>
							<span>Flow: {stream.data.mass_flow_rate?.toFixed(2)} kg/s</span>
						</div>
					{/each}
				</div>
			</div>
		{:else if activeTab === 'Spreadsheet'}
			<div class="tab-content">
				<h2>Spreadsheet</h2>
				<p>Spreadsheet interface for calculations would go here.</p>
			</div>
		{:else if activeTab === 'Charts'}
			<div class="tab-content">
				<h2>Charts</h2>
				<p>Charts and visualization interface would go here.</p>
			</div>
		{:else if activeTab === 'Settings'}
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

<ResultsPanel
	results={simulationResults}
	isVisible={showResultsPanel}
/>

<HeaterEditor
	unit={selectedUnitData as HeaterData}
	isOpen={showHeaterEditor}
	onClose={() => showHeaterEditor = false}
	onSave={saveHeaterData}
/>

<PumpEditor
	unit={selectedUnitData as PumpData}
	isOpen={showPumpEditor}
	onClose={() => showPumpEditor = false}
	onSave={savePumpData}
/>

</ValveEditor>

<HeatExchangerEditor
	unit={selectedUnitData as HeatExchangerData}
	isOpen={showHeatExchangerEditor}
	onClose={() => showHeatExchangerEditor = false}
	onSave={saveHeatExchangerData}
/>

<EquilibriumReactorEditor
	unit={selectedUnitData as EquilibriumReactorData}
	isOpen={showEquilibriumReactorEditor}
	onClose={() => showEquilibriumReactorEditor = false}
	onSave={saveEquilibriumReactorData}
/>

<ConversionReactorEditor
	unit={selectedUnitData as ConversionReactorData}
	isOpen={showConversionReactorEditor}
	onClose={() => showConversionReactorEditor = false}
	onSave={saveConversionReactorData}
/>

<DistillationColumnEditor
	unit={selectedUnitData as DistillationColumnData}
	isOpen={showDistillationColumnEditor}
	onClose={() => showDistillationColumnEditor = false}
	onSave={saveDistillationColumnData}
/>

<style>
	unit={selectedUnitData as ValveData}
	isOpen={showValveEditor}
	onClose={() => showValveEditor = false}
	onSave={saveValveData}
/>

<style>
	.dwsim-window {
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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