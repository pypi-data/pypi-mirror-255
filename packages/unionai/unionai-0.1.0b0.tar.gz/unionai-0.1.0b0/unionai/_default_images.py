import sys
from importlib.metadata import version
from typing import Optional

from unionai._config import _GCP_SERVERLESS_ENDPOINT, _UNIONAI_CONFIG

# TODO: Host these images in a public registry
_DEFAULT_IMAGE_PREFIX: str = "us-central1-docker.pkg.dev/serverless-gcp-dataplane/union/unionai:py"


def get_default_image() -> Optional[str]:
    """Get default image version."""

    # TODO: This is only temporary to support GCP endpoints. When the unionai images are public,
    # we will always use unionai images
    if _UNIONAI_CONFIG.serverless_endpoint == _GCP_SERVERLESS_ENDPOINT:
        major, minor = sys.version_info.major, sys.version_info.minor
        unionai_version = version("unionai")
        if "dev" in unionai_version:
            suffix = "latest"
        else:
            suffix = unionai_version

        return f"{_DEFAULT_IMAGE_PREFIX}{major}.{minor}-{suffix}"

    # Returning None means that flytekit will use it's default images
    return None
