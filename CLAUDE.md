# slide-svg

## Source of Truth

**This file is the project SSOT.** Before any slide task, read `.claude/skills/slide/SKILL.md` for the full workflow and execution rules. If another skill's conventions conflict with this document, this document wins.

## 개요

`ppt-master`의 네이티브 DrawingML SVG→PPTX 파이프라인 위에 **활성 테마 디자인 시스템**을 단일 시각언어로 락하는 한국어 강의 슬라이드 생성기. 1280×720, 편집 가능한 네이티브 도형, 모든 콘텐츠 슬라이드 하단에 `.gm` (governing message) 라인. 활성 테마는 `references/theme-active.json`(렌더 작업 사본)이 결정하며, 검증된 테마들은 **프리셋 카탈로그**(`.claude/skills/slide/assets/design-systems/<preset>/theme.json` + `active.json` 포인터)에 보관된다 — `/theme-init`로 새 테마를 굽고, 카탈로그에 있는 테마는 `init_theme.py --activate <preset>`으로 수 초 만에 전환(전역 참조 문서 결정적 재렌더, LLM 불필요). 기본 테마는 **Jangpm** (모노크롬 + 단일 `#4633E3` 인디고 액센트, Pretendard).

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
- **활성 테마 = 단일 시각언어** — PPTX가 export 시점에 토큰을 DrawingML로 굽기 때문에 런타임 멀티 테마(덱별 다른 테마 동시 사용)는 불가능. 대신 검증된 테마는 프리셋 카탈로그에 보관되고 `--activate`로 빠르게 전환한다 — 전환도 "한 시점에 하나"의 원칙은 유지 (`.claude/skills/theme-init/SKILL.md`)
- **plan/render 분리 (선택적)** — 체계적인 데크는 `/slide-plan`이 `slide_plan.json`을 먼저 만들고 `/slide`가 그 plan을 소비. 간단한 데크는 `/slide`만으로도 동작 (Standalone 모드 — 기존 Eight Confirmations 흐름 그대로). 두 모드는 같은 `/slide` 파이프라인 안에서 자동 분기.

## 스킬

| 스킬 | 트리거 | 위치 |
|------|--------|------|
| `/slide` | `"슬라이드 만들어"`, `"강의 슬라이드"`, `"프레젠테이션"`, `"make slides"`, `"/slide"`, `"생성PPT"` | 핵심 파이프라인 |
| `/slide-plan` | `"기획부터"`, `"체계적으로 슬라이드"`, `"narrative 짜줘"`, `"/slide-plan"` | 선택적 강화 단계 — `/slide` 이전에 실행 |
| `/theme-init` | `"테마 교체"`, `"디자인 시스템 바꿔"`, `"새 브랜드 적용"`, `"change the design system"`, `"replace the theme"` | 새 테마 베이크(카탈로그 등록) / 카탈로그 프리셋 빠른 전환(`--activate`) |

스킬 정의:
- `/slide`: `.claude/skills/slide/SKILL.md` — Step 4에서 `slide_plan.json` 존재 시 plan-consuming 모드, 부재 시 Eight Confirmations 모드로 자동 분기
- `/slide-plan`: `.claude/skills/slide-plan/SKILL.md` — deck_type 감지 + narrative arc + 슬라이드별 rationale + 차트 수사적 역할 + Layer 1 R1–R5 검증 (`scripts/validate_plan.py`). 출력: `output/<project>/slide_plan.json`
- `/theme-init`: `.claude/skills/theme-init/SKILL.md` (새 테마 베이크: 에이전트가 디자인 가이드를 직접 추출 → fill-nulls → 토큰 검증 → 전 참조 파일 재생성 + `templates/layouts/<theme>/DESIGN.md` skeleton 생성 → 에이전트가 `<!-- AGENT-FILL -->` 마커 채워 완성 → **Step 5 Shell Composition**(선택): 에이전트가 baseline 셸을 레퍼런스로 좌표·정렬·장식·내러티브 밴드를 `_shell_src/*.tpl.svg`로 재작곡 → render-first 프리뷰로 사용자 피드백 루프 → `validate_shells.py` 락 검사 → 사용자 검토 BLOCKING; API key 불필요, jsonschema만 필요; 캔버스 1280×720은 테마 간 영구 락; 라이트 완화는 내러티브 셸 밴드까지만 — content 셸은 라이트 유지. 베이크 성공 시 테마가 카탈로그에 자동 등록되며, 이미 카탈로그에 있는 테마는 `init_theme.py --activate <preset>`으로 베이크 없이 빠른 전환 — 셸·DESIGN.md·`_shell_src/`는 테마별 보존)

## 사용 패턴

```
간단:  /slide                                 (8 슬라이드 미만, 단일 소스)
체계: /slide-plan → 사용자 검토 → /slide      (강의·임원 보고서·세일즈 데크)
```

`/slide`는 두 패턴 모두 자동 처리. `slide_plan.json`이 `output/<project>/`에 있으면 plan-consuming, 없으면 Standalone.

## 디렉터리

