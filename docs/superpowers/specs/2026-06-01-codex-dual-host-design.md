# Codex Dual-Host 설계 (slide-svg)

> 상태: 승인됨(설계) · 작성일 2026-06-01 · 대상 repo: `slide-svg`
> 목표: 이 repo를 **Claude Code · Codex(클라우드/웹) 양쪽**에서 사용 가능하게 하면서, **현재 Claude Code 품질을 한 글자도 손대지 않고** 유지한다.

---

## 1. 배경 / 문제

동일 repo를 Claude Code와 Codex에서 각각 `/slide`로 돌렸을 때 Codex 결과물이 현저히 낮았다. 사용자가 붙여준 Codex 자기분석은 원인을 "Claude 전용 repo라서 안 됨"으로 일부 귀인했지만, **실제 코드 탐색 결과 그 진단은 부정확**하다:

- `AGENTS.md` 없음, `.codex/` 없음 → Codex가 잡을 진입점이 전무.
- 그러나 Python 파이프라인(`svg_to_pptx.py`, `svg_finalize/embed_icons.py`, `_py.sh`)은 **이미 경로 무관**이다. 전부 `__file__` 기준 `parents[N]` / 4-level walk-up으로 repo root와 `assets/`를 찾는다. `.claude` 문자열은 ~14곳뿐이고 대부분 **docstring/주석**이다.
- `.codex/skills/slide/scripts/...`는 `.claude/skills/slide/scripts/...`와 **디렉터리 깊이가 동일**(둘 다 repo root 바로 아래)하므로 `parents[N]` 가정이 그대로 성립한다.

따라서 진짜 병목은 *경로 하드코딩*이 아니라:

1. **실행 규율 부재** — Codex가 `SKILL.md`를 런타임 절차로 실행하지 않고 "문서로 읽고 즉흥 구현(fallback)" 했다. slide-plan 자동 진입을 건너뛰었고, 이미지 로그인 실패 시 PIL placeholder로 silent fallback 했으며, 검증 루프를 돌지 않았다.
2. **우회를 막을 강제 장치 부재** — 즉흥 우회를 했을 때 파이프라인이 실패하지 않으니, shortcut이 "성공"으로 보였다.

## 2. 목표 / 비목표

**목표**
- Codex(클라우드/웹)가 이 repo에서 `/slide`를 Claude Code와 동등한 절차로 실행하게 한다.
- Claude Code 경로(`.claude/skills/`)는 **정본(canonical)으로 불변** — 품질 무손상 보장.
- Codex가 절차를 우회하면 **하드 페일**로 막는다.

**비목표 (이번 범위 밖)**
- slide-html / slide-pencil repo 수정 (단, **이식 가능한 패턴**으로 설계하고 부록 A에 이식 가이드를 남긴다).
- 런타임 멀티 테마 (영구 락 유지).
- Codex 클라우드의 `image_gen` 백엔드 자체 구현 (가용성 검증 + 실패 시 halt만 담당).

## 3. 핵심 결정 (확정)

| 항목 | 결정 |
|------|------|
| Codex 실행 환경 | **클라우드/웹** (root `AGENTS.md`를 진입점으로 읽고, repo를 클론해 컨테이너에서 실행) |
| 호스트 연결 구조 | **`.codex/skills` 미러** — 단, 손수 복제가 아닌 **생성형 미러**(canonical=`.claude/skills`) |
| 작업 범위 | **slide-svg 이 repo만** (패턴은 재사용 가능하게) |
| 품질 게이트 | **하드 페일** (산출물 누락·placeholder·미러 stale 시 파이프라인 중단) |

### 3.1 "생성형 미러" 보정 (중요)

미러를 **손으로 두 벌 유지하면 드리프트**가 발생하고, 그게 새로운 품질 차이의 원인이 된다(Codex 분석문도 "복사론 부족"이라 경고). 따라서:

- **`.claude/skills` = 정본.** 사람은 여기만 편집한다.
- **`.codex/skills` = 생성물.** `sync_codex_mirror.py`가 `.claude/skills`에서 통째로 재생성한다. git에 커밋한다(클라우드가 클론 즉시 발견해야 하므로).
- **drift-check(`--check`)** 가 미러가 낡았으면 검증 게이트에서 exit 1.
- `.codex/skills`는 **hand-edit 금지** — AGENTS.md와 미러 헤더에 명시.

