<script lang="ts">
  import { onMount } from 'svelte'
  import { catalogApi, schedulerApi } from '../lib/api'
  import type { TableCatalog, ColumnCatalog } from '../lib/types'

  let tables: TableCatalog[] = []
  let loadError = ''
  let loading = true

  let selectedTable: TableCatalog | null = null
  let tableLoading = false
  let tableError = ''

  let editedColumns: Array<{ name: string; type: string; description: string }> = []
  let saving = false
  let saveError = ''
  let saveSuccess = false

  let syncing = false
  let syncMessage = ''
  let syncError = ''

  async function loadTables() {
    loading = true
    loadError = ''
    try {
      tables = await catalogApi.listTables()
    } catch (e) {
      loadError = (e as Error).message
    } finally {
      loading = false
    }
  }

  async function selectTable(name: string) {
    tableLoading = true
    tableError = ''
    saveError = ''
    saveSuccess = false
    selectedTable = null
    try {
      selectedTable = await catalogApi.getTable(name)
      editedColumns = (selectedTable.columns ?? []).map(col => ({
        name: col.name,
        type: col.type,
        description: col.description ?? '',
      }))
    } catch (e) {
      tableError = (e as Error).message
    } finally {
      tableLoading = false
    }
  }

  async function saveChanges() {
    if (!selectedTable) return
    saving = true
    saveError = ''
    saveSuccess = false
    try {
      await catalogApi.updateTable(selectedTable.name, { columns: editedColumns })
      saveSuccess = true
      await loadTables()
      // refresh selected table
      await selectTable(selectedTable.name)
    } catch (e) {
      saveError = (e as Error).message
    } finally {
      saving = false
    }
  }

  async function triggerSync() {
    syncing = true
    syncMessage = ''
    syncError = ''
    try {
      const result = await schedulerApi.triggerSync()
      syncMessage = `동기화 시작됨 (workflow: ${result.workflow_id})`
    } catch (e) {
      syncError = (e as Error).message
    } finally {
      syncing = false
    }
  }

  function getTypeColor(type: string): string {
    const t = type.toLowerCase()
    if (t.includes('int') || t.includes('float') || t.includes('numeric') || t.includes('double')) return '#7c3aed'
    if (t.includes('varchar') || t.includes('text') || t.includes('char')) return '#0369a1'
    if (t.includes('bool')) return '#15803d'
    if (t.includes('date') || t.includes('time') || t.includes('timestamp')) return '#b45309'
    if (t.includes('json')) return '#c2410c'
    return '#374151'
  }

  onMount(loadTables)
</script>

