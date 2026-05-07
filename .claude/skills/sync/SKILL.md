# /sync — 카탈로그 동기화

Trino `information_schema`에서 테이블·컬럼 정보를 가져와 `catalog/schema.yaml`을 최신 상태로 갱신한다.

**동기화 원칙:**
- **Trino** = 컬럼명·타입의 소스 오브 트루스
- **schema.yaml** = description을 보강하는 레이어 (git으로 버전 관리)
- 기존 `description` 필드는 병합 시 보존된다

## 사용법

```
/sync                         # memory.default 동기화 (기본)
/sync --catalog <c> --schema <s>   # 대상 지정
```

## 실행 절차

### Step 1. 동기화 실행

```bash
python scripts/sync_catalog.py
```

특정 카탈로그·스키마 대상:
```bash
python scripts/sync_catalog.py --catalog memory --schema default
```

### Step 2. 결과 확인

```bash
cat catalog/schema.yaml
```

### Step 3. 변경 사항 안내

동기화 후 추가·제거된 테이블·컬럼을 요약해서 보여준다:

예시:
```
동기화 완료
  추가된 테이블: events
  추가된 컬럼 : ratings.source (varchar)
  제거된 컬럼 : movies.metadata
```

### Step 4. description 작성 안내

description이 비어 있는 컬럼이 있으면 채우도록 안내한다.
description이 풍부할수록 `/analyze`의 SQL 생성 품질이 높아진다:

```yaml
- name: occupation
  type: integer
  description: "직업 코드 (0=기타, 1=교육, 4=IT, 7=경영 ...)"
```
