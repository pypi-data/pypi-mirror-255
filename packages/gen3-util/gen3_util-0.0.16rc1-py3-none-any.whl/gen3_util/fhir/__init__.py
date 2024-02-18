import json
import os

from fhir.resources.bundle import Bundle
from gen3_util.common import EmitterContextManager


def bundle_to_ndjson(bundle_path: str, output_dir: str):
    """Write bundle to ndjson files."""
    assert os.path.exists(bundle_path), f"{bundle_path} does not exist"
    assert os.path.exists(output_dir), f"{output_dir} does not exist"

    bundle_ = Bundle.parse_file(
        bundle_path, content_type="application/json", encoding="utf-8"
    )
    with EmitterContextManager(output_dir, file_mode="w") as emitter:
        for entry in bundle_.entry:
            fp = emitter(entry.resource.resource_type)
            json.dump(entry, fp, separators=(',', ':'))
            fp.write('\n')
