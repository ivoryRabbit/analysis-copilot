# /sync — 카탈로그 동기화

Trino `information_schema`에서 테이블·컬럼 정보를 가져와 온톨로지 repo의 `schema.yaml`을 최신 상태로 갱신한다.

**동기화 원칙:**
- **Trino** = 컬럼명·타입의 소스 오브 트루스
- **온톨로지 repo의 schema.yaml** = description을 보강하는 레이어 (git submodule로 버전 관리)
- 기존 `description` 필드는 병합 시 보존된다

**권한 구분:**
- 분석가: `sync/` 브랜치에 push 및 PR 생성 가능
- 온톨로지 담당자: PR 리뷰 후 main 머지

## 사용법

```
/sync                              # 온톨로지 submodule 자동 감지 후 동기화
/sync --catalog <c> --schema <s>   # 대상 카탈로그·스키마 지정
```

---

## 실행 절차

### Step 0. 온톨로지 submodule 및 설정 확인

```bash
git submodule status catalog/ontology
```

**submodule이 등록되지 않은 경우 (출력이 없거나 오류):**

사용자에게 아래 두 가지를 물어본다:
> 1. 온톨로지 repo의 GitHub URL을 알려주세요. (예: `https://github.com/your-org/ontology-repo`)
> 2. GitHub repo 슬러그를 알려주세요. (예: `your-org/ontology-repo`) — `gh pr create`에 사용됩니다.

입력받은 값으로 submodule을 등록하고, `ontology_config.yaml`의 `github_repo` 필드를 업데이트한 뒤 커밋한다:

```bash
git submodule add <repo_url> catalog/ontology
git add .gitmodules catalog/ontology catalog/ontology_config.yaml
git commit -m "chore: add ontology repo as submodule"
```

**이미 등록되었으나 `ontology_config.yaml`의 `github_repo`가 기본값(`your-org/ontology-repo`)인 경우:**

사용자에게 물어본다:
> GitHub repo 슬러그를 알려주세요. (예: `your-org/ontology-repo`) — `gh pr create`에 사용됩니다.

입력받은 값으로 `ontology_config.yaml`의 `github_repo` 필드를 업데이트한다.

**이미 등록된 경우:**

submodule을 최신 커밋으로 업데이트한다:

```bash
git submodule update --remote catalog/ontology
```

---

### Step 1. 동기화 실행

```bash
python scripts/sync_catalog.py
```

특정 카탈로그·스키마 대상:

```bash
python scripts/sync_catalog.py --catalog memory --schema default
```

---

### Step 2. 결과 확인

```bash
cat catalog/ontology/schema.yaml
```

---

### Step 3. 변경 사항 안내

동기화 후 추가·제거된 테이블·컬럼을 요약해서 보여준다:

```
동기화 완료
  대상: catalog/ontology/schema.yaml
  추가된 테이블: events
  추가된 컬럼 : ratings.source (varchar)
  제거된 컬럼 : movies.metadata
```

변경 사항이 없으면 Step 4~6을 건너뛰고 Step 7로 이동한다.

---

### Step 4. 온톨로지 repo — 브랜치 생성 및 커밋

`sync/YYYYMMDD` 형식의 브랜치를 만들고 변경 사항을 커밋한다:

```bash
BRANCH="sync/$(date +%Y%m%d)"
git -C catalog/ontology checkout -b "$BRANCH"
git -C catalog/ontology add schema.yaml
git -C catalog/ontology commit -m "sync: update schema from Trino"
```

---

### Step 5. 온톨로지 repo — 브랜치 push 및 PR 생성

```bash
git -C catalog/ontology push origin "$BRANCH"
```

GitHub CLI가 설치된 경우 PR을 자동 생성한다:

```bash
GITHUB_REPO=$(python -c "import yaml; c=yaml.safe_load(open('catalog/ontology_config.yaml')); print(c['github_repo'])")
gh pr create \
  --repo "$GITHUB_REPO" \
  --head "$BRANCH" \
  --base main \
  --title "sync: update schema from Trino ($(date +%Y-%m-%d))" \
  --body "Trino information_schema 변경사항을 schema.yaml에 반영합니다."
```

PR URL을 사용자에게 안내한다:
> PR이 생성되었습니다: <PR URL>
> 온톨로지 담당자의 리뷰 후 머지됩니다.

---

### Step 6. analytics-copilot repo — submodule 참조 업데이트

온톨로지 repo PR이 머지되면 analytics-copilot의 submodule 참조를 갱신한다.
**PR 머지 전에는 이 단계를 실행하지 않는다.**

사용자에게 안내한다:
> PR 머지 후 아래를 실행해 submodule 참조를 갱신하세요:
> ```bash
> git submodule update --remote catalog/ontology
> git add catalog/ontology
> git commit -m "chore: update ontology submodule"
> ```

---

### Step 7. description 작성 안내

description이 비어 있는 컬럼이 있으면 채우도록 안내한다.
description이 풍부할수록 `/analyze`의 SQL 생성 품질이 높아진다:

```yaml
- name: occupation
  type: integer
  description: "직업 코드 (0=기타, 1=교육, 4=IT, 7=경영 ...)"
```