<div class="page">
  <div class="page-header">
    <div>
      <h1>Data Catalog</h1>
      <p class="subtitle">테이블과 컬럼 메타데이터를 조회하고 편집합니다.</p>
    </div>
    <div class="header-actions">
      {#if syncMessage}
        <span class="sync-success">{syncMessage}</span>
      {/if}
      {#if syncError}
        <span class="sync-error">{syncError}</span>
      {/if}
      <button class="btn-secondary" on:click={triggerSync} disabled={syncing}>
        {syncing ? '동기화 중…' : '🔄 동기화'}
      </button>
    </div>
  </div>

  <div class="content">
    <!-- Table list panel -->
    <aside class="table-list">
      <div class="panel-header">
        <span>테이블 ({tables.length})</span>
        <button class="btn-icon" title="새로고침" on:click={loadTables} disabled={loading}>↺</button>
      </div>

      {#if loading}
        <p class="panel-loading">불러오는 중…</p>
      {:else if loadError}
        <p class="panel-error">{loadError}</p>
      {:else if tables.length === 0}
        <div class="empty-state">
          <span style="font-size:28px">📭</span>
          <p>카탈로그가 비어있습니다.</p>
          <p style="font-size:12px">동기화를 실행해주세요.</p>
        </div>
      {:else}
        <ul class="table-items">
          {#each tables as table (table.id)}
            <li>
              <button
                class="table-item"
                class:selected={selectedTable?.id === table.id}
                on:click={() => selectTable(table.name)}
              >
                <span class="table-name">{table.name}</span>
                {#if table.columns?.length}
                  <span class="col-count">{table.columns.length}</span>
                {/if}
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </aside>

    <!-- Detail panel -->
    <div class="detail-panel">
      {#if tableLoading}
        <p class="panel-loading">불러오는 중…</p>
      {:else if tableError}
        <p class="panel-error">{tableError}</p>
      {:else if !selectedTable}
        <div class="empty-state">
          <span style="font-size:36px">👈</span>
          <p>좌측에서 테이블을 선택해주세요.</p>
        </div>
      {:else}
        <div class="table-detail">
          <div class="detail-header">
            <h2>{selectedTable.name}</h2>
            <p class="description">{selectedTable.description ?? '설명 없음'}</p>
          </div>

          {#if saveSuccess}
            <p class="save-success">변경사항이 저장되었습니다.</p>
          {/if}
          {#if saveError}
            <p class="error-message">{saveError}</p>
          {/if}

          <div class="columns-section">
            <div class="section-title">
              <span>컬럼 ({editedColumns.length})</span>
            </div>

            {#if editedColumns.length === 0}
              <p class="no-columns">컬럼 정보가 없습니다.</p>
            {:else}
              <table class="columns-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {#each editedColumns as col, i (col.name)}
                    <tr>
                      <td class="col-name">{col.name}</td>
                      <td>
                        <span class="type-badge" style="color: {getTypeColor(col.type)}">
                          {col.type}
                        </span>
                      </td>
                      <td>
                        <input
                          type="text"
                          class="desc-input"
                          placeholder="설명을 입력하세요"
                          bind:value={editedColumns[i].description}
                        />
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>

              <div class="save-row">
                <button class="btn-primary" on:click={saveChanges} disabled={saving}>
                  {saving ? '저장 중…' : '변경사항 저장'}
                </button>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .page {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: 1100px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    flex-shrink: 0;
  }

  h1 {
    font-size: 22px;
    font-weight: 700;
    color: var(--color-text);
  }

  .subtitle {
    font-size: 13px;
    color: var(--color-text-muted);
    margin-top: 3px;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .sync-success {
    font-size: 12px;
    color: var(--color-success);
  }

  .sync-error {
    font-size: 12px;
    color: var(--color-danger);
  }

  .content {
    display: flex;
    gap: 16px;
    flex: 1;
    overflow: hidden;
    min-height: 0;
  }

  aside.table-list {
    width: 220px;
    flex-shrink: 0;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 14px;
    border-bottom: 1px solid var(--color-border);
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }

  .btn-icon {
    background: transparent;
    padding: 2px 6px;
    font-size: 15px;
    color: var(--color-text-muted);
    border-radius: var(--radius-sm);
  }

  .btn-icon:hover:not(:disabled) {
    background: var(--color-bg);
    color: var(--color-text);
  }

  .panel-loading,
  .panel-error {
    padding: 16px;
    font-size: 13px;
    color: var(--color-text-muted);
  }

  .panel-error {
    color: var(--color-danger);
  }

  .table-items {
    list-style: none;
    overflow-y: auto;
    flex: 1;
    padding: 6px;
  }

  .table-item {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--color-text);
    font-size: 13px;
    text-align: left;
    gap: 6px;
  }

  .table-item:hover {
    background: var(--color-bg);
  }

  .table-item.selected {
    background: var(--color-primary-light);
    color: var(--color-primary);
    font-weight: 500;
  }

  .table-name {
    font-family: var(--font-mono);
    font-size: 12.5px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .col-count {
    font-size: 11px;
    background: var(--color-bg);
    color: var(--color-text-muted);
    border-radius: 99px;
    padding: 1px 6px;
    flex-shrink: 0;
  }

  .table-item.selected .col-count {
    background: #dbeafe;
    color: var(--color-primary);
  }

  .detail-panel {
    flex: 1;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    overflow-y: auto;
    padding: 20px;
  }

  .table-detail {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .detail-header h2 {
    font-size: 18px;
    font-weight: 700;
    font-family: var(--font-mono);
    margin-bottom: 4px;
  }

  .description {
    font-size: 13px;
    color: var(--color-text-muted);
    font-style: italic;
  }

  .save-success {
    font-size: 13px;
    color: var(--color-success);
    padding: 8px 12px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: var(--radius-sm);
  }

  .section-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 10px;
  }

  .no-columns {
    color: var(--color-text-muted);
    font-size: 13px;
  }

  .columns-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  .columns-table th {
    text-align: left;
    padding: 8px 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: var(--color-text-muted);
    border-bottom: 2px solid var(--color-border);
  }

  .columns-table td {
    padding: 7px 10px;
    border-bottom: 1px solid var(--color-border);
    vertical-align: middle;
  }

  .columns-table tr:last-child td {
    border-bottom: none;
  }

  .columns-table tr:hover td {
    background: var(--color-bg);
  }

  .col-name {
    font-family: var(--font-mono);
    font-size: 12.5px;
    font-weight: 500;
    white-space: nowrap;
  }

  .type-badge {
    font-family: var(--font-mono);
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
  }

  .desc-input {
    font-size: 13px;
    padding: 5px 8px;
    border-radius: var(--radius-sm);
  }

  .save-row {
    display: flex;
    justify-content: flex-end;
    padding-top: 4px;
  }
</style>
