import { get, writable } from 'svelte/store';
import { api } from '../api/client';
import { auditGraph, issuesToNotifications } from '../graph/audit';
import { buildSimulationPayload } from '../serialization/flowsheet';
import type { FlowsheetEdge, FlowsheetNode, NotificationItem } from '../types/flowsheet';

export const nodes = writable<FlowsheetNode[]>([]);
export const edges = writable<FlowsheetEdge[]>([]);
export const simulationResults = writable<any>(null);
export const isSimulating = writable(false);

export const notifications = writable<NotificationItem[]>([]);

function pushNotification(type: NotificationItem['type'], message: string) {
    notifications.update(list => [...list, { id: Date.now() + Math.random(), type, message, ts: Date.now() }]);
}

function runAudit() {
    const issues = auditGraph(get(nodes) as any, get(edges) as any);
    if (issues.length) {
        const notifs = issuesToNotifications(issues);
        notifications.update(list => [...list, ...notifs]);
    }
}

export function addStreamNode() {
    const current = get(nodes);
    const id = `stream_${current.length + 1}`;
    const node: FlowsheetNode = {
        id,
        type: 'default',
        position: { x: 120 + current.length * 40, y: 120 },
        class: 'stream-node',
        data: {
            label: `🌊 ${id}`,
            name: id,
            temperature: 298.15,
            pressure: 101325,
            mass_flow_rate: 1.0,
            composition: { water: 1.0 }
        } as any
    };
    nodes.set([...current, node]);
    runAudit();
}

export function addUnitNode(unitType: string, position = { x: 400, y: 200 }) {
    const current = get(nodes);
    const id = `${unitType}_${current.length + 1}`;
    const node: FlowsheetNode = {
        id,
        type: 'default',
        position,
        class: 'unit-node',
        data: {
            label: `${unitType} ${current.length + 1}`,
            unitType,
            properties: {}
        } as any
    };
    nodes.set([...current, node]);
    runAudit();
}

export function connectNodes(sourceId: string, targetId: string) {
    const currentEdges = get(edges);
    const id = `edge_${sourceId}_${targetId}`;
    if (currentEdges.find(e => e.id === id)) return;
    edges.set([...currentEdges, { id, source: sourceId, target: targetId, type: 'default' }]);
    runAudit();
}

export async function runSimulation() {
    try {
        isSimulating.set(true);
        const payload = buildSimulationPayload(get(nodes), get(edges));
        pushNotification('info', 'Loading flowsheet...');
        const loadResp = await api.loadFlowsheet(payload);
        if (!loadResp.success) throw new Error(loadResp.message || 'Failed to load flowsheet');
        runAudit();
        pushNotification('info', 'Running simulation...');
        const simResp = await api.runSimulation();
        if (!simResp.success) throw new Error(simResp.message || 'Simulation failed');
        simulationResults.set(simResp.results || {});
        pushNotification('success', 'Simulation completed');
    } catch (e: any) {
        pushNotification('error', e.message || 'Simulation error');
        simulationResults.set({ error: e.message });
    } finally {
        isSimulating.set(false);
    }
}

export function clearFlowsheet() {
    nodes.set([]);
    edges.set([]);
    simulationResults.set(null);
    pushNotification('info', 'Flowsheet cleared');
    runAudit();
}
