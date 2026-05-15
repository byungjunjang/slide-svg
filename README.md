# slide-svg

> **네이티브 SVG × DrawingML 기반의 16:9 editable PPTX 생성기.**
> Claude Code 채팅창에 "AI 트렌드 강의 슬라이드 만들어줘"라고 한 줄만 입력하면,
> `/slide` 스킬이 1280×720 SVG 페이지를 직접 핸드크래프트 →
> 자체 DrawingML XML 라이터가 SVG를 PowerPoint 도형으로 1:1 번역 →
> `output/<주제>/<주제>.pptx`를 떨어뜨립니다.
> PowerPoint/Keynote에서 **도형 단위로 직접 편집** 가능한 진짜 네이티브 .pptx입니다 — 이미지 깔린 가짜 PPTX가 아닙니다.

![Theme](https://img.shields.io/badge/theme-Jangpm-4633E3)
![Viewport](https://img.shields.io/badge/viewport-1280%C3%97720-0b1f3a)
![Patterns](https://img.shields.io/badge/patterns-29-brightgreen)
![Stack](https://img.shields.io/badge/stack-Python%203.10%20%C2%B7%20python--pptx%20%C2%B7%20SVG%E2%86%92DrawingML-3776AB)
![Platform](https://img.shields.io/badge/platform-Claude%20Code-6b4bff)

<sub>📦 Based on <a href="https://github.com/hugohe3/ppt-master">hugohe3/ppt-master</a> · `/slide` 한국어 강의 덱 워크플로우 + Jangpm 디자인 시스템 + `/theme-init` 테마 교체 파이프라인 추가. Upstream MIT notice preserved in <a href="./LICENSE-ppt-master"><code>LICENSE-ppt-master</code></a>.</sub>

---

## 이게 뭔가요? (1분 요약)

- **무엇을 하는 도구:** 글로만 지시해도 컨설팅 리포트 스타일의 강의 슬라이드 덱을 자동으로 만들어주는 도구입니다. 결과물이 **이미지 PNG가 아니라 진짜 도형·텍스트·표**라서 PowerPoint에서 그대로 편집·발표할 수 있습니다.
- **누가 쓰면 좋은가:** 강사·기획자·임원·컨설턴트 — **PPT를 한 장씩 만들기 지겨운, 그리고 결과물을 PowerPoint에서 마저 손대고 싶은 누구나.**
- **어떻게 쓰는가:** Claude Code 안에서 `/slide` 또는 자연어로 요청하면 됩니다. 명령어 암기 불필요.
- **결과물:**
  - 네이티브 PPTX (`output/<주제>/<주제>.pptx`) — PowerPoint/Keynote/Google Slides에서 도형 단위로 편집
  - SVG 페이지 (`output/<주제>/svg_final/`) — 브라우저로 즉시 프리뷰
  - 스피커 노트 — 슬라이드별 자동 작성, PPTX에 임베드
  - Google Slides (`/upload-drive` 실행 시) — Drive 자동 업로드 + Slides 변환

**예시 한 줄:**
> "사내 AI 도입 효과 강의 슬라이드 12장 만들어줘. KPI 위주로."

↓ 2~5분 후 ↓

→ `output/사내-AI-도입/사내-AI-도입.pptx` 생성. 표지 → 챕터 → KPI 대시보드 →
사례 카드 → 로드맵 → 클로징 12장이 Jangpm 디자인 시스템(모노크롬 + accent `#4633E3`)으로
통일되어, **편집 가능한 네이티브 도형**으로 들어 있습니다.

---

## 디자인 시스템 — Jangpm

이 저장소의 활성 테마는 **Jangpm Slide Design System**입니다. 한 마디로:
**"맥킨지 표지처럼 임팩트, 본문은 미니멀 모노크롬, 강조는 단 한 가지 색."**

| 항목 | 값 |
|---|---|
| 캔버스 | **1280×720 (16:9)** 고정 — 테마 교체로도 바꿀 수 없음 |
| 폰트 | **Pretendard** (한글: Apple SD Gothic Neo / Malgun Gothic 폴백, 영문: Arial 최종 폴백) |
| 강조색 | **`#4633E3`** — 한 슬라이드당 1~2회만 사용 |
| accent-soft | `#E8E5FC` — 강조 카드 배경 |
| 모드 | **라이트 전용** (다크 배경 슬라이드 금지) |
| 카드 | 12px radius · 24px padding · 1px border |
| 그림자 | sparse (3단계). 데이터 강조 카드에만 |
| 아이콘 | Tabler outline 라인아트 (5000+종, stroke `currentColor`, 2px). **이모지·유니코드 장식 기호 금지** |
| Governing Message | 모든 콘텐츠 슬라이드 하단에 1줄 요약 (`.gm` 라인) |

**타이포 스케일 (시맨틱 클래스 우선):**

| 클래스 | 크기 | 굵기 | 용도 |
|---|---|---|---|
| `.display` | 56px | 800 | 커버·섹션 타이틀 |
| `.display-sm` | 40px | 800 | KPI 큰 숫자 |
| `.headline` | 32px | 700 | h2 (콘텐츠 슬라이드 헤딩) |
| `.title` | 18.4px | 600 | 카드 제목 |
| `.body` | 15.2px | 400 | 본문 |
| `.caption` | 12.8px | 500 | 라벨 / Governing Message |

> 시각 레퍼런스의 단일 진실 원천(SSOT)은 `.claude/skills/slide/references/theme-active.json`과
> `.claude/skills/slide/references/design-system.md`입니다.
> 다른 디자인 시스템으로 바꾸려면 → **`/theme-init`** 사용 (수동 편집 금지).

---

## 처음 설치하는 분을 위한 준비 (5분)

### 1단계. Claude Code 설치

[Claude Code 공식 다운로드](https://claude.com/claude-code) — Mac / Windows / Linux 모두 지원.

### 2단계. 이 저장소 클론

```bash
git clone https://github.com/byungjunjang/slide-svg.git ~/Desktop/slide-svg
cd ~/Desktop/slide-svg
```

### 3단계. Python 의존성 설치

Python 3.10 이상이 필요합니다. **한 번만** 다음을 실행:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
deactivate                          # 끝나면 닫아도 됨
```

이후엔 **`source .venv/bin/activate`를 매 세션 다시 칠 필요 없습니다.** `/slide` 스킬은 `.claude/skills/slide/scripts/_py.sh` 래퍼로 모든 파이썬 스크립트를 호출하는데, 이 래퍼가 `.venv/bin/python3`가 있으면 자동으로 그걸 쓰고 없으면 시스템 `python3`로 폴백합니다. 즉 venv는 만들어두기만 하면 됨.

> 루트의 `requirements.txt`는 단일 진실 원천(`.claude/skills/slide/requirements.txt`)을 가리키는 한 줄 래퍼입니다. 의존성 자체를 수정·추가할 때는 스킬 폴더 안쪽 파일을 고치세요.

대부분의 스크립트는 표준 라이브러리만 사용하지만, 다음은 필수입니다:

- `python-pptx` — SVG → PPTX 변환 본체
- `cairosvg` (또는 `svglib` + `reportlab`) — Office 호환을 위한 PNG 폴백 생성. macOS는 추가로 `brew install cairo`.
- `PyMuPDF`, `mammoth`, `markdownify` 등 — 소스 자료(PDF/DOCX/HTML) 임포트용
- `Pillow`, `numpy` — 이미지 처리
- `jsonschema` — `/theme-init` 토큰 검증
- `pytest` — 회귀 테스트용 (선택)

### 4단계. AI 이미지 생성 — `/codex-image` (기본값, API 키 불필요)

표지·인포그래픽에 AI 이미지가 필요할 때 `/slide` Step 5(Image_Generator)가 자동으로 호출하는 기본 경로입니다.
**API 키 발급·관리 없이 Codex CLI OAuth(ChatGPT 로그인)만으로** `gpt-image-2`를 호출합니다.

**최초 1회 준비 (한 번만 하면 됩니다):**

```bash
npm install -g @openai/codex      # Codex CLI 설치
codex login                        # ChatGPT 계정으로 OAuth 인증 (브라우저 자동 오픈)
codex login status                 # "Logged in using ChatGPT" 표시되면 끝
```

`codex login`은 OAuth 토큰을 `~/.codex/auth.json`에 한 번 저장하고, 이후 모든 이미지 호출은 그 토큰을 자동 재사용합니다.
**`sk-*` 형식 API 키는 어디에도 저장되지 않습니다.** Codex OAuth 토큰은 ChatGPT 세션 토큰이라 OpenAI REST API로 직접 던지면 401이 떨어지지만, `codex exec`의 내부 브릿지가 OAuth → 내장 `image_gen` 도구 → `gpt-image-2` 경로로 라우팅해줍니다.

`/slide` 외에 직접 호출하고 싶을 때는 Claude Code 채팅창에 그대로:

```
/codex-image cherry blossom hanok courtyard, golden afternoon light
/codex-image --size 1536x1024 --quality high aerial view of jeju coastline
```

| 증상 | 해결 |
|---|---|
| `auth expired` / 401 | `codex login` 재실행 (토큰 갱신) |
| `NOT_FOUND` | `npm install -g @openai/codex` |
| 트러스트 오류 | 스킬이 `--skip-git-repo-check` 사용 — 자세한 내용은 `.claude/skills/codex-image/README.md` |

**스킬 위치:** `.claude/skills/codex-image/` (이 저장소에 vendored. 업스트림: [wjb127/codex-image](https://github.com/wjb127/codex-image))
**비용:** ChatGPT Plus/Team/Enterprise 계정의 OpenAI 사용량에 청구 (`1024x1024 high` ≈ $0.04, `1024x1536 high` ≈ $0.06).

codex-image preflight(`codex login status`)가 실패하면 슬라이드는 **네이티브 도형 + SVG 일러스트**로만 생성됩니다 (Jangpm 기본 동작에서도 임팩트 있는 데크가 됩니다). 필요하면 프롬프트가 `images/image_prompts.md`에 그대로 남으므로 다른 도구로 직접 만들어 슬롯에 떨궈도 됩니다.

### 5단계. (선택) Google Drive 업로드

| 변환 종류 | 필요 도구 | 설치 |
|---|---|---|
| Google Slides 업로드 | `gws-drive-upload` 스킬 + Google 인증 | Claude Code Skills 안내 따라 인증 |

---

## 쓰는 법 — Claude Code 채팅창에 한 줄

### 가장 흔한 사용 패턴

이 저장소 폴더에서 Claude Code를 열고:

```
/slide AI 코딩 도구 도입 효과 발표 12장 만들어줘. KPI 중심으로.
```

또는 **슬래시 없이 자연어로**:

```
사내 발표용으로 우리 팀 AI 도입 효과 강의 슬라이드 만들어줘.
```

Claude는 자동으로 다음 단계를 직렬로 실행합니다 (`/slide` SKILL.md 정의):

1. **소스 자료 수집** — PDF / DOCX / URL / Markdown / 프롬프트 브리프를 먹여 `total.md` 한 권으로 통합
2. **프로젝트 초기화** — `output/<주제>/` 워크스페이스 생성, 활성 테마 자산 동기화
3. **Strategist (Eight Confirmations)** — 슬라이드 수, 패턴 배치, 톤 시퀀스, governing message 결정
4. **(선택) Image Generator** — 표지·인포그래픽용 AI 이미지 생성. `/codex-image` 스킬(Codex CLI OAuth → `gpt-image-2`, **API 키 불필요**)을 사용합니다 — 셋업은 위 "4단계" 참조.
5. **Executor** — 1280×720 SVG 페이지 N개 작성 + 스피커 노트 작성
6. **후처리** — `total_md_split.py` → `finalize_svg.py` (아이콘 임베드, 둥근사각형 변환, 텍스트 플래튼)
7. **PPTX export** — `svg_to_pptx.py <project> -s final`로 네이티브 DrawingML 생성

### 운영 체크 — WorkOS 3-pipeline 실행

`slide-svg`는 보통 가장 빨리 PPTX까지 도달하지만, 3개 파이프라인 작업에서는 `slide-svg` 성공만으로 전체 완료를 선언하지 않습니다.

- `preflight`: SVG 품질 검사기, `finalize_svg.py`, `svg_to_pptx.py`, notes split/export 스크립트 실행 가능성을 먼저 확인합니다.
- `content_ready`: `output/<주제>/svg_final/` 또는 동등한 최종 SVG 폴더에 계획한 장수만큼 페이지가 있어야 합니다.
- `built`: `svg_to_pptx.py <project> -s final` 또는 해당 export 스크립트가 성공해야 합니다.
- `verified`: PPTX가 존재하고 `unzip -t <deck>.pptx`가 성공해야 합니다.
- 병렬 worker가 hook 오류를 내거나 2분 이상 파일 변화 없이 정체하면, 같은 폴더에서 메인 세션이 즉시 이어받아 export와 검증을 끝냅니다.
- `slide-html`, `slide-pencil`의 완료/업로드 상태를 별도로 확인한 뒤 3-pipeline 전체 완료를 보고합니다.
- WorkOS 병렬 실행에서는 `pipeline_status.json` 또는 동등한 상태 파일에 `pipeline`, `project_slug`, `status`, `updated_at`, `planned_slide_count`, `actual_content_count`, `pptx_path`, `verification`, `blocked_reason`, `source_artifacts`를 남깁니다.

### 체계적인 데크는 `/slide-plan`을 먼저

8장이 넘거나 스토리 흐름이 중요한 데크(강의·임원 보고서·세일즈 데크 등)는 `/slide` 앞에 **`/slide-plan`을 먼저** 돌리면 결과 품질이 크게 올라갑니다.

```
/slide-plan AI 코딩 도구 도입 효과 발표 12장. 임원진 대상으로 KPI 위주.
```

`slide-plan`은 다음을 자동으로 결정합니다:
- **deck_type 감지** — educational / report / consulting / sales / internal_update / proposal / keynote
- **narrative arc** — deck_type별 권장 흐름 (예: report → exec_summary → context → findings → insight → cta)
- **슬라이드별 rationale** — `core_message`, `audience_takeaway`, `why_here`, layout family
- **차트의 수사적 역할** — growth-trend / forecast / focus-comparison / quadrant / split-segment / funnel ...
- **evidence 매핑** — 각 슬라이드 주장의 출처 추적

산출물은 `output/<주제>/slide_plan.json` + 한 화면짜리 markdown 요약. 사용자가 한 번 검토·확정한 뒤 `/slide`를 부르면 그 plan을 그대로 소비합니다 (Eight Confirmations 단계는 활성 테마 락 1-click 확인으로 단축).

> **간단한 데크는 그냥 `/slide`만** — 5~7장짜리 짧은 설명 슬라이드, 단일 소스 요약 같은 케이스는 `slide-plan` 없이도 충분합니다. `/slide`가 자동으로 standalone 모드로 동작합니다 (기존 흐름 그대로).

### 추가로 변환하기

```
/upload-drive          ← PPTX → Google Drive 업로드 + Slides 자동 변환
```

### 디자인 테마 자체를 바꾸고 싶으면

```
/theme-init            ← 활성 테마(Jangpm)를 새 디자인 시스템으로 일회성 교체
```

테마 가이드 마크다운을 사용자가 제공하면, 토큰 컨트랙트(v1)에 맞춰 `theme-active.json`을 만들고
`design-system.md`, `anti-slop-theme.md`, `strategist.md`, `executor.md`, `image-generator.md`,
`templates/layouts/<theme>/`, HTML 갤러리 CSS, `SKILL.md` THEME 블록 등 **모든 다운스트림 참조를 일괄 갱신**합니다.
PPTX는 export 시점에 토큰을 DrawingML로 굽기 때문에 런타임 멀티 테마는 불가능 — `/theme-init`는 **1회성 전체 교체**만 지원합니다.

---

## claude.ai에 단독 업로드하기

이 프로젝트는 외부 MCP 서버나 브라우저 바이너리에 의존하지 않아 스킬 폴더만 zip으로 묶어 claude.ai에 업로드할 수 있습니다. **번들 빌드는 헬퍼 스크립트로 한 줄**:

```bash
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/package_for_claude_ai.py
# → output/slide-skill-claude-ai.zip 생성 (약 196 파일, 2 MB)
```

이 zip을 claude.ai 스킬 업로더에 그대로 드래그하면 됩니다. 검증 사항(자동):
- 스킬 폴더 안에 중첩 `.zip`이 없을 것 (claude.ai의 새 검증 — "Zip cannot contain nested zip files" 차단)
- 파일 수 ≤ 200 (claude.ai 업로드 한도)

**듀얼 모드로 동작합니다 (자동 분기):**
- **Claude Code 로컬**: `embed_icons.py`가 외부 `assets/icons/` (Tabler 6000+ 풀 라이브러리)를 먼저 시도 → 모든 아이콘 정상 인라인. 성능 100%.
- **claude.ai 업로드**: 스킬 안에 동봉된 `templates/icons/tabler-outline/` essentials ~20개로 폴백. 이 외 아이콘은 `[WARN] Icon not found` + skip — 슬라이드는 빈 자리로 정상 완성.

번들에 포함되지 않는 것:
- 외부 `assets/icons/` 풀 라이브러리 (200-file 한도 초과로 의도적 제외)
- `assets/fonts/` Pretendard OTF (claude.ai에선 폰트 설치 권한 없음 — 데드웨이트라 기본 미동봉. `--include-fonts` 플래그로 옵트인 가능)
- **`/theme-init` 스킬** — 새 디자인 시스템 굽는 용도라 Claude Code 로컬 전용
- **`/upload-drive` 스킬** — Google Drive 인증 필요해 claude.ai 샌드박스 비호환

claude.ai 업로드 후 첫 사용 시 `pip install -r requirements.txt`로 Python 의존성 설치. 시스템 바이너리(`cairo`, `pandoc`)는 모두 **선택적** — 없어도 핵심 PPTX 빌드 흐름은 svglib + 순수 Python 경로로 동작합니다.

---

## 실전 가이드 — 폴더 정리 & 시나리오

### 폴더 정리 방법

```
slide-svg/
├── output/                       ← 완성물 (자동 생성, 주제명만 폴더로)
│   └── <주제명>/
│       ├── sources/              ← --move로 임포트된 원본 자료
│       ├── total.md              ← 통합 소스 (Strategist 입력)
│       ├── md_split/             ← 슬라이드별 markdown
│       ├── svg_output/           ← Executor 출력 (raw)
│       ├── svg_final/            ← 후처리 완료 SVG (브라우저 프리뷰용)
│       └── <주제명>.pptx         ← 네이티브 편집 가능 PPTX
└── ...
```

폴더 이름은 한글/영어 무관. `output/<주제>/` 안에서 모든 단계가 순차 산출되며, 각 단계 결과를 그대로 열어볼 수 있어 디버깅이 쉽습니다.

### 시나리오 A. 분기 사업 리뷰 강의

원본 자료를 `output/Q4-사업리뷰/sources/`에 넣어두거나 채팅에 직접 첨부:

```
4분기_재무.xlsx와 리스크_리스트.md 보고 Q4 사업 리뷰 강의 12장 만들어줘.
KPI 대시보드 한 장, 리스크는 매트릭스로, 결론은 투자 승인 요청.
```

### 시나리오 B. 사내 AI 도입 발표

```
사내 AI 도입 성과 발표 10장. 이미지 표지 + 도입 전후 비교 +
KPI 4개 + 사례 6개 + 로드맵 + 클로징.
```

### 시나리오 C. 숫자만 있고 스토리는 모를 때

```
5년_매출.csv만 보고 핵심 메시지 5장으로 뽑아줘. 추세, 변곡점, 이상치 중심.
```

### 시나리오 D. 외부 자료가 출발점일 때

URL / PDF / DOCX를 던지면 그대로 흡수합니다:

```
https://example.com/research.pdf 이거 보고 강의 슬라이드 8장으로 정리해줘.
```

### 결과가 마음에 안 들면 바로 수정

```
슬라이드 4를 KPI 대시보드 패턴(20-kpi-dashboard)으로 바꿔줘. 전년 대비 화살표 포함.
```

```
슬라이드 7의 세 번째 카드를 accent로 바꿔줘 (시선 앵커).
```

```
전체적으로 카드 그림자 다 빼고, 그라디언트 잔존하는 거 있으면 제거.
```

```
영문판도 같이 만들어줘. 구조·숫자는 동일하게.
```

대화하듯 계속 다듬을 수 있습니다 — Executor는 페이지를 한 번에 한 장씩 다시 그립니다.

---

## 자주 묻는 질문

**Q. 결과물이 이미지가 박힌 PPT 아니라, 진짜 편집되는 거 맞아요?**
A. 네. SVG → DrawingML 직변환이라 도형·텍스트·표가 PowerPoint 네이티브 객체로 들어갑니다. 색을 바꾸고 박스를 옮기고 글자를 고치는 모든 동작이 일반 PPT처럼 동작합니다. 이미지 임베드 폴백은 명시적 옵션일 때만 발동합니다.

**Q. 디자인 색상·폰트를 우리 회사 브랜드로 바꾸고 싶어요.**
A. `/theme-init`을 쓰세요. 디자인 가이드 마크다운을 주면 `theme-active.json`(토큰 컨트랙트 v1)을 만들고, `design-system.md`·`anti-slop-theme.md`·`strategist.md`·`executor.md`·`image-generator.md`·`templates/layouts/<theme>/`·HTML 갤러리 CSS·`SKILL.md` THEME 블록까지 모든 다운스트림 참조를 일괄 갱신합니다. 수동 편집은 금지 — 어긋나면 슬라이드가 일관성을 잃습니다.

**Q. 슬라이드 개수를 지정할 수 있나요?**
A. 네. "10장으로", "15슬라이드짜리"라고 말하면 그대로 만듭니다. 미지정 시 주제 분량에 맞게 4장 이상으로 자동 결정.

**Q. 영어 덱도 만들 수 있나요?**
A. 네. 한국어로 요청하면서 "영문으로 만들어줘"라고 하거나, 영어로 요청하면 영어 덱이 나옵니다. Pretendard 폰트 체인 그대로, 한글이 없으면 자동으로 Arial 폴백을 탑니다.

**Q. 완성된 PPTX를 직접 편집할 수 있나요?**
A. 네, 일반 `.pptx` 파일이라 PowerPoint/Keynote/Google Slides에서 자유롭게 편집·발표 가능합니다. 사내 발표 직전 슬라이드 한두 장만 직접 손보는 워크플로우가 가장 흔합니다.

**Q. 폰트가 깨질 수도 있나요?**
A. Pretendard가 설치되어 있지 않은 환경에서는 폰트 체인에 따라 Apple SD Gothic Neo → Malgun Gothic → Arial 순으로 폴백됩니다. 어디서 열어도 깨지진 않지만, 정확히 동일한 모양을 보장하려면 `assets/fonts/` 디렉터리의 Pretendard OTF를 PPTX와 함께 배포하세요.

**Q. 기밀 데이터인데 안전한가요?**
A. 파일은 모두 로컬에서 처리됩니다. 단, Claude와의 대화 내용은 AI 응답을 받기 위해 Anthropic 서버로 전달됩니다. 회사 보안 정책에 따라 판단하세요. AI 이미지 생성 백엔드(Gemini/OpenAI)는 명시적 설정 시에만 활성화됩니다.

**Q. 이전 슬라이드 덱을 삭제하지 않고 보존할 수 있나요?**
A. 네. `output/<주제>/`는 주제별로 폴더가 분리되어 있어 그대로 두면 보존됩니다. 디스크가 무거워지면 `svg_output/` 같은 중간 산출물만 지워도 됩니다 (`.pptx`와 `svg_final/`만 남기면 충분).

---

## 어떤 슬라이드 패턴을 만들어주나요? — 29개 Jangpm 패턴

Claude가 자동으로 골라주지만, 직접 지정하고 싶으면 패턴 ID로 부르면 됩니다.
패턴 HTML 원본은 `.claude/skills/slide/references/jangpm-patterns/`에 있습니다 (활성 테마 CSS로 reskin됨).

### 표지·구조 슬라이드
- **01-title** — 메인 표지 (큰 제목 + 부제 + 메타데이터)
- **13-cover-vertical** — 세로형 표지 (이미지 강한 슬라이드용)
- **02-agenda** — 목차
- **03-section** — 섹션 구분 (큰 번호 + 섹션 타이틀)
- **11-summary** — 요약 슬라이드
- **12-closing** — 클로징
- **21-closing-big** — 큰 한 줄 클로징

### 그리드 카드 (고밀도 패턴 — 콘텐츠의 30% 이상 의무)
- **04-three-point** — 3분할 카드
- **04b-four-point** — 4분할 카드
- **07b-six-point** — 6분할 카드
- **15-matrix-trends** — 트렌드 매트릭스
- **20-kpi-dashboard** — KPI 4~8개 타일

### 데이터·테이블 패턴
- **06-stats** — 큰 숫자 + 본문
- **07-table** — 비교 테이블
- **16-forecast-table** — 실적 + 전망 테이블
- **17-pnl** — 손익 테이블
- **18-seasonal** — 계절성 차트형 테이블

### 비교·프로세스
- **05-comparison** — 좌우 비교 (Before/After, Option A/B)
- **09-process** — 프로세스 흐름도 (3~6단계)
- **19-paired-concept** — 짝개념 카드

### 진행·체크리스트
- **10-checklist** — 체크리스트
- **08a-exercise-1up** — 실습 슬라이드 (1단)
- **08b-exercise-2up** — 실습 슬라이드 (2단)

### 이미지·인용
- **08-quote** — 인용 슬라이드
- **22-image-1up** — 이미지 1장 풀폭
- **23-image-2up** — 이미지 2장
- **14-overview-split** — 좌우 분할 (이미지 + 본문)

### 데모·기술 콘텐츠
- **24-terminal-split** — 터미널 + 설명 분할
- **25-terminal-full** — 터미널 풀스크린

> **다양성 룰:** 연속 동일 패턴 금지(section 예외), 8장 이하 → 3종 이상, 10장 이상 → 4종 이상, 고밀도 grid 패턴은 콘텐츠의 30% 이상.

---

## 저장소 구조

```
slide-svg/
├── .claude/
│   └── skills/
│       ├── slide/                       ← /slide 스킬 (활성 테마 기반 슬라이드 생성)
│       │   ├── SKILL.md                 ← 직렬 파이프라인 정의 (실행 규율 락)
│       │   ├── requirements.txt
│       │   ├── references/
│       │   │   ├── theme-active.json    ← 활성 테마 스펙 (토큰 컨트랙트 v1)
│       │   │   ├── design-system.md     ← 디자인 시스템 (테마별 재생성)
│       │   │   ├── anti-slop-core.md    ← 18 구조적 금지 패턴 (테마 불가지)
│       │   │   ├── anti-slop-theme.md   ← 테마 리터럴 락 (테마별 재생성)
│       │   │   ├── strategist.md        ← Eight Confirmations
│       │   │   ├── executor.md          ← 단일 executor (SVG 생성 규칙)
│       │   │   ├── image-generator.md   ← 활성 테마 일러스트 레시피
│       │   │   ├── export.md            ← svg_to_pptx 파이프라인
│       │   │   ├── shared-standards.md  ← SVG 기술 제약
│       │   │   ├── canvas-formats.md    ← 1280×720 전용
│       │   │   ├── patterns.md          ← 30+ 레이아웃 패턴 레지스트리
│       │   │   ├── jangpm-patterns/     ← 29개 패턴 HTML (시각 레퍼런스 갤러리)
│       │   │   └── ... (libraries, visual-assets, skeleton, …)
│       │   ├── scripts/                 ← 22개 파이썬 도구
│       │   │   ├── source_to_md/        ← PDF/DOCX/HTML/URL → markdown
│       │   │   ├── total_md_split.py    ← 통합 md → 슬라이드별 분할
│       │   │   ├── finalize_svg.py      ← 아이콘 임베드 + 둥근사각형 변환 + 텍스트 플래튼
│       │   │   ├── svg_to_pptx.py       ← SVG → DrawingML PPTX
│       │   │   ├── svg_quality_checker.py
│       │   │   ├── project_manager.py
│       │   │   └── dev/                 ← 내부 유틸 (batch_validate, generate_examples_index, …)
│       │   ├── templates/
│       │   │   ├── layouts/jangpm/      ← 활성 테마 레이아웃 팩 (cover/chapter/content/ending + design_spec)
│       │   │   ├── charts/              ← 54개 차트 SVG (사용 시점에 활성 테마 토큰으로 오버라이드)
│       │   │   └── icons/tabler-outline/ ← claude.ai essentials ~20개 (Claude Code는 외부 assets/icons/ 사용)
│       │   └── workflows/               ← create-template, topic-research
│       ├── theme-init/                  ← 활성 테마 일회성 교체
│       └── upload-drive/                ← PPTX → Google Drive + Slides 변환
│
├── assets/
│   ├── fonts/                           ← 공유 폰트 풀 (Pretendard 9 OTF + variable)
│   └── icons/                           ← Tabler 풀 라이브러리 (outline 5000+ · filled 1000+ · icons_index.txt). Claude Code 전용 — claude.ai 업로드 번들엔 의도적으로 제외
│
├── output/                              ← 빌드 결과물 (주제별 폴더)
│   └── <주제명>/
│       ├── total.md, md_split/, sources/
│       ├── svg_output/, svg_final/
│       └── <주제명>.pptx
│
├── tests/                               ← theme-init 회귀 테스트 (pytest)
├── docs/
│   ├── faq.md                           ← 알려진 이슈 + 해결책
│   ├── technical-design.md              ← 파이프라인 기술 설계
│   └── solutions/                       ← /reflect 학습 기록 (sol-YYYYMMDD-NNN.md)
│
├── CLAUDE.md                            ← 에이전트용 HARD RULES + 프로젝트 SSOT
├── README.md                            ← (이 파일)
├── LICENSE                              ← MIT (Byungjun Jang)
├── LICENSE-ppt-master                   ← 업스트림 ppt-master MIT 고지 (의무 보존)
└── .env.example
```

---

## 핵심 제약 (HARD RULES)

`CLAUDE.md`에 정의된 위반 금지 규칙. 슬라이드 작성 시 매 슬라이드마다 자기 점검합니다. **테마를 바꿔도 이 규칙들은 그대로**입니다.

- **C1. 1280×720 전용** — 다른 캔버스 포맷 지원 안 함. 테마 교체로도 바꿀 수 없음.
- **C2. 단일 액센트 원칙** — 활성 테마의 `colors.accent` **하나만** 사용. 멀티 휴 / 그라디언트 / 글로우 / 레인보우 금지.
- **C3. Governing Message 의무** — 커버/챕터/클로징 외 모든 콘텐츠 슬라이드 하단에 `.gm` 한 줄 필수. 타이틀 재진술이 아니라 편집적 "so-what" 문장.
- **C4. 이모지 금지** — 아이콘은 활성 테마의 Tabler outline 라인아트 (2px stroke)만. `→`, `✓`, `★` 같은 유니코드 장식 기호도 금지.
- **C5. 네이티브 SVG → PPTX** — 이미지 플래튼 금지, 편집 가능한 도형 유지. 명시적 폴백 옵션일 때만 PNG 임베드.
- **C6. 직렬 실행** — strategist → [image_generator] → executor → post-processing → export. 교차 병합 금지.
- **C7. 메인 에이전트 단독 SVG 생성** — Executor Step 6은 sub-agent에 위임 금지 (`SKILL.md §Global Execution Discipline #6`).
- **C8. 순차 페이지 생성** — 한 번에 한 페이지씩, 그룹 배치 금지.
- **C9. 라이트 모드 전용** — 모든 슬라이드(커버·클로징 포함) 루트 배경은 `bg` 또는 `surface` 토큰. 다크 배경 금지.

**SVG 기술 제약 요약** (`shared-standards.md` 전체 규격):

- **금지**: `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate>`, `mask`, `<script>`
- **PPT 호환 대체**: `rgba(…)` → `fill-opacity` / `stroke-opacity`; `<g opacity>` → 요소별 opacity
- **텍스트**: 모든 `<text>`에 Pretendard 풀 체인 (`Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", Arial, sans-serif`)
- **아이콘**: `<use data-icon="tabler-outline/<name>" stroke="currentColor" stroke-width="2"/>` 플레이스홀더 — `finalize_svg.py`가 임베드

**후처리 규율** (`SKILL.md §Step 7`):

1. **`cp` 금지** — `finalize_svg.py` 대신 파일 복사로 끝내지 말 것 (아이콘 임베드/이미지 크롭/텍스트 플래튼/둥근사각형 변환을 건너뜀).
2. **단일 블록 금지** — `total_md_split.py`, `finalize_svg.py`, `svg_to_pptx.py` 세 스크립트는 **각각 별도의 bash 호출**로 순차 실행.
3. **`-s final` 필수** — `svg_to_pptx.py <project> -s final`. `svg_output/`에서 직접 export 하면 후처리를 건너뜀.

자세한 내용은 `CLAUDE.md` 및 `.claude/skills/slide/SKILL.md` 참조.

---

## 학습된 사고 사례 (Past Learnings)

`/reflect` 스킬로 누적된 회고 — 같은 실수를 반복하지 않기 위해 자동 로드됩니다.

- **sol-20260423-001** — `is_cjk_char`에 한글(Hangul) 범위가 누락되어 PPTX 텍스트박스 폭이 좁게 계산되던 버그. 한글 포함 폭 계산 규칙은 `docs/solutions/bug-fix/`에 기록.
- **sol-20260423-002** — Jangpm 레이아웃 "Breath Over Symmetry": 최장 문장 기준 column 수 선택 + 제목 줄바꿈 금지. 패턴 회귀의 첫 번째 체크.
- **sol-20260423-003** — Layer-separated debugging: 사용자가 "여전하다"고 하면 source → SVG → PPTX → viewer 레이어를 분리 검증 (한 레이어씩 산출물을 직접 열어볼 것).

전체 기록: `docs/solutions/<category>/<id>.md`

---

## 빌드 & 개발

```bash
pip install -r requirements.txt                              # 의존성 설치 (한 번만, 루트 wrapper)

# 일반 사용은 /slide 스킬을 통해 자동 실행되지만, 단계별 수동 실행도 가능:
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/project_manager.py init <project_name> --format ppt169
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/source_to_md/pdf_to_md.py <file.pdf>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/total_md_split.py <project_path>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/finalize_svg.py <project_path>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/svg_to_pptx.py <project_path> -s final

# 로컬 SVG 프리뷰 서버 (브라우저로 svg_final/ 확인)
python3 -m http.server -d <project_path>/svg_final 8000

# 회귀 테스트 (theme-init 파이프라인)
pytest tests/
```

---

## 자매 프로젝트

이 저장소는 **WorkOS 슬라이드 3대 파이프라인** 중 하나입니다. 같은 주제로 세 가지 다른 결과물을 동시에 만들 수 있습니다.

| 프로젝트 | 입력 → 출력 | 강점 |
|---|---|---|
| **slide-svg** (이 저장소) | 자연어 → SVG → 네이티브 DrawingML PPTX | 파워포인트 네이티브 편집성, 도형 단위 정밀도, 한글 강의 톤 |
| **slide-pencil** | 자연어 → Pencil → React/Tailwind → HTML/PPTX/PDF | 디자인 일관성, 시각 레퍼런스 기반, 토큰 컨트랙트 |
| **slide-html** | 자연어 → Reveal.js HTML | 발표 인터랙션, 트랜지션, 단일 HTML로 즉시 발표 |

WorkOS 루트에서 "슬라이드 만들어줘"라고 요청하면 3개를 병렬 실행합니다.

---

## 라이선스 & 기여

본 프로젝트는 **MIT 라이선스**입니다 — [`LICENSE`](./LICENSE) 참조.
[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) (동일 MIT)의 상당 부분을 포함하며, MIT의 저작자 표시 조항에 따라 업스트림 고지는 [`LICENSE-ppt-master`](./LICENSE-ppt-master)에 그대로 보존되어 있습니다.

- **버그 리포트·패턴 제안:** GitHub 이슈 환영
- **PR:** 디자인 시스템 추가, 패턴 추가, 회고 기록 환영
- **테마 교체 제안:** `/theme-init` 사용법은 `.claude/skills/theme-init/SKILL.md` 참조

---

<details>
<summary>개발자용 (스킬 내부 구조 · 토큰 컨트랙트 · 변환 파이프라인)</summary>

### 토큰 컨트랙트 v1

`.claude/skills/theme-init/references/token-contract.json`에 정의된 키들은 **테마와 무관하게 항상 같은 의미**로 유지되어야 합니다. `theme-active.json`이 이 스키마를 만족해야 `/theme-init`가 통과됩니다.

| 카테고리 | 키 | 의미 |
|---|---|---|
| colors | `bg`, `surface`, `surface-alt` | 페이지·카드 배경 (3단계) |
| colors | `text`, `text-secondary`, `text-tertiary` | 본문·보조·보조보조 텍스트 |
| colors | `border`, `border-strong` | 카드·디바이더 테두리 (2단계) |
| colors | `accent`, `accent-soft`, `accent-ink` | 강조색 + 강조 카드 배경 + 강조 위 텍스트 |
| colors | `positive`, `negative`, `warning` (+`-soft`) | 시멘틱 신호색 |
| typography | `font-chain`, `display`, `display-sm`, `headline`, `title`, `body`, `caption`, `label` | 폰트 체인 + 7단계 스케일 |
| radius | `xs/sm/md/lg/xl/pill` | 6단계 코너 |
| stroke | `icon/divider/emphasis` | 라인 두께 |
| spacing | `1`~`16` | 4px 베이스 스케일 |

`/theme-init`은 이 키 이름을 유지한 채 **값만** 새 테마로 교체합니다.

### `/theme-init`이 건드리는 다운스트림 참조 (전부 일괄 갱신)

1. `.claude/skills/slide/references/theme-active.json` — 토큰 값 자체
2. `.claude/skills/slide/references/design-system.md` — 디자인 시스템 페이지 (template은 `design-system.tpl.md`)
3. `.claude/skills/slide/references/anti-slop-theme.md` — 테마 리터럴 락 (template은 `anti-slop-theme.tpl.md`)
4. `.claude/skills/slide/references/strategist.md` / `executor.md` / `image-generator.md` — 활성 테마 락된 에이전트 정의
5. `.claude/skills/slide/templates/layouts/<theme>/` — 레이아웃 팩 + design_spec.md + assets/
6. `.claude/skills/slide/references/jangpm-patterns/` HTML 갤러리 CSS — 활성 테마 토큰으로 reskin
7. `.claude/skills/slide/SKILL.md` — `<!-- THEME:START -->` ~ `<!-- THEME:END -->` 블록
8. `assets/fonts/` 스캔 → 활성 테마의 primary 폰트가 없으면 Arial로 폴백 결정 (런타임)

### `/slide` 직렬 파이프라인

```
Step 1: 소스 수집 (Bash + source_to_md/)
  ├─ PDF → pdf_to_md.py (PyMuPDF)
  ├─ DOCX → doc_to_md.py (mammoth)
  ├─ URL → web_to_md.py (requests/curl_cffi + BS4)
  └─ project_manager.py import-sources <project> <files…> --move

Step 2: 프로젝트 초기화 (project_manager.py init)
  └─ output/<project>/ 생성, 활성 테마 자산 동기화

Step 3: Strategist (LLM, references/strategist.md)
  ├─ Eight Confirmations
  ├─ 슬라이드 수 + 패턴 배치 + 톤 시퀀스
  └─ governing message 초안

Step 4: (선택) Image Generator (/codex-image)
  ├─ Codex CLI OAuth → gpt-image-2 (API 키 불필요)
  └─ 표지·인포그래픽 일러스트 생성 — Jangpm Style Lock 자동 prepend

Step 5: Executor (LLM, references/executor.md)
  ├─ 페이지별 SVG 작성 (1280×720, shared-standards.md 준수)
  ├─ 메인 에이전트 단독 (sub-agent 위임 금지)
  └─ 한 번에 한 페이지씩 순차 (그룹 배치 금지)

Step 6: 후처리 (각각 별도 bash 호출)
  ├─ total_md_split.py <project>          ← 통합 md → 슬라이드별 분할
  ├─ finalize_svg.py <project>            ← 아이콘 임베드, 둥근사각형 변환, 텍스트 플래튼, 이미지 크롭
  └─ svg_quality_checker.py (선택, 회귀 검사)

Step 7: PPTX export
  └─ svg_to_pptx.py <project> -s final    ← svg_final/에서 DrawingML 생성 (-s final 필수)
```

### SVG 페이지 안에 들어가는 것들

- **shapes**: `<rect>`, `<circle>`, `<line>`, `<path>` — DrawingML로 직변환되는 네이티브 도형
- **text**: 모든 `<text>`에 Pretendard 풀 체인. h2는 `.headline` (32/700), 카드 제목은 `.title` (18.4/600)
- **icons**: `<use data-icon="tabler-outline/<name>" stroke="currentColor" stroke-width="2"/>` — `finalize_svg.py`가 인라인 SVG path로 치환
- **rounded rects**: `rx`/`ry` 그대로 두면 후처리에서 둥근사각형 도형으로 변환
- **images**: `<image>` 태그로 PPTX에 임베드. AI 이미지는 `/codex-image`가 떨군 `images/<slot>.png`를 참조
- **차트**: `templates/charts/` 54종에서 활성 테마 토큰으로 색만 오버라이드

### Tech Stack

```
Python 3.10+
python-pptx >= 0.6.21      ← SVG → DrawingML 본체
cairosvg / svglib           ← Office 호환 PNG 폴백
PyMuPDF, mammoth, markdownify ← 소스 임포트
Pillow, numpy               ← 이미지 처리
jsonschema                  ← /theme-init 토큰 검증
pytest                      ← 회귀 테스트

(AI 이미지 생성은 `/codex-image` 스킬이 담당 — Node 기반 Codex CLI를 사용하므로 Python SDK 의존성 없음.)
```

### 주요 경로 한눈에

```
.claude/skills/slide/SKILL.md                          ← /slide 스킬 정의 (직렬 파이프라인 락)
.claude/skills/slide/references/theme-active.json      ← 활성 테마 스펙
.claude/skills/slide/references/design-system.md       ← 활성 디자인 시스템
.claude/skills/slide/references/anti-slop-core.md      ← 18 구조적 금지 패턴 (테마 불가지)
.claude/skills/slide/references/anti-slop-theme.md     ← 테마 리터럴 락 (테마별 재생성)
.claude/skills/slide/references/jangpm-patterns/       ← 29개 패턴 HTML 갤러리
.claude/skills/slide/scripts/finalize_svg.py           ← 후처리 본체
.claude/skills/slide/scripts/svg_to_pptx.py            ← SVG → DrawingML
.claude/skills/theme-init/SKILL.md                     ← 테마 일괄 교체
.claude/skills/upload-drive/SKILL.md                   ← Drive + Slides 변환
docs/faq.md                                            ← 알려진 이슈 + 해결책
docs/technical-design.md                               ← 파이프라인 기술 설계
docs/solutions/                                        ← /reflect 회고 기록
```

</details>