이로써 ① Codex는 원하는 `.codex/skills`에서 발견·실행, ② 정본 무손상, ③ 드리프트 물리적 차단.

## 4. 아키텍처 — 5개 기둥

### 기둥 1 — 생성형 `.codex/skills` 미러 + 드리프트 락

**파일:** `.claude/skills/slide/scripts/dev/sync_codex_mirror.py`

**동작:**
- 입력: repo root에서 `.claude/skills/` 전체.
- 출력: `.codex/skills/`를 삭제 후 재생성(멱등).
- **변환 규칙(유일):** 텍스트 파일(`.md`, `.py`, `.sh`, `.json`, `.txt`) 내 문자열 `.claude/skills` → `.codex/skills` 치환. 그 외 바이트는 그대로. 바이너리(폰트/이미지/SVG 자산)는 무변환 복사.
- **제외:** `__pycache__`, `*.pyc`, `.venv` 등.
- 각 미러 파일/디렉터리 루트에 헤더 주석 또는 `_GENERATED.md` 마커: "이 트리는 sync_codex_mirror.py 생성물. 직접 편집 금지. `.claude/skills`를 고치고 sync 재실행."
- **`--check` 모드:** 임시 디렉터리에 재생성 → `.codex/skills`와 diff. 다르면 stderr에 낡은 파일 목록 + 재실행 명령 출력 후 exit 1.

**자산 처리:** `assets/icons/`, `assets/fonts/`는 repo root에 있고 두 호스트가 공유 → 미러 대상 아님(스크립트가 walk-up으로 동일하게 참조).

**경로 깊이 불변식:** `.codex`와 `.claude`는 둘 다 repo root 직속 → `parents[N]` 가정 보존. sync는 깊이를 바꾸지 않는다.

### 기둥 2 — 루트 `AGENTS.md` (Codex 실행 규율의 핵심)

**파일:** `AGENTS.md` (repo root). 짧게 유지하고 전체 제약은 `CLAUDE.md`/`SKILL.md`를 SSOT로 참조. 핵심 강제 항목:

1. **라우팅:** 슬라이드 요청("슬라이드", "프레젠테이션", "생성PPT", "make slides", "/slide") → **반드시** `.codex/skills/slide/SKILL.md`를 단계대로 실행. 절차를 문서로 요약만 하고 즉흥 구현하는 것 금지. **fallback 재구현(직접 PPTX/이미지 생성) 금지.**
2. **계획 자동 진입:** 데크가 **≥ 8장 또는 강의/임원보고서/세일즈/멀티소스/명시적 품질요구** → 먼저 `.codex/skills/slide-plan/SKILL.md` 실행 → `output/<project>/slide_plan.json` 생성. 우회 키워드(`간단히`, `빠르게`, `quick`, `simple로`, `plan 없이`)만 예외.
3. **직렬 파이프라인 락:** strategist → [image_generator] → executor → post-processing → export. 교차 병합 금지, 메인 에이전트 단독 SVG(Step 6 위임 금지), 순차 페이지 생성.
4. **이미지 규율:** codex-image/`image_gen` 가용성·로그인 선검사. 이미지가 필요한데 진짜 생성이 불가하면 **HALT** — PIL/placeholder/단색 이미지로 silent fallback 금지.
5. **후처리 규율:** `total_md_split.py` → `finalize_svg.py` → `svg_to_pptx.py <project> -s final`을 **각각 별도 호출**. `cp` 금지, `-s final` 필수, 미문서 플래그 금지.
6. **완료 게이트:** "done" 선언 전 `verify_deck.py <project>` 통과 필수. 실패 시 완료 선언 금지.
7. **미러 주의:** `.codex/skills`는 생성물. 편집은 `.claude/skills`에서 하고 sync 재실행.

> Claude Code는 이 규율을 Skill 런타임으로 "공짜로" 얻는다(Skill 도구가 SKILL.md를 절차로 로드). Codex는 그 런타임이 없으므로 AGENTS.md가 그 역할을 대신한다 — 이것이 품질 차이의 핵심 교정점.

### 기둥 3 — 하드 페일 품질 게이트 (두 호스트 공용)

**파일:** `.claude/skills/slide/scripts/verify_deck.py`, `.claude/skills/slide/scripts/preflight.py` (sync로 `.codex`에도 미러됨).

