import os
import json
from typing import Dict
from unctl.config.config import get_config_instance
from unctl.lib.models.checks import CheckMetadataModel


def load_checks(provider=None, checks_dir="checks") -> Dict[str, CheckMetadataModel]:
    checks_loaded = {}

    check_root = os.path.join(os.path.dirname(__file__), checks_dir)

    config = get_config_instance()
    categories = config.filter.categories
    services = config.filter.services
    checks = config.filter.checks
    ignored_checks = config.ignore.checks

    for provider_dir in os.listdir(check_root):
        if provider and provider != provider_dir:
            continue

        for check_name in os.listdir(os.path.join(check_root, provider_dir)):
            check_md_path = os.path.join(
                check_root, provider_dir, check_name, f"{check_name}.json"
            )

            if not os.path.isfile(check_md_path):
                continue

            module_name = (
                f"{__package__}.{checks_dir}.{provider_dir}.{check_name}.{check_name}"
            )

            with open(check_md_path, "r") as metadata_file:
                metadata = json.load(metadata_file)

                # Check if the check matches the criteria
                provider_match = not provider or provider == metadata["Provider"]
                categories_match = not categories or any(
                    cat in metadata["Categories"] for cat in categories
                )
                services_match = not services or metadata["ServiceName"] in services
                checks_match = not checks or metadata["CheckID"] in checks
                not_ignored = metadata["CheckID"] not in ignored_checks

                if all(
                    [
                        provider_match,
                        categories_match,
                        services_match,
                        checks_match,
                        not_ignored,
                    ]
                ):
                    # Extract the required information
                    check = CheckMetadataModel.model_validate_json(json.dumps(metadata))
                    checks_loaded[module_name] = check

    checks_loaded = dict(
        sorted(checks_loaded.items(), key=lambda check: check[1].CheckTitle)
    )

    return checks_loaded


def get_services(provider=None) -> Dict[str, int]:
    checks = load_checks(provider)
    unique_services = {}
    for check in list(checks.values()):
        service_name = check.ServiceName
        unique_services[service_name] = unique_services.get(service_name, 0) + 1
    return unique_services


def get_categories(provider=None) -> Dict[str, int]:
    checks = load_checks(provider)
    unique_categories = {}
    for check in list(checks.values()):
        for category in check.Categories:
            unique_categories[category] = unique_categories.get(category, 0) + 1
    return unique_categories
