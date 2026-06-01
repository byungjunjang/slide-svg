---
name: upload-drive
description: >
  Upload slide files to Google Drive and convert to Google Slides by default.
  Uses gws-drive-upload skill for file upload.
  Trigger on: "/upload-drive", "드라이브에 올려", "upload to Google Drive",
  "구글 드라이브", "share on Drive"
---

# /upload-drive — Google Drive Uploader

## Purpose

Upload PPTX (or HTML/PDF) slide files to Google Drive. **Google Slides 변환은 기본값 — 별도 지시 없어도 항상 변환한다.**

In slide-svg the canonical deliverable is the native DrawingML PPTX produced by `svg_to_pptx.py -s final` (written to `output/<project>/exports/<project>_<timestamp>.pptx`). This skill takes that PPTX and pushes it to Drive + Google Slides.

## Usage

```
/upload-drive
/upload-drive output/my-deck/exports/my-deck_20260422.pptx
/upload-drive output/my-deck/exports/my-deck_20260422.pptx --folder "Presentations/2026-Q1"
/upload-drive output/my-deck/exports/my-deck_20260422.pptx --no-slides   ← 변환 안 할 때만 명시
```

## Prerequisites

Google Workspace authentication must be configured via the `gws` CLI tools. Run `gws-drive` to verify access.

## Workflow

### Step 1 — Identify the File

- If a path is provided, use it
- Otherwise, find the most recent `.pptx` file anywhere under `output/**/exports/`
- slide-svg 구조: `output/<project>/exports/<project>_<timestamp>.pptx` (기본) 또는 `..._svg.pptx` (SVG 이미지 버전)
- 기본 대상은 **네이티브 DrawingML PPTX** (`<project>_<timestamp>.pptx`). `_svg.pptx`는 사용자가 명시한 경우에만 업로드한다.
- Also accepts `.html` or `.pdf` files

### Step 2 — Upload to Google Drive

Use the `gws-drive-upload` skill:

```bash
gws drive +upload "{file_path}"
```

### Step 3 — Convert to Google Slides (DEFAULT, always run)

업로드 완료 후 **항상** Google Slides로 변환한다. `--no-slides`를 명시한 경우에만 건너뛴다.

```bash
# 업로드로 얻은 fileId를 사용해 Google Slides로 복사·변환
gws drive files copy \
  --params '{"fileId": "<uploaded_file_id>"}' \
  --json '{"mimeType": "application/vnd.google-apps.presentation", "name": "<한국어 제목>"}'
```

- `name` 필드에는 파일명 slug 대신 **슬라이드의 실제 한국어 제목**을 사용한다 (프로젝트 `total.md` 상단 H1 또는 strategist가 확정한 덱 타이틀 사용).
- 변환된 파일 ID로 Google Slides URL을 생성한다: `https://docs.google.com/presentation/d/{id}`

### Step 4 — Report Results

Return to the user:
- Google Drive PPTX 파일 ID (원본)
- **Google Slides URL** (항상 제공)
- Share settings (default: private, user can adjust)

## Notes

- Large files (>50MB) may take longer to upload
- Google Slides conversion may alter some formatting — slide-svg의 네이티브 DrawingML은 대부분의 도형/텍스트를 보존하지만, 커스텀 폰트(Pretendard)와 일부 벡터 효과가 Google Slides 기본 폰트로 치환될 수 있다
- Users can share the Drive link directly for collaboration
