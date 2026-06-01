# slide-svg

## Source of Truth

**This file is the project SSOT.** Before any slide task, read `.claude/skills/slide/SKILL.md` for the full workflow and execution rules. If another skill's conventions conflict with this document, this document wins.

## 개요

`ppt-master`의 네이티브 DrawingML SVG→PPTX 파이프라인 위에 **활성 테마 디자인 시스템**을 단일 시각언어로 락하는 한국어 강의 슬라이드 생성기. 1280×720, 편집 가능한 네이티브 도형, 모든 콘텐츠 슬라이드 하단에 `.gm` (governing message) 라인. 활성 테마는 `references/theme-active.json`이 결정하며 `/theme-init`로 교체 — 기본 테마는 **Jangpm** (모노크롬 + 단일 `#4633E3` 인디고 액센트, Pretendard).

**듀얼 모드 (Claude Code · claude.ai)**: 외부 MCP 서버, 브라우저 바이너리, 다른 스킬 폴더 참조 없음. 핵심 PPTX 빌드(`finalize_svg.py` + `svg_to_pptx.py`)는 100% 순수 Python (`python-pptx` + 자체 DrawingML XML 라이터). 시스템 바이너리(`cairo`, `pandoc`)는 모두 선택적이며 없으면 svglib + reportlab 경로로 자동 폴백.

- **Claude Code 로컬**: 풀 라이브러리 모드. `.claude/skills/slide/` + 외부 `assets/icons/` (Tabler 6000+) + `assets/fonts/` (Pretendard) 모두 사용. 성능·완성도 100%.
- **claude.ai 업로드**: essentials 모드. `.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/package_for_claude_ai.py`로 묶은 `output/slide-skill-claude-ai.zip`을 업로더에 드래그. 외부 `assets/icons/`는 번들에 포함 안 됨 — 스킬 안에 동봉된 ~20개 essentials 아이콘만 인라인되고 그 외는 graceful skip(`[WARN] Icon not found`). 폰트는 기본 미동봉 (claude.ai 환경엔 폰트 설치 권한 없어 데드웨이트). `/theme-init`은 새 디자인을 굽는 용도라 Claude Code 로컬 전용, `/upload-drive`는 Google 인증 필요해 로컬 전용.

**듀얼 호스트 (Claude Code · Codex)**: Codex(클라우드/웹)는 루트 `AGENTS.md`를 읽어 생성형 `.codex/skills` 미러로 같은 파이프라인을 실행한다. `.claude/skills`가 정본이고 `.codex/skills`는 `sync_codex_mirror.py` 생성물이므로 손으로 편집하지 말 것.

## 핵심 제약 (non-negotiable)

다음 제약은 **테마에 관계없이 영구 락**이다. 테마를 바꿔도 이 규칙들은 그대로 적용된다.

