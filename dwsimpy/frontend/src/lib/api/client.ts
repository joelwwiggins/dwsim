import { writable } from 'svelte/store';
import type { ConnectionState, SimulationPayload, SimulationResultEnvelope } from '../types/flowsheet';

function detectApiBase(): string {
    if (typeof window === 'undefined') return 'http://localhost:8000/api';
    const host = window.location.hostname || 'localhost';
    const protocol = window.location.protocol || 'http:';
    return `${protocol}//${host}:8000/api`;
}

export const apiBase = writable<string>(detectApiBase());

async function request<T>(path: string, init?: RequestInit): Promise<T> {
    let base: string = detectApiBase();
    apiBase.subscribe(v => (base = v))();
    const url = `${base}${path}`;
    const resp = await fetch(url, init);
    if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        throw new Error(`API ${resp.status} ${resp.statusText}: ${text}`);
    }
    if (resp.status === 204) return undefined as unknown as T;
    return resp.json() as Promise<T>;
}

export const api = {
    health: () => request<{ status: string; version: string }>(`/health`),
    unitOperations: () => request<Record<string, any>>(`/unit-operations`),
    loadFlowsheet: (payload: SimulationPayload) =>
        request<SimulationResultEnvelope>(`/flowsheet/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }),
    runSimulation: () =>
        request<SimulationResultEnvelope>(`/simulation/run`, { method: 'POST' })
};

// Connection status poller
export const connectionState = writable<ConnectionState>({ status: 'unknown', apiBase: detectApiBase() });

let pollTimer: any;
export function startConnectionPolling(intervalMs = 8000) {
    stopConnectionPolling();
    const tick = async () => {
        try {
            const h = await api.health();
            connectionState.set({ status: 'ok', apiBase: detectApiBase(), lastChecked: Date.now() });
        } catch (e) {
            connectionState.set({ status: 'offline', apiBase: detectApiBase(), lastChecked: Date.now() });
        }
    };
    tick();
    pollTimer = setInterval(tick, intervalMs);
}
export function stopConnectionPolling() {
    if (pollTimer) clearInterval(pollTimer);
}
