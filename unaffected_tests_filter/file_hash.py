import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, Dict, Tuple

from unaffected_tests_filter.types import SrcPathStr, ChecksumStr


def get_src_file_hash(
    file_name: SrcPathStr,
) -> Tuple[SrcPathStr, ChecksumStr]:
    hash_md5 = hashlib.md5()
    if not os.path.isfile(file_name):
        return file_name, ChecksumStr("")
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return file_name, ChecksumStr(hash_md5.hexdigest())


def get_src_file_checksums_and_deletions(
    files: Iterable[SrcPathStr],
) -> Dict[SrcPathStr, ChecksumStr]:
    with ThreadPoolExecutor(max_workers=5) as executor:
        result = executor.map(get_src_file_hash, files)
        return {src_path: checksum for src_path, checksum in result}