- **1280×720 전용** — 다른 캔버스 포맷 지원 안 함. 테마 교체로도 바꿀 수 없음
- **단일 액센트 원칙** — 활성 테마의 `colors.accent` 하나만 사용, 멀티 휴 / 그라디언트 / 글로우 / 레인보우 금지 (현재 테마 기본값: `#4633E3`)
- **모든 콘텐츠 슬라이드 하단에 `.gm` (governing message) 한 줄** — 편집적 "so-what", 타이틀 재진술 아님. 테마별 voice 규정은 `anti-slop-theme.md` 참고
- **이모지 금지** — 아이콘은 활성 테마 `assets.icon-pack-default`의 2px 라인아트만 (현재: `tabler-outline`)
- **네이티브 SVG→PPTX 파이프라인** — 이미지 플래튼 금지, 편집 가능한 도형 유지
- **직렬 실행** — strategist → [image_generator] → executor → post-processing → export. 교차 병합 금지
- **메인 에이전트 단독 SVG 생성** — Executor Step 6은 sub-agent에 위임 금지 (SKILL.md §Global Execution Discipline #6)
- **순차 페이지 생성** — 한 번에 한 페이지씩, 그룹 배치 금지 (#7)
- **활성 테마 = 단일 시각언어** — PPTX가 export 시점에 토큰을 DrawingML로 굽기 때문에 런타임 멀티 테마 불가능. `/theme-init`는 1회성 전체 교체만 지원 (`.claude/skills/theme-init/SKILL.md`)
- **plan/render 분리 (선택적)** — 체계적인 데크는 `/slide-plan`이 `slide_plan.json`을 먼저 만들고 `/slide`가 그 plan을 소비. 간단한 데크는 `/slide`만으로도 동작 (Standalone 모드 — 기존 Eight Confirmations 흐름 그대로). 두 모드는 같은 `/slide` 파이프라인 안에서 자동 분기.

## 스킬

| 스킬 | 트리거 | 위치 |
|------|--------|------|
| `/slide` | `"슬라이드 만들어"`, `"강의 슬라이드"`, `"프레젠테이션"`, `"make slides"`, `"/slide"`, `"생성PPT"` | 핵심 파이프라인 |
| `/slide-plan` | `"기획부터"`, `"체계적으로 슬라이드"`, `"narrative 짜줘"`, `"/slide-plan"` | 선택적 강화 단계 — `/slide` 이전에 실행 |
| `/theme-init` | `"테마 교체"`, `"디자인 시스템 바꿔"`, `"새 브랜드 적용"`, `"change the design system"`, `"replace the theme"` | 활성 테마 1회성 교체 |

스킬 정의:
- `/slide`: `.claude/skills/slide/SKILL.md` — Step 4에서 `slide_plan.json` 존재 시 plan-consuming 모드, 부재 시 Eight Confirmations 모드로 자동 분기
- `/slide-plan`: `.claude/skills/slide-plan/SKILL.md` — deck_type 감지 + narrative arc + 슬라이드별 rationale + 차트 수사적 역할 + Layer 1 R1–R5 검증 (`scripts/validate_plan.py`). 출력: `output/<project>/slide_plan.json`
- `/theme-init`: `.claude/skills/theme-init/SKILL.md` (활성 테마 전체 교체; 에이전트가 디자인 가이드를 직접 추출 → fill-nulls → 토큰 검증 → 전 참조 파일 재생성 + `templates/layouts/<theme>/DESIGN.md` skeleton 생성 → 에이전트가 `<!-- AGENT-FILL -->` 마커 채워 완성 → **Step 5 Shell Composition**(선택): 에이전트가 baseline 셸을 레퍼런스로 좌표·정렬·장식·내러티브 밴드를 `_shell_src/*.tpl.svg`로 재작곡 → render-first 프리뷰로 사용자 피드백 루프 → `validate_shells.py` 락 검사 → 사용자 검토 BLOCKING; API key 불필요, jsonschema만 필요; 캔버스 1280×720은 테마 간 영구 락; 라이트 완화는 내러티브 셸 밴드까지만 — content 셸은 라이트 유지)

## 사용 패턴

```
간단:  /slide                                 (8 슬라이드 미만, 단일 소스)
체계: /slide-plan → 사용자 검토 → /slide      (강의·임원 보고서·세일즈 데크)
```

`/slide`는 두 패턴 모두 자동 처리. `slide_plan.json`이 `output/<project>/`에 있으면 plan-consuming, 없으면 Standalone.

## 디렉터리

```
slide-svg/
├── CLAUDE.md                          ← 이 파일 (SSOT)
├── README.md                          ← 짧은 프로젝트 README
├── LICENSE                            ← 프로젝트 MIT (Byungjun Jang)
├── LICENSE-ppt-master                 ← 업스트림 ppt-master MIT 고지 (MIT 의무 보존)
├── LICENSE-diagram-design             ← 업스트림 diagram-design MIT 고지 (벤더링; MIT 의무 보존)
├── .gitignore
├── .claude/
│   ├── settings.json                  ← 스크립트 실행 allow-list
│   └── skills/
│       ├── slide-plan/                ← 선택적 plan 스킬 (체계적인 데크용)
│       │   ├── SKILL.md               ← deck_type/arc/role/chart 어휘 + Layer 1 R1–R5
│       │   └── scripts/validate_plan.py ← R1/R2/R4/R5 + enum + 진단 비율 검증기
│       ├── diagram-design/           ← 벤더링된 다이어그램 레퍼런스 라이브러리 (lean clone, MIT). /slide가 슬라이드 다이어그램에 소비 (로컬 전용, claude.ai 번들 미포함)
│       ├── slide/
│       ├── SKILL.md                   ← 스킬 엔트리 (활성 테마 락, 직렬 파이프라인, dual-mode)
│       ├── requirements.txt           ← 파이썬 런타임 의존성 (`pip install -r`)
│       ├── references/                ← 활성 테마 디자인 참조 + 파이프라인 기술 참조
│       │   ├── design-system.tpl.md   ← 디자인 시스템 템플릿 (활성 테마에 따라 렌더)
│       │   ├── design-system.md       ← 디자인 시스템 (`/theme-init` 시 생성)
│       │   ├── theme-active.json      ← 활성 테마 스펙 (스키마: `.claude/skills/theme-init/references/token-contract.json`)
│       │   ├── anti-slop-core.md      ← 18 구조적 금지 패턴 (테마 불가지)
│       │   ├── anti-slop-theme.tpl.md ← 테마 리터럴 락 템플릿
│       │   ├── anti-slop-theme.md     ← 테마 리터럴 락 (`/theme-init` 시 생성)
│       │   ├── chart-rhetorical-roles.md ← 9 차트 수사적 역할 × charts_index.json 매핑 (slide-plan SSOT)
│       │   ├── slide-role-enum.md     ← slide_role enum + deck_type별 확장 + 진단 비율 (slide-plan SSOT)
│       │   ├── patterns.md            ← 30+ 레이아웃 패턴 레지스트리
│       │   ├── diagram-types.md       ← 14종 다이어그램 타입 문법 브리지 (테마 비종속, strict SVG subset; Executor가 다이어그램 슬라이드에서 참조)
│       │   ├── skeleton.md            ← HTML 프리뷰 스켈레톤
│       │   ├── libraries.md           ← Reveal.js / Chart.js / Mermaid / Lucide
│       │   ├── visual-assets.md       ← 일러스트 스타일
│       │   ├── strategist.tpl.md      ← Eight Confirmations 템플릿
│       │   ├── strategist.md          ← Eight Confirmations (활성 테마 락; `/theme-init` 시 생성)
│       │   ├── executor.tpl.md        ← 단일 executor 템플릿
│       │   ├── executor.md            ← 단일 executor (활성 테마 락; `/theme-init` 시 생성)
│       │   ├── image-generator.tpl.md ← 일러스트 레시피 템플릿 (활성 테마 토큰으로 렌더)
│       │   ├── image-generator.md     ← 활성 테마 일러스트 레시피 (`/theme-init` 시 image-generator.tpl.md에서 렌더; hue-neutral, 현재: Jangpm)
│       │   ├── export.md              ← svg_to_pptx 파이프라인
│       │   ├── shared-standards.md    ← SVG 기술 제약
│       │   ├── canvas-formats.md      ← 1280×720 전용
│       │   ├── image-layout-spec.md
│       │   ├── svg-image-embedding.md
│       │   ├── template-designer.md
│       │   ├── reference-2-text.txt   ← 타깃 시각 기준 텍스트
│       │   └── jangpm-patterns/       ← 25 HTML 샘플 (시각 레퍼런스 갤러리; 활성 테마 CSS로 reskin)
│       ├── scripts/                   ← 파이썬 도구 모음 (source_to_md, svg_quality_checker, finalize_svg, svg_to_pptx, …)
│       ├── templates/
│       │   ├── layouts/<theme>/       ← 활성 테마 레이아웃 팩 (cover, chapter, content, ending + design_spec + DESIGN.md). 현재: `jangpm/`
│       │   │   ├── DESIGN.md          ← preset 디자인 어휘 (`recommended_layout_family` + 차트 처리 + anti-pattern). slide-plan이 소비. jangpm은 수동 작성, 새 preset은 `/theme-init`이 skeleton 생성 후 agent가 마커 채움
│       │   │   └── assets/            ← 테마 전용 자산 (`/theme-init` 시 테마별로 갈아끼움)
│       │   │       ├── brand/         ← 저자 일러스트 (선택; 없으면 instructor-persona 슬라이드 생략)
│       │   │       └── specimen/      ← colors_and_type, preview cards (테마 시점 스냅샷)
│       │   ├── charts/                ← 56 차트 SVG (색은 사용 시점에 활성 테마 토큰으로 오버라이드)
│       │   └── icons/tabler-outline/  ← claude.ai 업로드용 essentials ~20개 (flat SVG). Claude Code는 외부 assets/icons/를 우선 사용
│       └── workflows/                 ← create-template, topic-research
├── assets/
│   ├── fonts/                         ← 공유 폰트 풀 (Pretendard 9 OTF + variable). theme-init이 이 디렉터리를 스캔해 @font-face를 동적 생성하고, 활성 테마의 primary 폰트가 없으면 Arial로 폴백
│   └── icons/                         ← Tabler 풀 라이브러리 (tabler-outline/ 5000+ · tabler-filled/ 1000+ · icons_index.txt). Claude Code 전용 — 너무 커서 claude.ai 업로드 번들에 포함 안 됨
└── output/                            ← 사용자 워크스페이스 (프로젝트 폴더는 주제명만, 예: `claude-mythos/`)
```

## 이미지 생성 백엔드

`/slide` Step 5(Image_Generator)가 이미지가 필요한 슬롯을 채울 때 사용하는 경로는 **`codex-image` 단일 경로**다. `references/image-generator.md` §🔒의 **활성 테마 Style Lock**(Deck Style Anchor + Negative Prompt)이 프롬프트 앞/뒤에 자동 prepend 된다. 이 Style Lock의 팔레트·테마명은 `image-generator.tpl.md`에서 `theme-active.json` 토큰으로 렌더되므로 `/theme-init` 교체 시 자동으로 새 테마 색을 따른다 (anti-slop 구조 락은 테마 불가지로 고정).

- **`codex-image` 스킬** (`.claude/skills/codex-image/SKILL.md`) — API 키 불필요. Codex CLI OAuth(ChatGPT 로그인) 경유 `gpt-image-2` 호출. Step 5가 `/codex-image --out <project>/images --filename <slot> --size <매핑> --quality high "<Jangpm anchor> <prompt> Avoid: <negative>"` 형태로 호출. 사이즈는 `1024x1024` / `1024x1536` / `1536x1024` 중 선택 (gpt-image-2 제약). 16:9 슬롯은 `1536x1024` 생성 → SVG `preserveAspectRatio="xMidYMid slice"`로 1280×720 크롭.

codex-image preflight(`codex login status`)가 실패하면 Step 5는 진행을 멈추고 사용자에게 `codex login` 안내한다 — 다른 백엔드로 silent fallback 하지 않는다. 새 레이아웃 템플릿은 추가하지 않음 — 기존 `templates/layouts/jangpm/01_cover.svg`(풀-블리드 16:9 슬롯) + `references/patterns.md`의 `image-text`/`image-annotated` 패턴이 이미지 슬롯을 커버한다.

## 다이어그램

시스템·관계·프로세스 시각물(architecture / flowchart / sequence / state / ER / timeline / swimlane / quadrant / nested / tree / org / layers / venn / pyramid)은 `/slide` Executor가 `references/diagram-types.md`를 참조해 **네이티브 DrawingML SVG**로 그린다. 이 브리지는 벤더링된 `.claude/skills/diagram-design/`(lean clone, MIT — `cathrynlavery/diagram-design`) 레퍼런스 라이브러리의 14종 타입 관례를 strict SVG subset(`shared-standards.md`) + 활성 테마 토큰으로 재서술한 것이다. **슬라이드 전용** — 독립 HTML 출력은 쓰지 않으며(네이티브 파이프라인 락), 이미지 플래튼도 금지. 브리지는 테마 비종속이라 `/theme-init` 교체에도 그대로 유지된다. 깊은 타입별 관례는 `.claude/skills/diagram-design/references/type-*.md`. (기존 Mermaid 경로는 HTML 프리뷰 전용으로 유지 — `libraries.md`.)

## SVG 기술 제약 (요약)

`references/shared-standards.md`에 전체 규격. 핵심:

- **금지**: `<style>`, `class`, `<foreignObject>`, `textPath`, `@font-face`, `<animate>`, `mask`, `<script>`
- **조건부 허용**: `<marker>`, `<clipPath>` (특정 구조로만)
- **PPT 호환 대체**: `rgba(…)` → `fill-opacity` / `stroke-opacity`; `<g opacity>` → 요소별 opacity
- **텍스트**: 모든 `<text>`에 Pretendard 풀 체인 (`Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", Arial, sans-serif`)
- **아이콘**: `<use data-icon="tabler-outline/<name>" … stroke="currentColor" stroke-width="2"/>` 플레이스홀더 — `finalize_svg.py`가 임베드

## 후처리 규율 (non-negotiable)

`SKILL.md §Step 7`에 상세. 핵심 규칙:

1. **`cp` 금지** — `finalize_svg.py` 대신 파일 복사로 끝내지 말 것. 아이콘 임베드 / 이미지 크롭 / 텍스트 플래튼 / 둥근사각형 변환을 건너뛴다.
2. **단일 블록 금지** — `total_md_split.py`, `finalize_svg.py`, `svg_to_pptx.py` 세 스크립트는 **각각 별도의 bash 호출**로 순차 실행. 한 블록에 묶지 말 것.
3. **`-s final` 필수** — `svg_to_pptx.py <project> -s final`. `svg_output/`에서 직접 export 하면 후처리를 건너뛴다.
4. **추가 플래그 금지** — 문서에 없는 `--only` 등 추가 플래그는 쓰지 말 것 (예외: 명시된 `--only native` / `--only legacy`).

## 자주 쓰는 명령

```bash
# 1. 프로젝트 초기화 (Jangpm 기본)
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/project_manager.py init <project_name> --format ppt169

# 2. 소스 문서 변환
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/source_to_md/pdf_to_md.py <file.pdf>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/source_to_md/doc_to_md.py <file.docx>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/source_to_md/web_to_md.py <URL>

# 3. 소스 임포트 (반드시 --move)
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/project_manager.py import-sources <project_path> <source_files...> --move

# 4. (Step 7 후처리 — 각각 별도 호출)
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/total_md_split.py <project_path>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/finalize_svg.py <project_path>
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/svg_to_pptx.py <project_path> -s final

# 5. 로컬 프리뷰
python3 -m http.server -d <project_path>/svg_final 8000

# 6. 아이콘 검색 (Claude Code: 풀 라이브러리)
grep '^tabler-outline/.*<keyword>' assets/icons/icons_index.txt
ls assets/icons/tabler-outline/ | grep <keyword>

# 6b. claude.ai 번들 빌드 (output/slide-skill-claude-ai.zip)
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/package_for_claude_ai.py

# 6c. Codex 미러 재생성 (.claude/skills 수정 후 필수)
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/dev/sync_codex_mirror.py
# 6d. dual-host 품질 게이트
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/preflight.py --needs-images
.claude/skills/slide/scripts/_py.sh .claude/skills/slide/scripts/verify_deck.py output/<project>
```

## Troubleshooting

레이아웃 오버플로우, export 에러, 빈 이미지 등 알려진 이슈는 GitHub Issues에서 보고·검색하세요.

## 참고

- **시각 기준 텍스트**: `.claude/skills/slide/references/reference-2-text.txt` — Jangpm 소스 타깃 데크에서 추출한 텍스트
- **Pretendard 폰트**: `assets/fonts/` — PPTX 배포 시 함께 배포하면 수정자 환경에서도 그대로 렌더
- **업스트림 출처**: `LICENSE-ppt-master` — 본 프로젝트가 포크한 `ppt-master` MIT 고지
