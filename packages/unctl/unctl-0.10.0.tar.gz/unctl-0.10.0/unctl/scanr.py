from kubernetes import client, config


# Data Collection Module
class DataCollector:
    def fetch_data(self):
        raise NotImplementedError


class KubernetesData:
    def __init__(self, nodes, pods):
        self._nodes = nodes
        self._pods = pods

    def get_nodes(self):
        return self._nodes

    def get_pods(self):
        return self._pods


class KubernetesDataCollector(DataCollector):
    def fetch_data(self):
        # Load kube config
        config.load_kube_config()

        # Get an instance of the API class
        v1 = client.CoreV1Api()

        # Fetch the list of nodes and pods
        nodes = v1.list_node(watch=False).items
        pods = v1.list_pod_for_all_namespaces().items

        return KubernetesData(nodes, pods)


# Check Module
class Check:
    def run(self, data):
        raise NotImplementedError


class NodeReadinessCheck(Check):
    def run(self, data):
        not_ready_nodes = [
            node.metadata.name
            for node in data.get_nodes()
            if any(
                condition.type == "Ready" and condition.status == "False"
                for condition in node.status.conditions
            )
        ]
        return not_ready_nodes


class PodHealthCheck(Check):
    def run(self, data):
        not_running_pods = [
            (pod.metadata.name, pod.metadata.namespace)
            for pod in data.get_pods()
            if pod.status.phase != "Running"
        ]
        return not_running_pods


# Main Application
class Application:
    def __init__(self, collector, checks):
        self.collector = collector
        self.checks = checks

    def execute(self):
        data = self.collector.fetch_data()
        results = {}
        for check in self.checks:
            results[check.__class__.__name__] = check.run(data)
        return results


# Usage
collector = KubernetesDataCollector()
checks = [NodeReadinessCheck(), PodHealthCheck()]
app = Application(collector, checks)
results = app.execute()

# Display the results
for check_name, result in results.items():
    if check_name == "NodeReadinessCheck":
        if result:
            print(f"{check_name}: Nodes in NotReady state: {', '.join(result)}")
        else:
            print(f"{check_name}: All nodes are in Ready state.")
    elif check_name == "PodHealthCheck":
        if result:
            pod_strings = [
                f"{pod_name} (namespace: {namespace})" for pod_name, namespace in result
            ]
            print(f"{check_name}: NotRunning pods: {', '.join(pod_strings)}")
        else:
            print(f"{check_name}: All pods are in Running state.")
