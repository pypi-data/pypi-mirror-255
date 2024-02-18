from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_service_target_port_match(Check):
    def __init__(self, **data):
        super().__init__(**data)

    def _ports_match(self, pod, svc):
        # List to track whether each service port has been matched
        all_ports_matched = []

        for service_port in svc.spec.ports:
            # Check if there is a matching port for the current service port
            port_matched = any(
                container_port.container_port == service_port.target_port
                for container in pod.spec.containers
                if container.ports
                for container_port in container.ports
            )
            all_ports_matched.append(port_matched)

        # Return True only if all service ports have been matched
        return all(all_ports_matched)

    def _namespace_match(self, pod, svc):
        return pod.metadata.namespace == svc.metadata.namespace

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        # Assuming services and pods have been collected from the cluster
        services = data.get_services()
        pods = data.get_pods()

        for service in services:
            report = CheckReportK8s(self.metadata())
            report.resource_id = service.metadata.uid
            report.resource_name = service.metadata.name
            report.resource_service = service.metadata.name
            report.resource_namespace = service.metadata.namespace

            # Get selectors from the service to match pods
            service_selectors = service.spec.selector

            # If the service has no selectors, it will not have matching pods
            if not service_selectors:
                report.status = "FAIL"
                report.status_extended = (
                    f"Service {service.metadata.name} does"
                    " not have any selectors for pods."
                )
                findings.append(report)
                continue

            # Check if any pod matches the service selectors
            matching_pods = [
                (pod, service)
                for pod in pods
                if self.matches_service_selectors(pod, service_selectors)
            ]

            if matching_pods:
                for pod, service in matching_pods:
                    if self._ports_match(pod, service) and self._namespace_match(
                        pod, service
                    ):
                        report.status = "PASS"
                        report.status_extended = (
                            f"Matching port found between '{pod.metadata.name}' "
                            f"and service '{service.metadata.name}'"
                        )
                    else:
                        report.status = "FAIL"
                        report.status_extended = (
                            f"No matching port for '{pod.metadata.name}' "
                            f"and any service"
                        )
            else:
                report.status = "FAIL"
                report.status_extended = (
                    f"Service {service.metadata.name} does "
                    "not have any matching pods with its selectors."
                )

            findings.append(report)

        return findings

    def matches_service_selectors(self, pod, service_selectors):
        if not pod.metadata.labels:
            return False
        return all(
            label in pod.metadata.labels.items() for label in service_selectors.items()
        )
