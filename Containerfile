FROM registry.fedoraproject.org/fedora:44

RUN dnf install -y python3-pip && dnf clean all
COPY app/ /opt/app/
RUN pip3 install -r /opt/app/requirements.txt

EXPOSE 8080
CMD ["python3", "/opt/app/main.py"]