**`preflight.py` (파이프라인 시작 전):**
- Python/venv 사용 가능 + `requirements.txt` 설치 확인(없으면 안내 후 exit 1).
- codex-image 로그인/가용성 상태(이미지 필요 데크일 때) → 실패 시 loud halt.
- `assets/` (icons/fonts) 존재 확인.
- 미러 freshness(`sync_codex_mirror.py --check`).

**`verify_deck.py <project_path>` (완료 전):** 아래 중 하나라도 실패 → exit 1.
1. **계획 강제:** 페이지 ≥ 8 인데 `slide_plan.json` 부재 → FAIL (우회 키워드가 기록된 경우 제외). 있으면 `validate_plan.py`로 위임 검증.
2. **단계 산출물:** `svg_final/` 페이지 수 == `svg_output/` 페이지 수.
3. **네이티브 PPTX:** `<project>.pptx` 존재 + `svg_quality_checker.py` 기반 네이티브성(미디어 카운트/도형 편집성) 검사. 이미지-플래튼된 데크 거부.
4. **이미지 진위:** `images/` 각 파일이 placeholder/degenerate 아님 — 휴리스틱(파일 크기 하한 + 픽셀 분산 하한; 단색·저분산 이미지 거부).
5. **`.gm` 라인:** 모든 콘텐츠 슬라이드 하단에 governing message 텍스트 존재.
6. **캔버스:** 모든 SVG `viewBox`/크기 1280×720.
7. **미러 freshness:** `sync --check` 통과.

**재사용 원칙:** 새 검증 로직을 중복 구현하지 않는다. `svg_quality_checker.py`(SVG/PPTX 품질)와 `slide-plan/scripts/validate_plan.py`(plan 구조)를 오케스트레이션하고, 게이트는 host-parity + 산출물 존재 + 이미지 진위만 추가한다.

### 기둥 4 — 경로/호스트 감사 (작지만 필수)

- `.claude` 리터럴 ~14곳 전수 확인: 전부 docstring/주석/문서면 무수정, 기능 하드코드 발견 시 `__file__` 파생으로 교정.
- `.codex/skills`에서 `_py.sh` + 3단 후처리 스모크 실행으로 동등 동작 확인.

### 기둥 5 — 문서 + 회귀 테스트

- `README.md`: "Claude Code / Codex dual-host" 섹션 추가.
- `CLAUDE.md`: AGENTS.md 존재 + **"`.claude/skills` 수정 후 `sync_codex_mirror.py` 재실행"** 워크플로 한 줄.
- `docs/dual-host.md`(선택): 운영 가이드 + 부록 A 이식 패턴.
- `tests/test_codex_mirror.py`: ① `sync --check` 통과, ② AGENTS.md가 가리키는 `.codex/skills/...` 경로 실재, ③ `.codex` 깊이에서 핵심 스크립트 import 가능.

## 5. 제어 흐름 — Codex 클라우드 실행 경로

```
Codex 클라우드: repo 클론 → root AGENTS.md 읽음
  → 슬라이드 요청 감지 → preflight.py (env/login/mirror)
  → (≥8장) slide-plan/SKILL.md → slide_plan.json
  → slide/SKILL.md 단계 실행 (strategist → image → executor → 후처리 → export)
  → verify_deck.py (하드 페일 게이트)
  → 통과 시에만 "완료"
```

`_py.sh`는 bash라 클라우드 Linux 컨테이너에서 동작. venv 부재 시 preflight가 안내/생성.

## 6. 에러 처리

모든 게이트 실패는 **exit ≠ 0 + 명확한 교정 메시지**(무엇이 빠졌는지 + 실행할 명령). silent fallback 일절 없음. AGENTS.md가 "게이트 실패 시 완료 선언 금지"를 명시하므로 Codex는 우회 대신 수정으로 유도된다.

## 7. 테스트 전략

- 단위: `sync_codex_mirror.py`(멱등성, `--check` 정확도), 이미지 진위 휴리스틱, `.gm`/캔버스 파서.
- 통합: `tests/test_codex_mirror.py`(미러 동기성 + 경로 해석).
- 회귀: 기존 `pytest tests/` 그대로 통과 유지.

## 8. 산출 파일 목록

| 파일 | 신규/수정 |
|------|-----------|
| `.claude/skills/slide/scripts/dev/sync_codex_mirror.py` | 신규 |
| `.claude/skills/slide/scripts/verify_deck.py` | 신규 |
| `.claude/skills/slide/scripts/preflight.py` | 신규 |
| `AGENTS.md` (root) | 신규 |
| `.codex/skills/**` | 신규(생성물, 커밋) |
| `tests/test_codex_mirror.py` | 신규 |
| `README.md`, `CLAUDE.md` | 수정(섹션 추가) |
| `docs/dual-host.md` | 신규(선택) |

