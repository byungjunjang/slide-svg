---
name: codex-image
description: |
  Generate images via Codex CLI's built-in image_gen tool (gpt-image-2). OAuth auth — no API key needed.
  Codex CLI의 내장 image_gen 도구로 이미지 생성. OAuth 인증으로 API 키 불필요.
  Usage: /codex-image cherry blossom hanok, /codex-image --size 1024x1536 space cat, /codex-image --quality high seoul night
argument-hint: "[--size <WxH>] [--quality low|medium|high] [--out <dir>] [--filename <stem>] [-n <count>] [--ref <image>]... <image prompt>"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# codex-image — AI Image Generation via Codex OAuth

Generate images with OpenAI's `gpt-image-2` model through Codex CLI.
No API key is needed: Codex OAuth (ChatGPT login) handles authentication.

User-facing messages below are bilingual (EN / KO). Print the one that matches the user's chat language.

## How it works

```
User prompt → Claude Code (/codex-image)
  → codex exec (OAuth token auto-managed)
    → built-in image_gen tool (gpt-image-2)
      → ~/.codex/generated_images/<session>/
        → copy to <out dir>/<filename>.png
```

OAuth tokens cannot call the OpenAI REST API directly (it returns 401), so generation goes through `codex exec`, which handles auth internally.

---

## Step 1 — Verify Codex CLI & Auth

```bash
which codex 2>/dev/null && codex --version 2>/dev/null || echo "NOT_FOUND"
```

If `NOT_FOUND`, stop:
> "Codex CLI not installed. Run `npm install -g @openai/codex` then `codex login`."
> "Codex CLI 없음. `npm install -g @openai/codex` 후 `codex login` 실행해."

```bash
codex login status 2>&1
```

If not "Logged in", stop:
> "Codex login required. Run `codex login` in terminal. OAuth login enables image generation without API key."
> "Codex 로그인 필요. 터미널에서 `codex login` 실행. OAuth 로그인하면 API 키 없이 이미지 생성 가능."

## Step 2 — Parse Arguments

Extract from `$ARGUMENTS`:

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `1024x1024`, `1024x1536`, `1536x1024`, `auto` | `1024x1024` | Image dimensions |
| `--quality` | `low`, `medium`, `high`, `auto` | `auto` | Generation quality |
| `--out` | directory path (inside the project root) | project root | Save location |
| `--filename` | name without extension | `codex-image-<timestamp>` | Output filename stem |
| `-n` | 1–10 | `1` | Number of images |
| `--ref` | image file path, repeatable | none | Reference image attached to Codex (Step 4) |

Remaining text → image prompt.

If the prompt is empty, ask via AskUserQuestion:
> "What image should I generate? Enter a prompt."
> "어떤 이미지를 생성할까? 프롬프트를 입력해줘."

If a user typed a prompt that is too vague to act on, ask what they want before spending a generation. When another skill or pipeline passes a finished prompt, generate it as given.

## Step 3 — Normalize Background Phrasing

`gpt-image-2` cannot output real alpha. Asked for a "transparent background", it paints a gray-and-white checkerboard (the pattern editors use to display transparency) into the pixels, which looks broken on any backdrop. Rewrite transparency phrasing to a clean solid background before generating. A backdrop color the caller named (`#FAFAF9 background`, `white background`, `흰색 배경`) is left as is and becomes the solid fill.

```bash
_PROMPT=$(printf '%s' "${_PROMPT}" | perl -CSD -Mutf8 -pe '
  s/\b(?:fully |truly |perfectly |pure )?transparent[ -]+(?:background|backdrop|bg)\b/clean solid background/gi;
  s/\bno background\b/clean solid background/gi;
  s/투명(?:한)?\s*배경/단색 배경/g;
  s/배경\s*없(?:음|이|는|다)/단색 배경/g;')
echo "[codex-image] prompt after background normalization: ${_PROMPT}"
```

When writing prompts for this skill, ask for `clean solid <color> background` directly instead of a transparent one. If the user needs a cut-out asset, generate on a flat solid color and remove the background afterward in an image editor.

## Step 4 — Resolve Paths

```bash
_PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd -W 2>/dev/null || pwd)
_OUT_DIR="${_OUT_ARG:-${_PROJECT_ROOT}}"
case "${_OUT_DIR}" in /*|[A-Za-z]:*) ;; *) _OUT_DIR="${_PROJECT_ROOT}/${_OUT_DIR}" ;; esac
mkdir -p "${_OUT_DIR}"
_FILENAME="${_FILENAME_ARG:-codex-image-$(date +%Y%m%d-%H%M%S)}"

# Existing outputs: stop if anything prints.
ls "${_OUT_DIR}/${_FILENAME}.png" "${_OUT_DIR}/${_FILENAME}"-[0-9]*.png 2>/dev/null

# References: absolute paths; stop if anything prints MISSING.
_REFS=()
for r in "${_REF_ARGS[@]}"; do
  case "$r" in /*|[A-Za-z]:*) ;; *) r="${_PROJECT_ROOT}/$r" ;; esac
  [ -f "$r" ] || echo "MISSING: $r"
  _REFS+=("$r")
done
```

