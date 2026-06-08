FROM registry.fedoraproject.org/fedora:42

LABEL name="devconf-demo" \
      summary="TrustChain — Build Provenance Dashboard" \
      description="Demo app for DevConf.CZ 2026: From Podman to Production" \
      io.k8s.display-name="TrustChain" \
      io.k8s.description="A Flask app that displays its own build provenance and trust chain" \
      maintainer="Vladimir Sokolenko <vsokolen@redhat.com>"

RUN dnf install -y python3 python3-pip && \
    dnf clean all && \
    rm -rf /var/cache/dnf

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

USER 1001

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
