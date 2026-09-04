#!/usr/bin/env python3
"""
Regenerates frontend/public/favicon.ico from the app's own sidebar brand mark,
instead of from a hardcoded icon/color. Source of truth:

  - frontend/src/components/layout/app-sidebar.tsx
    the rounded-square badge (className contains "bg-sidebar-primary") and the
    lucide-react icon component rendered inside it
  - frontend/src/index.css
    the `--sidebar-primary` / `--sidebar-primary-foreground` oklch() values in
    the light-mode `:root { }` block

Re-run this whenever the sidebar logo icon or brand color changes; it re-reads
both from source rather than reproducing today's specific icon/hex forever.
"""

import math
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
FRONTEND = REPO_ROOT / "frontend"
SIDEBAR_TSX = FRONTEND / "src/components/layout/app-sidebar.tsx"
INDEX_CSS = FRONTEND / "src/index.css"
FAVICON_ICO = FRONTEND / "public/favicon.ico"
ICON_SIZES = [16, 32, 48, 64, 128, 256]


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def find_python_with_pillow() -> str:
    """The bare `python3` on PATH may resolve to a venv without Pillow
    (e.g. this repo's backend/.venv). Probe a few candidates instead of
    assuming any particular interpreter has it."""
    candidates = ["python3", sys.executable]
    pyenv_versions = Path.home() / ".pyenv/versions"
    if pyenv_versions.is_dir():
        candidates += [str(p / "bin/python3") for p in sorted(pyenv_versions.iterdir(), reverse=True)]
    for candidate in candidates:
        try:
            subprocess.run(
                [candidate, "-c", "import PIL"],
                check=True,
                capture_output=True,
            )
            return candidate
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    fail(
        "no Python interpreter with Pillow found (tried python3, "
        f"{sys.executable}, and any ~/.pyenv/versions/*/bin/python3). "
        "Install Pillow (`pip install pillow`) for one of these interpreters."
    )


def extract_badge_icon_name() -> str:
    """Find the lucide-react icon rendered inside the bg-sidebar-primary badge
    div in app-sidebar.tsx, e.g. `<ScrollText className="size-4" />` -> "ScrollText"."""
    tsx = SIDEBAR_TSX.read_text()
    badge_match = re.search(r'className="[^"]*\bbg-sidebar-primary\b[^"]*"', tsx)
    if not badge_match:
        fail(f"couldn't find a `bg-sidebar-primary` badge div in {SIDEBAR_TSX}")
    after_badge = tsx[badge_match.end():]
    icon_match = re.search(r"<([A-Z][A-Za-z0-9]*)", after_badge)
    if not icon_match:
        fail(f"couldn't find a JSX icon component right after the bg-sidebar-primary badge in {SIDEBAR_TSX}")
    return icon_match.group(1)


