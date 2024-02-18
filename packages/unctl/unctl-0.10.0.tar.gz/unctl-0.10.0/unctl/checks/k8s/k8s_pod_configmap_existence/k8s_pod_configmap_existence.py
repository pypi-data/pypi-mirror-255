from unctl.lib.checks.k8s import CheckReportK8s
from unctl.lib.checks.check import Check


class k8s_pod_configmap_existence(Check):
    def _execute(self, pod, configmaps, report) -> bool:
        configmap_names = {
            (configmap.metadata.name, configmap.metadata.namespace)
            for configmap in configmaps
        }
        pod_namespace = pod.metadata.namespace

        # Check if pod.spec.containers exists before iterating
        container_checks = [
            env_var.value_from.config_map_key_ref.name
            for container in pod.spec.containers or []
            if container.env
            for env_var in container.env
            if (
                hasattr(env_var, "value_from")
                and env_var.value_from is not None
                and getattr(env_var.value_from, "config_map_key_ref", None) is not None
                and (env_var.value_from.config_map_key_ref.name, pod_namespace)
                not in configmap_names
            )
        ]

        # Check if pod.spec.volumes exists before iterating
        volume_checks = [
            volume.config_map.name
            for volume in pod.spec.volumes or []
            if volume.config_map is not None
            and (volume.config_map.name, pod_namespace) not in configmap_names
        ]

        if container_checks or volume_checks:
            configmap_name = (
                container_checks[0] if container_checks else volume_checks[0]
            )
            report.resource_configmap = configmap_name
            report.status_extended = (
                f"ConfigMap name {configmap_name} in Pod "
                f"for namespace {pod_namespace} does not "
                "exist in the list of ConfigMaps."
            )
            return False

        return True

    def execute(self, data) -> list[CheckReportK8s]:
        findings = []

        configmaps = data.get_configmaps()
        for pod in data.get_pods():
            report = CheckReportK8s(self.metadata())
            report.resource_id = pod.metadata.uid
            report.resource_name = pod.metadata.name
            report.resource_namespace = pod.metadata.namespace
            report.status = "PASS"

            if not self._execute(pod, configmaps, report):
                report.status = "FAIL"

            findings.append(report)

        return findings
