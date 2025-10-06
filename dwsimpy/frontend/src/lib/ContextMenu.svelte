<script lang="ts">
	import type { ComponentProps } from 'svelte';

	interface MenuItem {
		label: string;
		action?: () => void;
		separator?: boolean;
		disabled?: boolean;
		icon?: string;
		submenu?: MenuItem[];
	}

	interface Props {
		items: MenuItem[];
		x: number;
		y: number;
		isVisible: boolean;
		onClose: () => void;
	}

	let { items, x, y, isVisible, onClose }: Props = $props();

	let menuElement: HTMLDivElement;

	// Close menu when clicking outside
	function handleClickOutside(event: MouseEvent) {
		if (menuElement && !menuElement.contains(event.target as Node)) {
			onClose();
		}
	}

	// Handle menu item clicks
	function handleItemClick(item: MenuItem) {
		if (!item.disabled && item.action) {
			item.action();
			onClose();
		}
	}

	// Position the menu within viewport bounds
	$effect(() => {
		if (isVisible && menuElement) {
			const rect = menuElement.getBoundingClientRect();
			const viewportWidth = window.innerWidth;
			const viewportHeight = window.innerHeight;

			let newX = x;
			let newY = y;

			// Adjust horizontal position
			if (x + rect.width > viewportWidth) {
				newX = viewportWidth - rect.width - 10;
			}

			// Adjust vertical position
			if (y + rect.height > viewportHeight) {
				newY = viewportHeight - rect.height - 10;
			}

			menuElement.style.left = `${newX}px`;
			menuElement.style.top = `${newY}px`;
		}
	});
</script>

<svelte:window on:click={handleClickOutside} />

{#if isVisible}
	<div
		bind:this={menuElement}
		class="context-menu"
		style="left: {x}px; top: {y}px;"
	>
		{#each items as item}
			{#if item.separator}
				<div class="menu-separator"></div>
			{:else}
				<div
					class="menu-item"
					class:disabled={item.disabled}
					class:has-submenu={item.submenu}
					onclick={() => handleItemClick(item)}
				>
					{#if item.icon}
						<span class="menu-icon">{item.icon}</span>
					{/if}
					<span class="menu-label">{item.label}</span>
					{#if item.submenu}
						<span class="submenu-arrow">▶</span>
					{/if}
				</div>
			{/if}
		{/each}
	</div>
{/if}

<style>
	.context-menu {
		position: fixed;
		background: white;
		border: 1px solid #ccc;
		border-radius: 4px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		padding: 4px 0;
		min-width: 180px;
		z-index: 10000;
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		font-size: 14px;
	}

	.menu-item {
		display: flex;
		align-items: center;
		padding: 8px 16px;
		cursor: pointer;
		user-select: none;
		transition: background-color 0.1s;
	}

	.menu-item:hover:not(.disabled) {
		background-color: #e6f3ff;
	}

	.menu-item.disabled {
		color: #999;
		cursor: default;
	}

	.menu-item.disabled:hover {
		background-color: transparent;
	}

	.menu-icon {
		margin-right: 8px;
		width: 16px;
		text-align: center;
		font-size: 12px;
	}

	.menu-label {
		flex: 1;
	}

	.has-submenu {
		position: relative;
	}

	.submenu-arrow {
		font-size: 10px;
		color: #666;
		margin-left: 8px;
	}

	.menu-separator {
		height: 1px;
		background-color: #e0e0e0;
		margin: 4px 0;
	}

	/* Animation for menu appearance */
	.context-menu {
		animation: menu-appear 0.1s ease-out;
	}

	@keyframes menu-appear {
		from {
			opacity: 0;
			transform: scale(0.95);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}
</style>