<script>
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  function handleMenuClick(menuItem) {
    dispatch('menuClick', { menuItem })
  }
</script>

<header class="app-header">
  <div class="header-left">
    <div class="logo">
      <span class="logo-icon">🧪</span>
      <span class="logo-text">DWSIM</span>
      <span class="version">Web Edition</span>
    </div>
  </div>

  <nav class="header-nav">
    <button class="nav-item" on:click={() => handleMenuClick('file')}>
      File
    </button>
    <button class="nav-item" on:click={() => handleMenuClick('edit')}>
      Edit
    </button>
    <button class="nav-item" on:click={() => handleMenuClick('view')}>
      View
    </button>
    <button class="nav-item" on:click={() => handleMenuClick('tools')}>
      Tools
    </button>
    <button class="nav-item" on:click={() => handleMenuClick('help')}>
      Help
    </button>
  </nav>

  <div class="header-right">
    <div class="status-indicator">
      <span class="status-dot status-ready"></span>
      <span class="status-text">Ready</span>
    </div>
  </div>
</header>

<style>
  .app-header {
    height: 50px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000;
  }

  .header-left {
    display: flex;
    align-items: center;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .logo-icon {
    font-size: 24px;
  }

  .logo-text {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.5px;
  }

  .version {
    font-size: 10px;
    opacity: 0.8;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .header-nav {
    display: flex;
    gap: 4px;
  }

  .nav-item {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background-color 0.2s ease;
  }

  .nav-item:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-ready {
    background: #4ade80;
    box-shadow: 0 0 6px rgba(74, 222, 128, 0.5);
  }

  .status-text {
    opacity: 0.9;
  }
</style>