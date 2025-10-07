<script>
  export let status = 'Ready'
  export let backendHealthy = true
  export let simulationState = 'Idle'
</script>

<footer class="app-footer" role="contentinfo">
  <div class="footer-section">
    <strong>DWSIM</strong> Web Edition
  </div>
  <div class="footer-section">
    <span class="footer-label">Status:</span>
    <span class="chip" class:ok={backendHealthy} class:error={!backendHealthy}>{backendHealthy ? 'Backend Connected' : 'Backend Unreachable'}</span>
    <span class="chip neutral">Simulation: {simulationState}</span>
  </div>
  <div class="footer-section">
    <span class="footer-label">Shortcuts:</span>
    <span class="shortcut">N = New</span>
    <span class="shortcut">R = Run</span>
  </div>
</footer>

<style>
  .app-footer {
    height: 34px;
    background: #1e293b;
    color: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    font-size: 12px;
    gap: 24px;
  }
  .footer-section { display: flex; align-items: center; gap: 12px; }
  .footer-label { opacity: 0.7; }
  .chip { padding: 4px 10px; border-radius: 999px; background: #334155; font-weight: 500; }
  .chip.ok { background: #065f46; color: #d1fae5; }
  .chip.error { background: #7f1d1d; color: #fecaca; }
  .chip.neutral { background: #475569; color: #f1f5f9; }
  .shortcut { background: #334155; padding: 2px 6px; border-radius: 4px; font-family: monospace; opacity: 0.85; }
</style>