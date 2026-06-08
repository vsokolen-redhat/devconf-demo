import os
from datetime import datetime, timezone

from flask import Flask, render_template

app = Flask(__name__)


def get_build_info():
    return {
        "image_digest": os.getenv("IMAGE_DIGEST", "unknown"),
        "image_url": os.getenv("IMAGE_URL", "unknown"),
        "build_time": os.getenv("BUILD_TIME", datetime.now(timezone.utc).isoformat()),
        "pipeline": os.getenv("BUILD_PIPELINE", "local (podman)"),
        "slsa_level": os.getenv("SLSA_LEVEL", "none"),
        "hermetic": os.getenv("HERMETIC_BUILD", "false"),
        "signed": os.getenv("IMAGE_SIGNED", "false"),
        "sbom": os.getenv("SBOM_GENERATED", "false"),
        "source_repo": os.getenv("SOURCE_REPO", "unknown"),
        "commit_sha": os.getenv("COMMIT_SHA", "unknown"),
        "base_image": os.getenv("BASE_IMAGE", "registry.fedoraproject.org/fedora:42"),
    }


@app.route("/")
def index():
    info = get_build_info()
    is_trusted = info["pipeline"] != "local (podman)"
    return render_template("index.html", info=info, is_trusted=is_trusted)


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/api/provenance")
def provenance():
    return get_build_info()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
