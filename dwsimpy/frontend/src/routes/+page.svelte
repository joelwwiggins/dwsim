<script lang="ts">
	import { onMount } from 'svelte';
	import { SvelteFlow, Controls, Background, MiniMap } from '@xyflow/svelte';
	import UnitPalette from '../lib/UnitPalette.svelte';
	import PropertyPanel from '../lib/PropertyPanel.svelte';
	import Toolbar from '../lib/Toolbar.svelte';
	import StreamDialog from '../lib/StreamDialog.svelte';
	import ResultsPanel from '../lib/ResultsPanel.svelte';
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
		{ id: 'heat_exchanger', name: 'Heat Exchanger', icon: '🔄' },
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
					className: 'stream-node',
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
			alert(`Failed to load flowsheet: ${error.message}`);
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
			className: 'unit-node',
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
			className: 'stream-node',
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
</script>

<div class="app-container">
	<Toolbar
		onNew={newFlowsheet}
		onSave={saveFlowsheet}
		onLoad={loadFlowsheet}
		onRun={runSimulation}
		onToggleResults={toggleResultsPanel}
		showResults={showResultsPanel}
	/>

	<div class="main-content">
		<UnitPalette {unitTypes} onAddStream={addStream} />

		<div class="flow-container" ondragover={ondragover} ondrop={ondrop} role="application">
			<SvelteFlow
				{nodes}
				{edges}
			>
				<Controls />
				<Background />
				<MiniMap />
			</SvelteFlow>
		</div>

		<PropertyPanel {selectedNode} />
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
</div>

<style>
	.app-container {
		height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.main-content {
		flex: 1;
		display: flex;
	}

	.flow-container {
		flex: 1;
		position: relative;
	}

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