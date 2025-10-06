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
export type UnitData = HeaterData | PumpData | ValveData;