# frontend — Mini Data Catalog

Svelte 4 + Vite 5 + TypeScript SPA. 백엔드(`http://localhost:8000`) API를 `/api` 프록시로 호출한다.

## 레이아웃

```
<header>  — 앱 바 (52px, 다크)
<nav>     — 사이드바 (200px) — Data Source / Data Catalog 전환
<main>    — 선택된 컴포넌트 렌더링
```

## 파일 구조

```
src/
├── App.svelte               — 앱 셸: 헤더 + 레이아웃 + 라우팅 (store 기반)
├── main.ts                  — 마운트 진입점
├── style.css                — CSS 변수(--color-*, --radius-*, --shadow-*) + 공통 유틸
├── lib/
│   ├── types.ts             — 백엔드 Pydantic 모델 미러 타입
│   ├── api.ts               — fetch 래퍼 (configApi, catalogApi, schedulerApi)
│   └── stores.ts            — currentPage writable store
└── components/
    ├── DataSource.svelte    — Config CRUD (GET/POST /api/config/)
    └── DataCatalog.svelte   — 테이블/컬럼 브라우저 + 설명 편집 + 동기화 트리거
```

## API 엔드포인트 매핑

| 기능 | 메서드 | 경로 |
|------|--------|------|
| Config 목록 | GET | `/api/config/` |
| Config 등록 | POST | `/api/config/` |
| 테이블 목록 | GET | `/api/catalog/` |
| 테이블 상세 | GET | `/api/catalog/{name}` |
| 테이블 수정 | PUT | `/api/catalog/{name}` |
| 동기화 트리거 | POST | `/api/scheduler/sync/` |

## CSS 컨벤션

- 공통 변수는 `style.css` `:root`에 정의 (`--color-primary`, `--radius-md` 등)
- 컴포넌트 고유 스타일은 각 `.svelte` 파일 내 `<style>` (scoped)
- 공통 클래스: `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.form-group`, `.error-message`, `.empty-state`, `.badge`
- UI 라이브러리/Tailwind 없음 — plain CSS 유지

## 개발 서버

```bash
cd frontend
npm install
npm run dev    # → http://localhost:3000
```

백엔드(`http://localhost:8000`)가 실행 중이어야 API 호출이 동작한다.

## 주의사항

- `backend/`, `example/`, `temporal/` 수정 금지
- SvelteKit 도입 금지 (Svelte 4 단일 SPA)
- 페이지 전환은 `currentPage` store로만 처리 (URL 라우팅 없음)
- `alert()` 사용 금지 — 컴포넌트 내 인라인 에러 상태 사용
- 백엔드 Config 모델 필드: `id, type, host, user, password` (name/port/database 없음 — WIP)