- Single image: `<stem>.png`. Multiple (`-n > 1`): `<stem>-1.png`, `<stem>-2.png`, ...
- Without `--filename` the stem carries a timestamp. With `--filename`, the stem is used as given, so callers that need a fixed name (a slot name, a numbered candidate) pass it here.
- Never overwrite an existing file. If the `ls` check prints a path, stop and report it; the caller picks a new `--filename` or `--out`, or removes the old file first.
- Keep `--out` inside the project root. Codex runs with `-s workspace-write` rooted at `-C`, so it cannot write outside that tree.
- If any `--ref` path is missing, stop before calling Codex and report the path.

## Step 5 — Generate

Build the task text, then pipe it to `codex exec -`. Passing the task on stdin keeps quotes in the prompt from breaking shell quoting, and the pipe closes stdin when the task ends. From a non-TTY shell such as the Bash tool, `codex exec` otherwise waits on "Reading additional input from stdin..." until the timeout.

```bash
_REF_LINE="No reference images are attached."
if [ "${#_REFS[@]}" -gt 0 ]; then
  _REF_LINE="Treat the attached reference images as controls, not inspiration: follow each one for the role the prompt gives it. If the prompt text and a reference disagree, follow the reference. Attached, in order: $(printf "'%s' " "${_REFS[@]}")"
fi

_TASK=$(cat <<EOF
Perform the following tasks:
1. Use the built-in image_gen tool to generate ${_N:-1} image(s).
2. Image prompt (everything between the markers, verbatim):
---PROMPT---
${_PROMPT}
---END PROMPT---
3. ${_REF_LINE}
4. Background: render on a clean, single, solid flat background. Do not paint a transparency checkerboard (alternating gray and white squares); gpt-image-2 has no real alpha, so a transparent request comes out as painted squares. If the prompt implies a transparent or missing background, use the backdrop color it names, otherwise plain white.
5. Size: ${_SIZE:-1024x1024}
6. Quality: ${_QUALITY:-auto}
7. Copy the generated image to '${_OUT_DIR}/${_FILENAME}.png'. For multiple images use '${_OUT_DIR}/${_FILENAME}-1.png', '-2.png', and so on. Do not overwrite existing files.
8. Print the absolute saved file path(s) and file size in bytes.
EOF
)

_ARGS=(exec - -C "${_PROJECT_ROOT}" -s workspace-write -c 'model_reasoning_effort="medium"' --skip-git-repo-check)
for r in "${_REFS[@]}"; do _ARGS+=(-i "$r"); done

printf '%s\n' "${_TASK}" | codex "${_ARGS[@]}" 2>&1
```

Bash tool timeout: 600000 ms (10 min). A medium 1536x1024 image takes 1–2 minutes; `--quality high` and `--ref` runs take longer.

Flag notes:

- `exec -` reads the task from stdin. If you pass the task as an argument instead, add `< /dev/null` to close stdin.
- `-i <file>` takes several values, so the `-i` flags go last. Placed before the other arguments, it can swallow the next one as a file name. One `-i` per reference.
- `-s workspace-write` lets Codex copy the file into the project. `--skip-git-repo-check` lets it run outside a git repo.
- With `--ref`, the prompt should say what each reference controls (for example: line art = silhouette, depth map = camera, material map = material zones).

## Step 6 — Verify and Display

Confirm the expected files exist and are not empty:

```bash
ls -l "${_OUT_DIR}/${_FILENAME}.png" "${_OUT_DIR}/${_FILENAME}"-[0-9]*.png 2>/dev/null
```

If Codex printed a path but no file is on disk, report the failure; do not say an image was produced.

Then open each saved image with the Read tool. The user sees the result, and you can check it against the prompt. If it shows a painted checkerboard or clearly misses the prompt, say so and offer a rerun with an explicit solid background color.

```
═══════════════════════════════════════════════
IMAGE GENERATED / 이미지 생성 완료
═══════════════════════════════════════════════
Prompt: <prompt used>
Size: <size>
Quality: <quality>
Count: <n>
References: <ref paths, or none>
Auth: OAuth (ChatGPT)
───────────────────────────────────────────────
<saved file path(s)>
═══════════════════════════════════════════════
```

Follow-up for standalone use: run `/codex-image` again for another image; in a Next.js project, suggest moving the file under `public/images/` if needed.

## Error Handling

| Error | Message / action |
|-------|---------|
| Auth expired | "Codex OAuth expired. Run `codex login` again." / "OAuth 인증 만료. `codex login` 다시 실행." |
| Model access denied | "No access to gpt-image-2. Check your OpenAI plan." / "gpt-image-2 접근 권한 없음. OpenAI 플랜 확인." |
| Model requires a newer Codex | The model in `~/.codex/config.toml` is newer than the installed CLI. Suggest `npm install -g @openai/codex@latest`, or pass `-m <model>` for this run. Do not edit the user's config. |
| Timeout (>10 min) | Retry once with a lower `--quality`, then report. / "생성 시간 초과. 낮은 `--quality`로 한 번 재시도." |
| Rate limit | "API rate limited. Wait and retry." / "API 호출 제한. 잠시 후 재시도." |
| Trust error | Check the `--skip-git-repo-check` flag or add the project to `~/.codex/config.toml`. |
| Missing `--ref` file | Stop before calling Codex and report the missing path. / Codex 호출 전에 중단하고 누락 경로 보고. |
| Output file exists | Stop and report the path; do not overwrite. / 기존 파일이 있으면 덮어쓰지 않고 경로 보고. |

## Notes

- Inside a Codex session, call the built-in `image_gen` tool directly. A nested `codex exec` started from inside Codex gets 401.
- Do not call the OpenAI REST API with the OAuth token; it returns 401.
