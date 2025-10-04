import { getContext } from 'svelte';
import { key } from '../store';
import { derivedWarning } from './derivedWarning.svelte';
export function useStore() {
    const storeContext = getContext(key);
    if (!storeContext) {
        throw new Error('To call useStore outside of <SvelteFlow /> you need to wrap your component in a <SvelteFlowProvider />');
    }
    if (process.env.NODE_ENV === 'development') {
        derivedWarning('useStore');
    }
    return storeContext.getStore();
}
