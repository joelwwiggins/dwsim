// Type definitions for DWSIMpy flowsheet front-end
// These types centralize structures used across stores, serialization, and API layer.

export interface BasePosition { x: number; y: number }

export interface BaseNodeData {
    label: string;
    // common optional metadata
    description?: string;
}

export interface UnitNodeData extends BaseNodeData {
    unitType: string; // e.g. 'heater', 'mixer'
    properties?: Record<string, any>;
}

export interface StreamNodeData extends BaseNodeData {
    temperature: number; // K
    pressure: number;    // Pa
    mass_flow_rate: number; // kg/s
    composition: Record<string, number>;
}

export type FlowsheetNodeData = UnitNodeData | StreamNodeData;

export interface FlowsheetNode<T = FlowsheetNodeData> {
    id: string;
    type: string; // svelte-flow node type
    position: BasePosition;
    class?: string;
    data: T;
}

export interface FlowsheetEdge {
    id: string;
    source: string;
    target: string;
    sourceHandle?: string;
    targetHandle?: string;
    type?: string;
}

export interface SerializedNode {
    id: string;
    type: string; // maps to backend unit or 'stream'
    position: BasePosition;
    data: Record<string, any>;
}

export interface SerializedStream {
    id: string;
    name?: string;
    temperature?: number;
    pressure?: number;
    mass_flow_rate?: number;
    composition?: Record<string, number>;
}

export interface SimulationPayload {
    nodes: SerializedNode[];
    edges: { id: string; source: string; target: string }[];
    streams: SerializedStream[];
}

export interface SimulationResultEnvelope {
    success: boolean;
    message: string;
    results?: Record<string, any>;
    error?: string;
}

export interface NotificationItem {
    id: number;
    type: 'info' | 'error' | 'success' | 'warning';
    message: string;
    ts: number;
}

export interface ConnectionState {
    status: 'unknown' | 'ok' | 'degraded' | 'offline';
    lastChecked?: number;
    apiBase: string;
}
