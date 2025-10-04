/**
 * Warns the user that they should use $derived() when calling a hook.
 * This is not neccessarry when the hook is called inside a child of <SvelteFlowFlow />,
 * however exceptions can be made if you don't want to return a closure.
 * @param functionName - The name of the function that is being called
 * @param force - If true, the warning will be shown regardless if child of <SvelteFlowFlow />
 */
export declare function derivedWarning(functionName: string): void;