핵심 위치 요약:
- 스킬: `.claude/skills/{slide, slide-plan, theme-init, chart-design, diagram-design, codex-image, upload-drive}/` — 각 스킬은 SKILL.md + references/ + scripts/
- 활성 테마 참조: `.claude/skills/slide/references/` (theme-active.json, design-system.md, anti-slop-*.md, …)
- 테마 카탈로그: `.claude/skills/slide/assets/design-systems/`, 레이아웃 팩: `.claude/skills/slide/templates/layouts/<theme>/`
- 공유 자산: `assets/fonts/` (Pretendard), `assets/icons/` (Tabler 풀 라이브러리, Claude Code 전용)
- 산출물: `output/<project>/` (프로젝트 폴더는 주제명만)

## 이미지 생성 백엔드

🔒 **호스트별 백엔드 락**: Claude Code는 vendored `/codex-image` 스킬(Codex CLI OAuth 경유 `gpt-image-2`, API 키 불필요), Codex는 내장 `imagegen` 스킬 / `image_gen` 도구만. 다른 생성기 대체·silent fallback 금지 — preflight/실행 실패 시 Step 5는 halt하고 블로커 보고 (Claude Code는 `codex login status` 게이트). 모든 프롬프트에 `references/image-generator.md` §🔒의 활성 테마 Style Lock이 자동 prepend되며, 팔레트는 `/theme-init` 교체를 자동 추종한다. `codex-image`는 `.codex/skills` 미러에 패키징하지 않는다 (Codex 내장 기능과 중복). 호출 문법·사이즈 매핑·16:9 크롭 규칙 상세: `.claude/skills/slide/references/executor-steps-4-6.md` Step 5.

## 차트 (데이터 기반)

실제 숫자로 그리는 정량 차트(21종: bar 계열 5, line/area 계열 4, scatter/combo/waterfall/bullet, pie/donut/gauge/radar, kpi_cards/progress/funnel/heatmap/treemap)는 `/slide` Executor가 **`chart-design` 스킬의 렌더 엔진**으로 생성한다 — 데이터 spec JSON 작성 → `.claude/skills/chart-design/scripts/render_chart.py`가 지오메트리(스케일·틱·아크)를 계산하고 스타일은 전부 활성 테마 토큰에서 해석(하드코딩 색상 없음, 토큰 못 읽으면 fail). 순수 stdlib·네트워크 없음·컨버터 세이프 출력. 차트 선택 판단 규칙(bar 기본, pie/radar 게이트)은 `.claude/skills/chart-design/SKILL.md` §1, 슬라이드 임베딩 계약과 `chart_strategy` 매핑은 그 `references/integration.md`. 21종 외 타입(sankey, gantt, SWOT 등)과 구도 참고는 기존 `templates/charts/` 정적 라이브러리 경로 유지. 테마 교체 시 spec 재렌더로 자동 추종.

## 다이어그램

시스템·관계·프로세스 시각물(14종: architecture, flowchart, sequence, state, ER, timeline, swimlane, quadrant, nested, tree, org, layers, venn, pyramid)은 `/slide` Executor가 `references/diagram-types.md`를 참조해 **네이티브 DrawingML SVG**로 그린다. **슬라이드 전용** — 독립 HTML 출력 없음, 이미지 플래튼 금지, 테마 비종속(`/theme-init` 교체에도 유지). 타입별 깊은 관례: `.claude/skills/diagram-design/references/type-*.md` (lean clone, MIT). (Mermaid 경로는 HTML 프리뷰 전용 — `libraries.md`.)

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

# 7. 테마 카탈로그 (보관된 프리셋 목록: assets/design-systems/README.md)
python3 .claude/skills/theme-init/scripts/init_theme.py --activate <preset>   # 카탈로그 프리셋으로 빠른 전환
python3 .claude/skills/theme-init/scripts/init_theme.py --register-current    # 현 활성 테마를 카탈로그에 등록
```

## Troubleshooting

레이아웃 오버플로우, export 에러, 빈 이미지 등 알려진 이슈는 GitHub Issues에서 보고·검색하세요.

## 참고

- **officecli (선택)**: 설치 시 `verify_deck.py`(Step 7.4)가 최신 네이티브 PPTX에 OpenXML validate(열 수 없는 corrupt 파일 → 하드 페일, 스키마 warning → WARN)와 export된 PPTX 실물 컨택트 시트(`output/<project>/_pptx_render/<stem>-grid.png`, 눈검수용)를 추가 수행한다 — 미설치 시 자동 skip, `OFFICECLI_BIN`으로 지정/비활성 가능
- **시각 기준 텍스트**: `.claude/skills/slide/references/reference-2-text.txt` — Jangpm 소스 타깃 데크에서 추출한 텍스트
- **Pretendard 폰트**: `assets/fonts/` — PPTX 배포 시 함께 배포하면 수정자 환경에서도 그대로 렌더
- **업스트림 출처**: `LICENSE-ppt-master` — 본 프로젝트가 포크한 `ppt-master` MIT 고지
