<script lang="ts">
  import { currentPage, type Page } from './lib/stores'
  import DataSource from './components/DataSource.svelte'
  import DataCatalog from './components/DataCatalog.svelte'

  const navItems: { id: Page; label: string; icon: string }[] = [
    { id: 'datasource', label: 'Data Source',  icon: '🗄' },
    { id: 'catalog',    label: 'Data Catalog', icon: '📖' },
  ]
</script>

<header>
  <span class="logo">📚 Mini Data Catalog</span>
</header>

<div class="layout">
  <nav>
    <ul>
      {#each navItems as item}
        <li>
          <button
            class="nav-item"
            class:active={$currentPage === item.id}
            on:click={() => currentPage.set(item.id)}
          >
            <span class="nav-icon">{item.icon}</span>
            {item.label}
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  <main>
    {#if $currentPage === 'datasource'}
      <DataSource />
    {:else}
      <DataCatalog />
    {/if}
  </main>
</div>

<style>
  header {
    height: 52px;
    background: var(--color-header-bg);
    color: #f8fafc;
    display: flex;
    align-items: center;
    padding: 0 20px;
    flex-shrink: 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    z-index: 10;
  }

  .logo {
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.2px;
  }

  .layout {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  nav {
    width: 200px;
    flex-shrink: 0;
    background: var(--color-sidebar-bg);
    border-right: 1px solid var(--color-border);
    padding: 12px 8px;
    overflow-y: auto;
  }

  ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .nav-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 9px 12px;
    border-radius: var(--radius-md);
    background: transparent;
    color: var(--color-text-secondary);
    font-size: 13.5px;
    font-weight: 500;
    text-align: left;
    transition: background 0.12s, color 0.12s;
  }

  .nav-item:hover {
    background: var(--color-bg);
    color: var(--color-text);
  }

  .nav-item.active {
    background: var(--color-primary-light);
    color: var(--color-primary);
  }

  .nav-icon {
    font-size: 15px;
  }

  main {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }
</style>
