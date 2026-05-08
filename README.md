# analytics-copilot

> 데이터 분석가를 위한 대화형 SQL 분석 환경

자연어로 질문하면 **SQL 생성 → 실행 → 차트**까지 한 번에. 별도 API 서버 없이 로컬에서 바로 실행됩니다.

```
분석가: "장르별 평균 평점 보여줘"
  → SQL 자동 생성
  → Trino 실행
  → 마크다운 테이블로 결과 출력
  → /chart bar 로 바차트 시각화
```

---

## 기술 스택

| 역할 | 기술 |
|------|------|
| 쿼리 엔진 | [Trino](https://trino.io) (Docker) |
| 중간 결과 저장 | [DuckDB](https://duckdb.org) (로컬 파일) |
| 온톨로지 | 별도 GitHub repo (git submodule) |
| 차트 | [Plotly](https://plotly.com/python) → HTML |
| AI 인터페이스 | [Claude Code](https://claude.ai/code) 커스텀 스킬 |

---

## 시작하기

### 사전 요구사항

- Docker
- Python 3.9+
- [Claude Code](https://claude.ai/code)

### 설치

```bash
# 1. 레포 클론 (온톨로지 submodule 포함)
git clone --recurse-submodules <repo-url>

# 2. 의존성 설치
pip install -r requirements.txt

# 3. Trino 실행
docker-compose up -d

# 4. 샘플 데이터 로드 (Trino 기동 후 ~30초 대기)
python scripts/setup_data.py
```

> **온톨로지 repo가 아직 등록되지 않은 경우:** `/sync` 실행 시 GitHub URL을 입력하면 자동으로 submodule이 설정됩니다.

### 분석 시작

Claude Code에서 프로젝트 디렉터리를 열고:

```
/analyze 장르별 평균 평점 보여줘
```

---

## 스킬

Claude Code 커스텀 스킬로 분석 워크플로우를 실행합니다.

| 스킬 | 설명 | 예시 |
|------|------|------|
| `/analyze <질문>` | 자연어 → SQL → 결과 테이블 | `/analyze 평점 상위 영화 Top 10` |
| `/chart <타입>` | 마지막 결과를 차트로 시각화 | `/chart bar` `/chart pie` |
| `/save <name>` | 결과를 DuckDB에 저장해 후속 분석에 재사용 | `/save genre_stats` |
| `/schema [table]` | 테이블·컬럼·관계 탐색 | `/schema ratings` |
| `/sync` | Trino 스키마 → 온톨로지 repo 동기화 | `/sync` |

### 분석 흐름 예시

```
/analyze 장르별 평균 평점          # Trino 원천 쿼리
/save genre_ratings               # DuckDB scratch에 저장
/analyze scratch.genre_ratings에서 평점 3.2 이상 필터  # DuckDB 후속 분석
/chart bar                        # 시각화
```

---

## 아키텍처

```
analytics-copilot/
├── catalog/
│   ├── ontology_config.yaml  # 온톨로지 repo 경로 설정
│   └── ontology/             # 온톨로지 repo (git submodule)
│       └── schema.yaml       # 테이블·컬럼 메타데이터 + FK 관계 정의
├── scripts/
│   ├── setup_data.py         # 샘플 데이터 로드
│   ├── run_query.py          # SQL 실행 (Trino / DuckDB 자동 라우팅)
│   ├── save_result.py        # 결과 → DuckDB named 테이블
│   ├── chart.py              # Plotly 차트 생성
│   └── sync_catalog.py       # Trino 스키마 → 온톨로지 repo 동기화
├── scratch/                  # DuckDB 중간 결과 저장소 (로컬 영속)
├── trino/
│   └── catalog/
│       └── memory.properties
└── docker-compose.yaml
```

### 엔진 라우팅

`run_query.py`가 SQL을 분석해 자동으로 엔진을 선택합니다.

| SQL 조건 | 엔진 |
|----------|------|
| `scratch.*` 테이블 참조 | DuckDB |
| `memory.default.*` 또는 Trino 카탈로그 | Trino |

---

## 참고 문서

- [CLAUDE.md](./CLAUDE.md) — 아키텍처 및 상세 가이드
- [docs/cmux-setup.md](./docs/cmux-setup.md) — cmux 멀티패널 환경 설정

---

## 라이선스

MIT
