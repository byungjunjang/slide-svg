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

**예시 한 줄:**
> "사내 AI 도입 효과 강의 슬라이드 12장 만들어줘. KPI 위주로."

↓ 2~5분 후 ↓

→ `output/사내-AI-도입/사내-AI-도입.pptx` 생성. 표지 → 챕터 → KPI 대시보드 →
사례 카드 → 로드맵 → 클로징 12장이 Jangpm 디자인 시스템(모노크롬 + accent `#4633E3`)으로
통일되어, **편집 가능한 네이티브 도형**으로 들어 있습니다.

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

codex-image preflight(`codex login status`)가 실패하면 **AI 이미지 슬롯이 필요한 덱은 HALT**하고 `codex login`을 안내합니다. 이미지 슬롯이 없는 덱만 네이티브 도형 + SVG 다이어그램으로 계속 진행할 수 있습니다. placeholder, 단색 이미지, 다른 이미지 백엔드로 silent fallback 하지 않습니다.

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

claude.ai 업로드 후 첫 사용 시 `pip install -r requirements.txt`로 Python 의존성 설치. 시스템 바이너리(`cairo`, `pandoc`)는 모두 **선택적** — 없어도 핵심 PPTX 빌드 흐름은 svglib + 순수 Python 경로로 동작합니다.

---

## Dual-host: Claude Code · Codex

This repo runs on both Claude Code and Codex (cloud/web).

- **Claude Code** loads `.claude/skills/` via its Skill runtime (canonical, unchanged).
- **Codex** reads root `AGENTS.md`, which routes slide requests through the
  generated `.codex/skills/` mirror and enforces the same pipeline + gates.

`.claude/skills/` is the single source of truth. `.codex/skills/` is generated —
**never hand-edit it.** The mirror root includes `_GENERATED.md` as a reminder.
After editing any skill, regenerate the mirror:

    .claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py

Quality gates (run on either host):

    # before starting a deck
    .claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/preflight.py --needs-images
    # before declaring a deck done
    .claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/verify_deck.py output/<project>

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
A. 파일은 모두 로컬에서 처리됩니다. 단, Claude와의 대화 내용은 AI 응답을 받기 위해 Anthropic 서버로 전달됩니다. 회사 보안 정책에 따라 판단하세요. AI 이미지 생성은 `/codex-image` 스킬(Codex CLI OAuth → gpt-image-2) 단일 경로로만 수행되며, 다른 백엔드(Gemini/OpenAI/DALL·E/Midjourney 등)는 사용하지 않습니다.

**Q. 이전 슬라이드 덱을 삭제하지 않고 보존할 수 있나요?**
A. 네. `output/<주제>/`는 주제별로 폴더가 분리되어 있어 그대로 두면 보존됩니다. 디스크가 무거워지면 `svg_output/` 같은 중간 산출물만 지워도 됩니다 (`.pptx`와 `svg_final/`만 남기면 충분).

---

## 라이선스 & 기여

본 프로젝트는 **MIT 라이선스**입니다 — [`LICENSE`](./LICENSE) 참조.
[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) (동일 MIT)의 상당 부분을 포함하며, MIT의 저작자 표시 조항에 따라 업스트림 고지는 [`LICENSE-ppt-master`](./LICENSE-ppt-master)에 그대로 보존되어 있습니다.

- **버그 리포트·패턴 제안:** GitHub 이슈 환영
- **PR:** 디자인 시스템 추가, 패턴 추가, 회고 기록 환영
- **테마 교체 제안:** `/theme-init` 사용법은 `.claude/skills/theme-init/SKILL.md` 참조
