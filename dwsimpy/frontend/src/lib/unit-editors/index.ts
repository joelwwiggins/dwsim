export { default as HeaterEditor } from './HeaterEditor.svelte';
export { default as PumpEditor } from './PumpEditor.svelte';
export { default as ValveEditor } from './ValveEditor.svelte';

// Type definitions for unit data
export interface HeaterData {
	id: string;
	name?: string;
	pressure_drop?: number;
	efficiency?: number;
	heat_duty?: number;
	outlet_temperature?: number;
	calculation_mode?: 'heat_duty' | 'outlet_temperature';
	pressure_drop_unit?: string;
	heat_duty_unit?: string;
	temperature_unit?: string;
}

export interface PumpData {
	id: string;
	name?: string;
	outlet_pressure?: number;
	pressure_increase?: number;
	efficiency?: number;
	power_consumption?: number;
	calculation_mode?: 'outlet_pressure' | 'pressure_increase' | 'power_consumption';
	pressure_unit?: string;
	power_unit?: string;
}

export interface PipeData {
	id: string;
	name?: string;
	label: string;
	unitType: string;
	length: number;
	diameter: number;
	roughness: number;
	elevation_change: number;
	ambient_temperature: number;
	heat_transfer_coeff_outside: number;
	insulation_thickness: number;
	insulation_conductivity: number;
	flow_regime: 'laminar' | 'transitional' | 'turbulent';
}
export interface HeatExchangerData {
	id: string;
	name?: string;
	label: string;
	unitType: string;
	calculation_mode: 'heat_duty' | 'outlet_temperatures' | 'area';
	heat_transfer_area: number;
	overall_heat_transfer_coeff: number;
	fouling_factor: number;
	minimum_temperature_approach: number;
	hot_stream_outlet_temp?: number;
	cold_stream_outlet_temp?: number;
	heat_duty: number;
	flow_direction: 'counter_current' | 'co_current';
	equipment_type: 'shell_and_tube' | 'double_pipe' | 'plate';
	hot_side_pressure_drop: number;
	cold_side_pressure_drop: number;
}
export interface EquilibriumReactorData {
	id: string;
	name?: string;
	label: string;
	unitType: string;
	operation_mode: 'isothermal' | 'adiabatic';
	target_temperature?: number;
	pressure_drop: number;
	reactions: Array<{
		id: string;
		name?: string;
		stoichiometry: Record<string, number>;
		equilibrium_constant: number;
		reference_temperature: number;
	}>;
}

export interface ConversionReactorData {
	id: string;
	name?: string;
	label: string;
	unitType: string;
	operation_mode: 'isothermal' | 'adiabatic' | 'heat_duty';
	target_temperature?: number;
	heat_duty?: number;
	pressure_drop: number;
	reactions: Array<{
		id: string;
		name?: string;
		stoichiometry: Record<string, number>;
		conversion: number;
	}>;
}

export interface DistillationColumnData {
	id: string;
	name?: string;
	label: string;
	unitType: string;
	number_of_stages: number;
	feed_stage: number;
	reflux_ratio?: number;
	distillate_rate?: number;
	bottoms_rate?: number;
	condenser_type: 'total' | 'partial';
	reboiler_type: 'kettle' | 'thermosiphon';
}

export interface ValveData {
	id: string;
	name?: string;
	outlet_pressure?: number;
	pressure_drop?: number;
	valve_opening?: number;
	characteristic_curve?: 'linear' | 'equal_percentage' | 'quick_opening';
	valve_type?: 'gate' | 'globe' | 'ball' | 'check' | 'control';
	calculation_mode?: 'outlet_pressure' | 'pressure_drop' | 'valve_opening';
	pressure_unit?: string;
}

// Union type for all unit data
export type UnitData = HeaterData | PumpData | ValveData | DistillationColumnData | ConversionReactorData | EquilibriumReactorData | HeatExchangerData | PipeData;export { default as DistillationColumnEditor } from './DistillationColumnEditor.svelte';
export { default as ConversionReactorEditor } from './ConversionReactorEditor.svelte';
export { default as EquilibriumReactorEditor } from './EquilibriumReactorEditor.svelte';
export { default as HeatExchangerEditor } from './HeatExchangerEditor.svelte';
export { default as PipeEditor } from './PipeEditor.svelte';
