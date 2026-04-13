from __future__ import annotations

from pathlib import Path


OUT_DIR = Path(r"C:\Multiverse\output\pdf")
OUT_PATH = OUT_DIR / "gits_app_summary_one_pager.pdf"


class SimplePDF:
    def __init__(self, width: int = 612, height: int = 792) -> None:
        self.width = width
        self.height = height
        self.pages: list[str] = []

    @staticmethod
    def _esc(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def add_page(self, commands: list[str]) -> None:
        content = "\n".join(commands) + "\n"
        self.pages.append(content)

    def save(self, path: Path) -> None:
        objects: list[bytes] = []

        def add_object(data: str | bytes) -> int:
            if isinstance(data, str):
                payload = data.encode("latin-1", errors="replace")
            else:
                payload = data
            objects.append(payload)
            return len(objects)

        font_regular = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_bold = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        page_ids: list[int] = []
        content_ids: list[int] = []

        pages_placeholder = add_object("<< /Type /Pages /Kids [] /Count 0 >>")

        for page in self.pages:
            stream = page.encode("latin-1", errors="replace")
            content_id = add_object(
                b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream"
            )
            content_ids.append(content_id)
            page_id = add_object(
                f"<< /Type /Page /Parent {pages_placeholder} 0 R /MediaBox [0 0 {self.width} {self.height}] "
                f"/Resources << /Font << /F1 {font_regular} 0 R /F2 {font_bold} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            )
            page_ids.append(page_id)

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects[pages_placeholder - 1] = (
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")
        )

        catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_placeholder} 0 R >>")

        header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        body = bytearray(header)
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(body))
            body.extend(f"{index} 0 obj\n".encode("ascii"))
            body.extend(obj)
            body.extend(b"\nendobj\n")

        xref_start = len(body)
        body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        body.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

        body.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
                f"startxref\n{xref_start}\n%%EOF\n"
            ).encode("ascii")
        )

        path.write_bytes(bytes(body))


def wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_line(x: int, y: int, text: str, font: str = "F1", size: int = 10) -> str:
    return f"BT /{font} {size} Tf 1 0 0 1 {x} {y} Tm ({SimplePDF._esc(text)}) Tj ET"


def build_page() -> list[str]:
    y = 754
    commands = [
        "0.12 0.16 0.24 rg",
        "36 744 540 28 re f",
        "0 0 0 rg",
        text_line(48, 752, "Repo App Summary", font="F2", size=18),
    ]

    sections = [
        (
            "What It Is",
            [
                "A small repo-hosted control layer for temporary edit sessions and audited repo operations.",
                "The main service in gits/server/harvester.js issues JWTs, logs session events, and runs allowlisted commands in a Docker sandbox.",
            ],
        ),
        (
            "Who It's For",
            [
                "Primary persona (inferred): developers or repo maintainers who want a tracked edit session and restricted, auditable automation around a workspace.",
            ],
        ),
        (
            "What It Does",
            [
                "Issues short-lived JWT edit-session tokens via /enter and /exit endpoints.",
                "Stores the local token in .edit_token and wires a commit-msg hook during edit mode.",
                "Appends JSON audit entries for enter, exit, and run events to audit.log.",
                "Optionally signs audit lines or audit digests with GPG when available.",
                "Allowlists only lint, tests, and harvest operations on the /run endpoint.",
                "Executes those operations in an ephemeral Docker container with no network and a read-only workspace mount.",
            ],
        ),
        (
            "How It Works",
            [
                "Client scripts in gits/client call the harvester service on localhost:5000.",
                "The harvester service validates JWTs, rate-limits requests, and records audit metadata.",
                "For /run, it builds a docker run command using node:18, --network none, --read-only, and a /workspace:ro mount.",
                "docker-compose.yml exposes port 5000, injects HARVESTER_SECRET and TOKEN_TTL, and mounts the repo plus audit.log.",
                "Related auth/audit server variant: gits/server.js. Frontend UI: Not found in repo. Persistent database: Not found in repo.",
            ],
        ),
        (
            "How To Run",
            [
                "cd gits",
                "Set HARVESTER_SECRET in the environment, then run docker compose up --build",
                "Start a session: ./client/enter-edit-mode.sh \"<user>\"",
                "Run an allowlisted op: ./client/harvest-run.sh lint | tests | harvest",
                "Finish the session: ./client/exit-edit-mode.sh",
                "Dockerfile/package manifest/install doc for this service: Not found in repo.",
            ],
        ),
    ]

    heading_gap = 18
    line_gap = 12
    section_gap = 8

    for heading, bullets in sections:
        y -= 28
        commands.append(text_line(42, y, heading, font="F2", size=12))
        y -= heading_gap
        for bullet in bullets:
            wrapped = wrap(bullet, 88)
            for i, line in enumerate(wrapped):
                prefix = "- " if i == 0 else "  "
                commands.append(text_line(50, y, prefix + line, font="F1", size=9))
                y -= line_gap
        y -= section_gap

    commands.append(text_line(42, 26, f"Output: {OUT_PATH}", font="F1", size=8))
    return commands


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = SimplePDF()
    pdf.add_page(build_page())
    pdf.save(OUT_PATH)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
