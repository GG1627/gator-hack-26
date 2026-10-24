"""Build PHOTON's pinned Linux CUDA Rust binary, via WSL on Windows."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
from time import perf_counter

from photon.gpu import _linux_path

PIN = "fc747196f2d46dce41bd844e3f5b1c5882751f2b"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug", action="store_true", help="Development host build; benchmark the release build")
    parser.add_argument("--offline", action="store_true", help="Use already-cached Cargo dependencies")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    upstream = root/".tools/cuda-rust"
    upstream.parent.mkdir(parents=True, exist_ok=True)
    if not upstream.exists():
        subprocess.run(["git", "clone", "https://github.com/NVIDIA/cuda-rust", str(upstream)], check=True)
        subprocess.run(["git", "-C", str(upstream), "checkout", PIN], check=True)
    revision = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if revision != PIN:
        parser.error(f"Expected upstream {PIN}, found {revision}; existing checkout left unchanged")
    crate = root/"crates/photon-gpu"
    target = upstream/"cutile-rs/target"
    destination = root/".tools/photon-gpu"
    destination.mkdir(parents=True, exist_ok=True)
    cargo_args = ["cargo", "build", "--locked"]
    if not args.debug:
        cargo_args.append("--release")
    if args.offline:
        cargo_args.append("--offline")
    environment = os.environ.copy()
    command = cargo_args
    if os.name == "nt":
        script = ("source ~/.cargo/env && export CUDA_TOOLKIT_PATH=/usr/local/cuda-13.3 && export CARGO_TARGET_DIR="
                  +shlex.quote(_linux_path(target))+" && cd "+shlex.quote(_linux_path(crate))+" && "+shlex.join(cargo_args))
        command = ["wsl", "-d", os.environ.get("PHOTON_WSL_DISTRO", "Ubuntu-22.04"), "--exec", "bash", "-lc", script]
    else:
        environment["CARGO_TARGET_DIR"] = str(target)
    started = perf_counter()
    with (destination/"build.log").open("wb") as log:
        completed = subprocess.run(command, cwd=crate, env=environment, stdout=log, stderr=subprocess.STDOUT)
    elapsed = (perf_counter()-started)*1000
    if completed.returncode:
        print((destination/"build.log").read_text(errors="replace"))
        raise SystemExit(completed.returncode)
    profile = "debug" if args.debug else "release"
    binary = target/profile/"photon-gpu"
    shutil.copy2(binary, destination/"photon-gpu")
    sources = hashlib.sha256()
    for path in sorted(crate.rglob("*.rs")):
        sources.update(path.relative_to(crate).as_posix().encode())
        sources.update(path.read_bytes())
    metadata = {"profile":profile, "upstream_revision":revision, "rust_toolchain":"1.98.0",
                "build_wall_ms":elapsed, "build_note":"Cargo host compilation/link wall time, cache state not assumed cold",
                "binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
                "rust_source_sha256":sources.hexdigest(), "manifest_sha256":hashlib.sha256((crate/"Cargo.toml").read_bytes()).hexdigest(),
                "lock_sha256":hashlib.sha256((crate/"Cargo.lock").read_bytes()).hexdigest()}
    (destination/"build.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