def pascal_to_kebab(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def load_icon_paths(pascal_name: str) -> list[str]:
    """Read the icon's SVG path data straight from the installed lucide-react
    package rather than vendoring path data, so a version bump or icon swap
    is picked up automatically."""
    kebab_name = pascal_to_kebab(pascal_name)
    icon_file = FRONTEND / f"node_modules/lucide-react/dist/esm/icons/{kebab_name}.mjs"
    if not icon_file.exists():
        fail(
            f"expected lucide-react icon file not found: {icon_file}\n"
            "Run `bun install` in frontend/, or check the icon name extracted "
            f"from app-sidebar.tsx ({pascal_name!r})."
        )
    source = icon_file.read_text()
    paths = re.findall(r'\[\s*"path",\s*\{\s*d:\s*"([^"]+)"', source)
    if not paths:
        fail(f"couldn't extract any <path d=...> data from {icon_file}")
    return paths


def oklch_to_hex(l: float, c: float, h_deg: float) -> str:
    """OKLCH -> sRGB hex. OKLCH is perceptually uniform but CSS/SVG fills need
    sRGB, so every color pulled from index.css has to go through this."""
    h = math.radians(h_deg)
    a = c * math.cos(h)
    b = c * math.sin(h)

    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b

    l3, m3, s3 = l_**3, m_**3, s_**3

    r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    def to_srgb_byte(channel: float) -> int:
        channel = max(0.0, min(1.0, channel))
        if channel <= 0.0031308:
            gamma = 12.92 * channel
        else:
            gamma = 1.055 * (channel ** (1 / 2.4)) - 0.055
        return round(max(0.0, min(1.0, gamma)) * 255)

    return "#{:02X}{:02X}{:02X}".format(to_srgb_byte(r), to_srgb_byte(g), to_srgb_byte(bl))


def extract_light_mode_color(css_var: str) -> str:
    """Read `--<css_var>: oklch(L C H);` from the first `:root { ... }` block
    in index.css (light mode) and convert it to a hex color."""
    css = INDEX_CSS.read_text()
    root_match = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL)
    if not root_match:
        fail(f"couldn't find a `:root {{ }}` block in {INDEX_CSS}")
    root_block = root_match.group(1)
    var_match = re.search(
        rf"--{re.escape(css_var)}:\s*oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)",
        root_block,
    )
    if not var_match:
        fail(f"couldn't find `--{css_var}: oklch(...)` in the :root block of {INDEX_CSS}")
    l, c, h = (float(x) for x in var_match.groups())
    return oklch_to_hex(l, c, h)


def build_svg(icon_paths: list[str], badge_color: str, icon_color: str, size: int = 256) -> str:
    corner_radius = round(size * 0.22)
    icon_grid = 24  # lucide icons are drawn on a 24x24 grid
    icon_rendered_size = size * 0.65
    scale = icon_rendered_size / icon_grid
    offset = (size - icon_rendered_size) / 2

    path_elements = "\n    ".join(f'<path d="{d}"/>' for d in icon_paths)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <rect width="{size}" height="{size}" rx="{corner_radius}" fill="{badge_color}"/>
  <g transform="translate({offset:.2f},{offset:.2f}) scale({scale:.4f})" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    {path_elements}
  </g>
</svg>
"""


def rasterize_and_pack(svg_path: Path, python_with_pillow: str, tmp_dir: Path) -> None:
    png_paths = []
    for size in ICON_SIZES:
        png_path = tmp_dir / f"favicon-{size}.png"
        subprocess.run(
            ["rsvg-convert", "-w", str(size), "-h", str(size), str(svg_path), "-o", str(png_path)],
            check=True,
        )
        png_paths.append(png_path)

    pack_script = f"""
from PIL import Image
sizes = {ICON_SIZES!r}
paths = {[str(p) for p in png_paths]!r}
imgs = [Image.open(p) for p in paths]
imgs[0].save({str(FAVICON_ICO)!r}, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[1:])
"""
    subprocess.run([python_with_pillow, "-c", pack_script], check=True)


def main() -> None:
    if subprocess.run(["which", "rsvg-convert"], capture_output=True).returncode != 0:
        fail("rsvg-convert not found on PATH (install with `brew install librsvg` on macOS)")

    python_with_pillow = find_python_with_pillow()

    icon_pascal_name = extract_badge_icon_name()
    icon_paths = load_icon_paths(icon_pascal_name)
    badge_color = extract_light_mode_color("sidebar-primary")
    icon_color = extract_light_mode_color("sidebar-primary-foreground")

    print(f"badge icon: {icon_pascal_name} ({pascal_to_kebab(icon_pascal_name)})")
    print(f"badge color (--sidebar-primary): {badge_color}")
    print(f"icon color (--sidebar-primary-foreground): {icon_color}")

    svg_source = build_svg(icon_paths, badge_color, icon_color)

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        svg_path = tmp_dir / "favicon.svg"
        svg_path.write_text(svg_source)
        rasterize_and_pack(svg_path, python_with_pillow, tmp_dir)

    print(f"wrote {FAVICON_ICO}")


if __name__ == "__main__":
    main()
