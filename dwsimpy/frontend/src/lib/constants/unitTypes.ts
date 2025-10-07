// Central source of truth for available unit operation types in the UI.
// Deduplicated and extensible.

export interface UnitTypeMeta {
    id: string;
    name: string;
    icon: string;
    category?: string;
    description?: string;
}

export const unitTypes: UnitTypeMeta[] = [
    { id: 'mixer', name: 'Mixer', icon: '🔄', category: 'Mixing' },
    { id: 'heater', name: 'Heater', icon: '🔥', category: 'Thermal' },
    { id: 'cooler', name: 'Cooler', icon: '❄️', category: 'Thermal' },
    { id: 'valve', name: 'Valve', icon: '⚙️', category: 'Pressure' },
    { id: 'pump', name: 'Pump', icon: '💧', category: 'Mechanical' },
    { id: 'splitter', name: 'Splitter', icon: '↗️', category: 'Mixing' },
    { id: 'tank', name: 'Tank', icon: '🛢️', category: 'Storage' },
    { id: 'compressor', name: 'Compressor', icon: '🗜️', category: 'Mechanical' },
    { id: 'expander', name: 'Expander', icon: '📈', category: 'Mechanical' },
    { id: 'pipe', name: 'Pipe', icon: '📏', category: 'Transport' },
    { id: 'heat_exchanger', name: 'Heat Exchanger', icon: '🔄', category: 'Thermal' },
    { id: 'equilibrium_reactor', name: 'Equilibrium Reactor', icon: '⚗️', category: 'Reaction' },
    { id: 'conversion_reactor', name: 'Conversion Reactor', icon: '⚗️', category: 'Reaction' },
    { id: 'distillation_column', name: 'Distillation Column', icon: '🏭', category: 'Separation' },
    { id: 'vessel', name: 'Vessel', icon: '🏭', category: 'Storage' },
    { id: 'component_separator', name: 'Component Separator', icon: '⚗️', category: 'Separation' },
    { id: 'filter', name: 'Filter', icon: '🔍', category: 'Separation' },
    { id: 'orifice_plate', name: 'Orifice Plate', icon: '⭕', category: 'Measurement' },
    { id: 'relief_valve', name: 'Relief Valve', icon: '🚨', category: 'Safety' }
];

export function findUnitType(id: string) {
    return unitTypes.find(u => u.id === id);
}
