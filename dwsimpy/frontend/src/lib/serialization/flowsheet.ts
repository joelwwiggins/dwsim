import type { FlowsheetEdge, FlowsheetNode, SimulationPayload } from '../types/flowsheet';

export function buildSimulationPayload(nodes: FlowsheetNode[], edges: FlowsheetEdge[]): SimulationPayload {
    return {
        nodes: nodes.map(n => ({
            id: n.id,
            type: (n as any).data.unitType || 'stream',
            position: n.position,
            data: { ...n.data }
        })),
        edges: edges.map(e => ({ id: e.id, source: e.source, target: e.target })),
        streams: nodes
            .filter(n => !(n as any).data.unitType)
            .map(s => ({
                id: s.id,
                name: (s.data as any).name,
                temperature: (s.data as any).temperature,
                pressure: (s.data as any).pressure,
                mass_flow_rate: (s.data as any).mass_flow_rate,
                composition: (s.data as any).composition
            }))
    };
}