## 9. 가정 / 리스크

- **(가정)** Codex 클라우드가 root `AGENTS.md`를 진입 지시로 읽는다. (사용자 직접 경험 기반.)
- **(리스크) Codex 클라우드의 이미지 생성** — `image_gen`/codex-image 가용성이 클라우드에서 CLI와 다를 수 있다. 완화: preflight가 가용성 선검사, verify가 placeholder 거부 → "진짜 이미지 or halt"로 강제. 백엔드 자체는 이번 범위 밖.
- **(리스크) Codex가 `.codex/skills`를 직접 편집** → 역드리프트. 완화: 미러 헤더 + AGENTS.md 경고 + drift-check.

---

## 부록 A — slide-html / slide-pencil 이식 패턴 (포터블)

세 repo의 파이프라인은 다르지만 **dual-host 패턴(아래 4원칙)은 동일**하다. 각 repo 에이전트에게 다음을 그대로 전달하면 된다.

### 원칙 1 — 정본 + 생성형 미러 (절대 두 벌 손수 유지 금지)
`.claude/skills` = 정본, `.codex/skills` = `sync_codex_mirror.py` 생성물(경로 문자열만 치환). drift-check를 게이트에 넣어 미러가 낡으면 하드 페일. → slide-svg의 `sync_codex_mirror.py`를 그대로 복사해 재사용 가능(파이프라인 무관).

### 원칙 2 — AGENTS.md = 실행 규율 강제기 (진짜 교정점)
품질 차이의 근원은 경로가 아니라 **Codex가 SKILL.md를 실행하지 않고 즉흥 구현**한 것. AGENTS.md가 강제할 것:
- 요청 → 해당 repo의 `SKILL.md`를 단계대로 실행, fallback 재구현 금지.
- 계획/사전단계 자동 진입(해당 repo 기준).
- 이미지/외부도구 로그인 실패 시 HALT(placeholder 금지).
- **"done 전 verify 게이트 통과 필수."**

### 원칙 3 — 하드 페일 게이트는 각 repo의 "골든 산출물"을 검사
Claude 실행이 남긴, Codex 실행이 빠뜨린 흔적을 **존재 검사로 강제**한다(이것이 shortcut을 비가역적으로 차단):

| repo | 검사할 골든 산출물(예) |
|------|------------------------|
| **slide-svg** | `slide_plan.json`(≥8장), `svg_final/`==`svg_output/`, 네이티브 PPTX, 비-placeholder 이미지, `.gm` |
| **slide-html** | 미디어 용량(예: ≥수백 KB ↔ placeholder 60KB), text-run 수(예: ≈286 ↔ 147), HTML→PPTX 산출물 |
| **slide-pencil** | `pipeline_status.json`(`pencil_native_frames`, `manifest_check N/N`, `triple_gate`, `embedded_images`), **frame 수 == TSX 수 == plan slide 수**, `_eval/slide*.png`, **Pencil CLI 실제 실행(React fallback 금지)**, Tailwind `@source "./slides"` 등록 |

각 repo는 "Claude 결과 vs Codex 결과" 디렉터리를 비교해 빠진 산출물을 골든 체크로 인코딩한다.

### 원칙 4 — 스크립트는 경로 무관(`__file__` 기준)
`.claude` 하드코딩 대신 `parents[N]`/walk-up으로 repo root를 찾으면 같은 스크립트가 `.codex`에서도 그대로 돈다. `.claude`/`.codex` 깊이만 같으면 됨.

> **한 줄 요약(다른 에이전트에게):** "경로를 바꾸는 게 핵심이 아니다. (1) `.codex/skills`를 손수 복사하지 말고 `.claude/skills`에서 **생성**하라(drift-check 포함). (2) `AGENTS.md`로 SKILL.md를 **절차로 실행**하도록 강제하라(즉흥 fallback 금지). (3) 너희 repo의 **골든 산출물**(slide-pencil이면 pipeline_status.json·frame수·_eval PNG·Pencil CLI 실행)을 **하드 페일 게이트**로 검사해 shortcut을 막아라. (4) 스크립트는 `__file__` 기준으로 경로를 풀어라."
