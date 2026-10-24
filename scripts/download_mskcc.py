"""Resume verified MSKCC first270-volume downloads from the author ZIP.

One independent HTTP range reader per worker. Raw images stay under ignored data/.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
from pathlib import Path
import threading
import time
import zipfile

from audit_mskcc_dataset import RangeReader, cached_entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", choices=["s1","s2","s3"], default="s1")
    parser.add_argument("--workers", type=int, choices=range(1,5), default=4)
    args = parser.parse_args()
    sequence = f"mskcc_confocal_{args.sequence}"
    prefix = f"mskcc-confocal/{sequence}"
    cache = Path("data/mskcc-audit")
    state = threading.local()

    def fetch(name):
        if not hasattr(state,"zip"):
            state.zip = zipfile.ZipFile(RangeReader())
        for attempt in range(3):
            try:
                return cached_entry(state.zip,name,cache)
            except (OSError, ValueError, zipfile.BadZipFile) as exc:
                if attempt == 2:
                    raise
                print(f"Retry {attempt+1} for {name}: {exc}",flush=True)
                time.sleep(1+attempt)

    names = [f"{prefix}/images/{sequence}_t{t:03}.tif" for t in range(270)]
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch,name) for name in names]
        for number,future in enumerate(as_completed(futures),1):
            future.result()
            if number % 10 == 0 or number == len(names):
                print(f"Verified {number}/{len(names)} volumes; elapsed {time.perf_counter()-start:.1f}s",flush=True)
    for name in ("tracks.txt","tracks_mamut.xml"):
        fetch(f"{prefix}/tracks/{name}")
    manifest = {"dataset_id":"MSKCC-CONFOCAL","sequence_id":sequence,
        "source_doi":"10.5281/zenodo.6460303","source_frame_indices":[0,269],
        "selected_frame_count":270,"original_frame_count":400,
        "verification":"Each selected image and annotation checked against source ZIP CRC32",
        "full_archive_md5_verified":False,"completed_local_time":datetime.now().astimezone().isoformat()}
    (cache/prefix/"download-manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2),flush=True)


if __name__ == "__main__":
    main()
