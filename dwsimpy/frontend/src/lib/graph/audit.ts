import { getIncomers, getOutgoers, isNode } from '@xyflow/svelte';
import type { NotificationItem } from '../types/flowsheet';

export interface GraphIssue {
    node?: string;
    kind: string;
    severity: 'info' | 'warning' | 'error';
    message: string;
}

export function auditGraph(nodes: any[], edges: any[]): GraphIssue[] {
    const issues: GraphIssue[] = [];
    const flowNodes = nodes.filter(isNode);

    for (const n of flowNodes) {
        const incomers = getIncomers(n, flowNodes, edges);
        const outgoers = getOutgoers(n, flowNodes, edges);

        const ut = typeof n.data?.unitType === 'string' ? (n.data.unitType as string) : '';
        if (ut === 'Mixer' || ut.toLowerCase() === 'mixer') {
            if (incomers.length < 2) {
                issues.push({ node: n.id, kind: 'mixer_inlets', severity: 'warning', message: `Mixer ${n.id} has ${incomers.length} inlet(s); needs >= 2.` });
            }
            if (outgoers.length !== 1) {
                issues.push({ node: n.id, kind: 'mixer_outlets', severity: 'warning', message: `Mixer ${n.id} has ${outgoers.length} outlet(s); expected 1.` });
            }
        }
        if (ut === 'Heater' || ut.toLowerCase() === 'heater') {
            if (incomers.length !== 1) {
                issues.push({ node: n.id, kind: 'heater_inlets', severity: 'error', message: `Heater ${n.id} must have exactly 1 inlet (has ${incomers.length}).` });
            }
            if (outgoers.length !== 1) {
                issues.push({ node: n.id, kind: 'heater_outlets', severity: 'warning', message: `Heater ${n.id} should have exactly 1 outlet (has ${outgoers.length}).` });
            }
        }
    }

    return issues;
}

export function issuesToNotifications(issues: GraphIssue[]): NotificationItem[] {
    const now = Date.now();
    return issues.map(i => ({
        id: now + Math.random(),
        type: i.severity === 'error' ? 'error' : i.severity === 'warning' ? 'warning' : 'info',
        message: i.message,
        ts: now
    }));
}
