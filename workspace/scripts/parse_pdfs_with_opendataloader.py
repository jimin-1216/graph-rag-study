from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = ROOT / "data" / "raw"
DEFAULT_OUTPUT_DIR = ROOT / "workspace" / "extracted" / "opendataloader"
MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "manifest.json"


def list_pdfs(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.glob("*.pdf") if path.is_file())


def build_manifest(pdf_paths: list[Path], output_dir: Path) -> dict:
    documents = []
    for pdf_path in pdf_paths:
        stem = pdf_path.stem
        documents.append(
            {
                "source_pdf": str(pdf_path),
                "json_output": str(output_dir / f"{stem}.json"),
                "markdown_output": str(output_dir / f"{stem}.md"),
            }
        )

    return {
        "input_dir": str(DEFAULT_INPUT_DIR),
        "output_dir": str(output_dir),
        "document_count": len(documents),
        "documents": documents,
    }


def main() -> int:
    try:
        import opendataloader_pdf
    except ImportError:
        print(
            "opendataloader_pdf 패키지를 찾을 수 없습니다. "
            "먼저 `pip install opendataloader-pdf`를 실행해야 합니다.",
            file=sys.stderr,
        )
        return 1

    input_dir = DEFAULT_INPUT_DIR
    output_dir = DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = list_pdfs(input_dir)
    if not pdf_paths:
        print(f"PDF를 찾지 못했습니다: {input_dir}", file=sys.stderr)
        return 1

    opendataloader_pdf.convert(
        input_path=[str(path) for path in pdf_paths],
        output_dir=str(output_dir),
        format="json,markdown",
        reading_order="xycut",
        quiet=True,
    )

    manifest = build_manifest(pdf_paths, output_dir)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"parsed {len(pdf_paths)} pdfs")
    print(f"output: {output_dir}")
    print(f"manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
