<script lang="ts">
  import { onMount } from 'svelte'
  import { configApi } from '../lib/api'
  import { DATA_SOURCE_TYPES } from '../lib/types'
  import type { Config, CreateConfigPayload } from '../lib/types'

  let configs: Config[] = []
  let loadError = ''
  let loading = true

  let showForm = false
  let submitting = false
  let formError = ''

  let form: CreateConfigPayload = { type: DATA_SOURCE_TYPES[0], host: '', user: '', password: '' }

  async function loadConfigs() {
    loading = true
    loadError = ''
    try {
      configs = await configApi.list()
    } catch (e) {
      loadError = (e as Error).message
    } finally {
      loading = false
    }
  }

  async function handleSubmit() {
    if (!form.type || !form.host || !form.user || !form.password) {
      formError = '모든 필드를 입력해주세요.'
      return
    }
    submitting = true
    formError = ''
    try {
      await configApi.create(form)
      form = { type: DATA_SOURCE_TYPES[0], host: '', user: '', password: '' }
      showForm = false
      await loadConfigs()
    } catch (e) {
      formError = (e as Error).message
    } finally {
      submitting = false
    }
  }

  function cancelForm() {
    showForm = false
    formError = ''
    form = { type: DATA_SOURCE_TYPES[0], host: '', user: '', password: '' }
  }

  onMount(loadConfigs)
</script>

<section>
  <div class="page-header">
    <div>
      <h1>Data Source</h1>
      <p class="subtitle">등록된 데이터베이스 접속 설정을 관리합니다.</p>
    </div>
    <button class="btn-primary" on:click={() => (showForm = true)}>+ 데이터 소스 추가</button>
  </div>

  {#if showForm}
    <div class="form-card">
      <h2>데이터 소스 추가</h2>

      {#if formError}
        <p class="error-message">{formError}</p>
      {/if}

      <div class="form-grid">
        <div class="form-group">
          <label for="ds-type">타입</label>
          <select id="ds-type" bind:value={form.type}>
            {#each DATA_SOURCE_TYPES as t}
              <option value={t}>{t}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label for="ds-host">Host</label>
          <input id="ds-host" type="text" placeholder="localhost:5432" bind:value={form.host} />
        </div>

        <div class="form-group">
          <label for="ds-user">User</label>
          <input id="ds-user" type="text" placeholder="postgres" bind:value={form.user} />
        </div>

        <div class="form-group">
          <label for="ds-password">Password</label>
          <input id="ds-password" type="password" bind:value={form.password} />
        </div>
      </div>

      <div class="form-actions">
        <button class="btn-secondary" on:click={cancelForm} disabled={submitting}>취소</button>
        <button class="btn-primary" on:click={handleSubmit} disabled={submitting}>
          {submitting ? '추가 중…' : '추가'}
        </button>
      </div>
    </div>
  {/if}

  {#if loading}
    <p class="loading-text">불러오는 중…</p>
  {:else if loadError}
    <div class="error-message">{loadError}</div>
    <button class="btn-secondary" style="margin-top:12px" on:click={loadConfigs}>다시 시도</button>
  {:else if configs.length === 0}
    <div class="empty-state">
      <span style="font-size:36px">🗄</span>
      <p>등록된 데이터 소스가 없습니다.</p>
      <p style="font-size:13px; color: var(--color-text-muted)">우측 상단 버튼으로 추가해주세요.</p>
    </div>
  {:else}
    <div class="card-grid">
      {#each configs as config (config.id)}
        <div class="source-card">
          <div class="card-header">
            <span class="badge">{config.type}</span>
            <span class="card-id">#{config.id}</span>
          </div>
          <div class="card-field">
            <span class="field-label">Host</span>
            <span class="field-value">{config.host}</span>
          </div>
          <div class="card-field">
            <span class="field-label">User</span>
            <span class="field-value">{config.user}</span>
          </div>
          <div class="card-field">
            <span class="field-label">Password</span>
            <span class="field-value masked">{'•'.repeat(8)}</span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  section {
    max-width: 960px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
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

  .form-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-sm);
  }

  .form-card h2 {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 16px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 16px;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  .loading-text {
    color: var(--color-text-muted);
    padding: 32px 0;
    text-align: center;
  }

  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
  }

  .source-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 16px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.15s, border-color 0.15s;
  }

  .source-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--color-border-focus);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .card-id {
    font-size: 12px;
    color: var(--color-text-muted);
  }

  .card-field {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 5px 0;
    border-bottom: 1px solid var(--color-border);
    gap: 8px;
  }

  .card-field:last-child {
    border-bottom: none;
  }

  .field-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    flex-shrink: 0;
  }

  .field-value {
    font-size: 13px;
    color: var(--color-text);
    font-family: var(--font-mono);
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    text-align: right;
  }

  .masked {
    letter-spacing: 3px;
    color: var(--color-text-muted);
  }
</style>
