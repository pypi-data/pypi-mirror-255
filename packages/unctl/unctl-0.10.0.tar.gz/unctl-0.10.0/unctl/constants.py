from enum import Enum

# Segment analytics constants
USER = "unctl_user"
SEGMENT_WRITE_KEY = "qSQliHLwStBWT3nncdrN241UgdZdPM5H"


class CheckProviders(str, Enum):
    K8S = "k8s"
    MySQL = "mysql"
