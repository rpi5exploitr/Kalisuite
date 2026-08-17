#!/usr/bin/env python3
"""
Utility to build a .deb package for KaliSuite.

When executed, this script:
1. Copies the entire KaliSuite project (the folder containing this script)
   into a temporary build directory.
2. Generates the required DEBIAN/control metadata file, embedding the
   maintainer as rpi5exploitr <rpi5exploitr@outlook.com>.
3. Invokes `dpkg-deb` to produce a .deb file that can be installed on
   Debian/Ubuntu/Kali systems.

Author: rpi5exploitr <rpi5exploitr@outlook.com>
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def _read_version() -> str:
    """
    Extract the package version from setup.py.
    Falls back to "0.1.0" if the file cannot be read.
    """
    setup_path = Path(__file__).parent / "setup.py"
    if not setup_path.is_file():
        return "0.1.0"
    for line in setup_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("version"):
            # Expected format: version="0.1.0",
            try:
                return line.split("=")[1].strip().strip('",\'')
            except Exception:
                continue
    return "0.1.0"

def _create_control_file(debian_dir: Path, package_name: str, version: str) -> None:
    """
    Write the DEBIAN/control file with the required fields.
    The Maintainer field contains the signed email and author name.
    """
    control_content = f"""Package: {package_name}
Version: {version}
Section: utils
Priority: optional
Architecture: all
Maintainer: rpi5exploitr <rpi5exploitr@outlook.com>
Description: GUI for various Kali Linux security tools.
 Depends: python3, python3-pyqt6, python3-pymetasploit3
"""
    (debian_dir / "control").write_text(control_content, encoding="utf-8")

def _copy_source(src_root: Path, dst_root: Path, package_name: str) -> None:
    """
    Copy the entire project source tree into the package root.
    The actual install location inside the .deb will be /usr/share/kalisuite.
    """
    target_dir = dst_root / "usr" / "share" / package_name
    shutil.copytree(src_root, target_dir, dirs_exist_ok=True)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a .deb package from the KaliSuite source tree."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the resulting .deb file. Defaults to kalisuite_<version>_all.deb in the current directory.",
        default=None,
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.resolve()
    package_name = "kalisuite"
    version = _read_version()
    arch = "all"

    # Temporary build environment
    with tempfile.TemporaryDirectory() as tmpdir:
        build_root = Path(tmpdir) / f"{package_name}_{version}"
        debian_dir = build_root / "DEBIAN"
        debian_dir.mkdir(parents=True, exist_ok=True)

        # 1. Copy source files
        _copy_source(project_root, build_root, package_name)

        # 2. Create control metadata
        _create_control_file(debian_dir, package_name, version)

        # 3. Build the .deb package
        output_deb = args.output
        if not output_deb:
            output_deb = f"{package_name}_{version}_{arch}.deb"
        output_path = Path(output_deb).resolve()

        try:
            subprocess.check_call(
                ["dpkg-deb", "--build", str(build_root), str(output_path)]
            )
            print(f"✅ Package built successfully: {output_path}")
        except subprocess.CalledProcessError as exc:
            print("❌ Failed to build the .deb package.", file=sys.stderr)
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
