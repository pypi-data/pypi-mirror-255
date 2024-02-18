from types import MappingProxyType

from unctl.constants import CheckProviders

HEADERS = {
    CheckProviders.K8S: [
        "Namespace",
        "Object",
        "Check",
        "Severity",
        "Status",
        "Summary",
    ],
    CheckProviders.MySQL: [
        "Object",
        "Check",
        "Severity",
        "Status",
        "Summary",
    ],
}

HEADERS = MappingProxyType(HEADERS)
