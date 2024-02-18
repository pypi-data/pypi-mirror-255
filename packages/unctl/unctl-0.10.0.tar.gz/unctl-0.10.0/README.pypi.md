# unctl

<!-- PROJECT LOGO -->
<br />
<div align="center">
    <a href="https://unskript.com/">
        <img src="https://storage.googleapis.com/unskript-website/assets/favicon.png" alt="Logo" width="80" height="80">
    </a>
    <p align="center">
    <a href="https://pypi.org/project/unctl/"><img alt="Python Version" src="https://img.shields.io/pypi/v/unctl.svg"></a>
    <a href="https://pypi.python.org/pypi/unctl/"><img alt="Python Version" src="https://img.shields.io/pypi/pyversions/unctl.svg"></a>
    <a href="https://pypistats.org/packages/unctl"><img alt="PyPI unctl downloads" src="https://img.shields.io/pypi/dw/unctl.svg?label=unctl%20downloads"></a>
</p>
</div>

<!-- TABLE OF CONTENTS -->
<br />
<p align="center">Table of Contents</p>
<ol>
<li>
    About The Project
    <ul>
        <li>Checks</li>
        <li>Built With</li>
    </ul>
</li>
<li>
    Getting Started
    <ul>
        <li>Prerequisites</li>
        <li>Installation</li>
        <li>Config file</li>
    </ul>
</li>
<li>Usage</li>
<li>Roadmap</li>
<li>Contact</li>
</ol>

<!-- ABOUT THE PROJECT -->
## About The Project

`unctl` is a versatile command-line tool designed to perform a wide range of checks and inspections on various components of your infrastructure. It provides a unified interface to assess the health and performance of different services and platforms, and goes beyond mere diagnosis. With built-in **AI** capabilities, it guides you seamlessly from system diagnostic to remediation, offering intelligent solutions to address any issues it detects.

This addition emphasizes the tool's capacity to not only identify problems but also provide **AI-driven** recommendations and solutions for resolving those issues, making it even more valuable for infrastructure management and maintenance.

### Checks

<!-- Do not edit content within this section, it is auto-generated -->
<!-- GENERATED_CHECKS_GROUPS_SECTION_START -->
| Provider | Checks |
|---|---|
| k8s | 31 |
| mysql | 1 |

<!-- GENERATED_CHECKS_GROUPS_SECTION_END -->
<!-- GENERATED_CHECKS_SECTION_START -->
#### k8s checks
| Check | ID | Service | Category | Severity | Description |
|---|---|---|---|---|---|
| Check if a k8s PVC is in Pending state | K8S401 | pvc | Health | Critical | Alerts on pending PVCs, highlighting potential delays in provisioning persistent volume claims for all the namespaces |
| Check if the k8s node is in Ready state | K8S504 | node | Health | Critical | Ensure node health by examining readiness conditions, signaling failures if any issues are detected in the node's status |
| Deployment has insufficient replicas | K8S801 | deployment | Health | Critical | Validate Deployments for the correct number of available replicas, highlighting any discrepancies between desired and available counts |
| Pod has a high restart count | K8S104 | pod | Health | Critical | Identify pods for all the namespaces where certain containers have restarted more than 10 times, indicating potential instability concerns |
| Pod is in CrashLoopBackOff state | K8S103 | pod | Health | Critical | Identify pods with containers stuck in a CrashLoopBackOff state, highlighting potential issues impacting pod stability for all the namespaces |
| Service has endpoints that are NotReady | K8S304 | service | Health | Severe | Highlights when services have NotReady endpoints, indicating potential disruptions to service reliability for all the namespaces |
| Service has no endpoints | K8S301 | service | Health | Severe | Identify services with no associated endpoints, highlighting potential misconfigurations impacting service connectivity |
| Analyzing HPAs, checking if scale targets exist and have resources | K8S101 | pod | HPA | High | Analyze optimal Horizontal Pod Autoscaler (HPA) configurations by ensuring associated resources (Deployments, ReplicationControllers, ReplicaSets, StatefulSets) have defined resource limits for effective auto-scaling |
| Check for the existence of Ingress class, service and secrets for all the namespaces | K8S201 | ingress | Ingress | High | Ensure proper Ingress configurations by validating associated services, secrets, and ingress classes, flagging issues if there are missing elements or misconfigured settings for all the namespaces |
| Check the existence of secret in Daemonset | K8S603 | daemonset | Daemonset, Secret | High | Ensure the presence of referenced Secrets in Daemonset volumes, reporting failures for any missing Secret within all the namespaces |
| Check the existence of secret in Deployment | K8S701 | secret | Deployment | High | Ensure the presence of referenced Secrets in Deployment volumes, reporting failures for any missing Secret for all the namespaces |
| Excessive Pods on Node | K8S501 | node | Resource Limits | High | Assesses nodes for excessive pod counts, flagging potential issues if pods near capacity thresholds based on CPU and memory resources |
| Find Deployments with missing configmap | K8S901 | configmap | Deployment | High | Ensure the presence of referenced ConfigMaps in Deployment volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Find Pending Pods | K8S106 | pod | Health | High | Ensure that Pods are not in a Pending state due to scheduling issues or container creation failures, and report relevant details for diagnostics |
| Find Pods with missing configmap | K8S102 | pod | Pod, ConfigMap | High | Ensure the presence of referenced ConfigMaps in Pod containers and volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Find Pods with missing secrets | K8S105 | pod | Pod, Secret | High | Ensure the presence of referenced Secrets in Pod containers, reporting failures for any missing Secret for all the namespaces |
| Insufficient PIDs on Node | K8S502 | node | Performance | High | Check if the nodes have remaining PIDs less than a set threshold |
| Kubernetes Node Out-of-Memory Check | K8S503 | node | Performance | High | Checks if any Kubernetes node is using more than 85% of its memory capacity. |
| Validate configmap existence in Statefulset | K8S1001 | statefulset | StatefulSet | High | Ensure the existence of referenced ConfigMaps in StatefulSet volume claims and template volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Validate cronjob starting deadline | K8S1101 | cronjob | CronJob | High | Ensure CronJobs have a non-negative starting deadline, reporting failures for negative values for all the namespaces |
| Validate existence of configmaps in daemonsets | K8S601 | daemonset | DaemonSet, ConfigMap | High | Ensure the presence of referenced ConfigMaps in Daemonset volumes, reporting failures for any missing ConfigMap for all the namespaces |
| Verify StatefulSet has valid service | K8S1002 | statefulset | StatefulSet | High | Verify StatefulSet's service reference, ensuring it points to an existing service in all the namespaces, reporting failures for non-existent services |
| Verify StatefulSet has valid storageClass | K8S1003 | statefulset | StatefulSet | High | Validate StatefulSet's storage class, ensuring it references existing storage classes in the namespace, reporting failures for non-existent ones |
| Zero Scale Deployment Check | K8S802 | deployment | Availability | High | Verify that Deployments have a non-zero replica count, preventing unintentional scaling down to zero |
| Check if Kubernetes services have matching pod labels | K8S302 | service | Configuration | Medium | This check validates if Kubernetes service selectors match pod labels. This ensures proper routing & discovery of pods. |
| Pod template validation in DaemonSet | K8S602 | daemonset | Resource Management | Medium | Checks that the Pod template within a DaemonSet is configured correctly according to certain threshold values. |
| Services Target Port Match | K8S303 | service | Diagnostic | Medium | This check identifies service ports that do not match their target ports |
| Validate that network policies are in place and configured correctly | K8S1201 | networkpolicy | Network Security | Medium | Verify Network Policy configurations, highlighting issues if policies allow traffic to all pods or if not applied to any specific pods |
| Zero scale detected in statefulset | K8S1004 | statefulset | Availability | Medium | Check to ensure that no StatefulSets are scaled to zero as it might hamper availability. |
| Find unused DaemonSet | K8S604 | daemonset | DaemonSet, Cost, Resource Optimization | Low | Any DaemonSet that has been created but has no associated pods and remained unused for over 30 days. |
| Validate cronjobs schedule and state | K8S1102 | cronjob | CronJob | Low | Ensure CronJobs have valid schedules and are not suspended, reporting failures for any invalid schedules or suspended jobs for all the namespaces |

#### mysql checks
| Check | ID | Service | Category | Severity | Description |
|---|---|---|---|---|---|
| Checks max used connections | MYSQL101 | global | Connection, Thread | High | Checks max used connections reaching max count |

<!-- GENERATED_CHECKS_SECTION_END -->


### Built With

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
* Python >= 3.10
* [OpenAI API Key](https://platform.openai.com/account/api-keys) - to have AI based functionality enabled

### Installation

1. Get distibution on your machine:
    * Run `pip` command to install `unctl` from [PyPI](https://pypi.org/project/unctl/)
        ```sh
        pip install unctl
        ```
2. (optional) Set OpenAI API key to be able to use `--explain (-e)` option
   ```sh
   export OPENAI_API_KEY=<your api key>
   ```

#### Kubernetes

1. (optional) Set `KUBECONFIG` variable to specific location other than default:
   ```sh
   export KUBECONFIG=<path to kube config file>
   ```
2. Run unctl command to see list of options:
   ```sh
   unctl k8s -h
   ```

#### MySQL

1. `unctl` is using `~/.my.cnf` as [config path](https://dev.mysql.com/doc/refman/8.0/en/option-files.html).
2. Run unctl command to see list of options:
   ```sh
   unctl mysql -h
   ```

### Config file

By default `unctl` is looking at `~/.config/unctl/config.yaml`. Otherwise it would use default values.

To specify path to the config file use `--config` option:

```sh
unctl --config <path to file> {provider} ...
```

**Note:** CLI options will overwrite values in config file

#### Anonymisation

This section allows to handle data manipulation sending to 3rd party services in order to hide PII or any other sensitive data:
- `masks` - list of rules to mask data. Can be extended with own regex patterns. By default there are 2 rules present in the config: `email` and `ip_address`. 

Example:
```yaml
anonymisation:
  masks:
    - name: email
      pattern: \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
    - name: ip_address
      pattern: \b(?:\d{1,3}\.){3}\d{1,3}\b
```

#### Filter

This section allows to set filters for your scan options:
- `failed_only` - shows only failed checks in the report when `true`. Default is `false`
- `checks` - list of checks IDs to run scan for specific checks only. If value is `[]` or missed than filter considered as disabled. Default is `[]`
- `categories` - list of checks categories to run scan. If value is `[]` or missed than filter considered as disabled. Default is `[]`
- `services` - list of checks services to run scan. If value is `[]` or missed than filter considered as disabled. Default is `[]`

Example:
```yaml
filter:
  failed_only: false
  checks:
    - K8S101
    - K8S203
  categories:
    - Health
  services:
    - pod
    - deployment
```

#### Interactive mode

Section is reponsible for interactive mode configuration:
- `prompt` - defines whether ask user to enter in the interactive mode after report is done. Default is `true`

Example:
```yaml
interactive:
  prompt: true
```

#### Muting

Section is taking care of muting particular checks and objects:
- `checks` - list of check IDs which will be ignored by the scan. If value is `[]` or missed than filter considered as disabled. Default is `[]`
- `objects` - set of objects with list of specific check IDs which should be ignored. If value is `{}` or missed than filter considered as disabled. Default is `{}`

Example:
```yaml
ignore:
  checks: 
    - K8S101
  objects:
    "some-object-name-1": [] # ignore object for all checks
    "some-object-name-2":    # ignore object for the specific checks
      - K8S203
```

## Usage

### unctl
```sh
% unctl -h
usage: unctl [-h] [-v] [--config CONFIG [CONFIG ...]] {k8s,mysql} ...

          Welcome to unSkript CLI Interface 

options:
  -h, --help            show this help message and exit
  -v, --version         show program`s version number and exit
  --config CONFIG [CONFIG ...]
                        Specify path to the unctl config file

unctl available providers:
  {k8s,mysql}

To see the different available options on a specific provider, run:
    unctl {provider} -h|--help
```

### Provider
```sh
% unctl {provider} -h
usage: unctl k8s [-h] [-s] [-e] [-f] [-c CHECKS [CHECKS ...]] [--sort-by {object,check}] [--categories CATEGORIES [CATEGORIES ...]] [--services SERVICES [SERVICES ...]] [-l]
                 [--no-interactive] [--list-categories] [--list-services] [-r] [--ignore IGNORE [IGNORE ...]] [--ignore-objects IGNORE_OBJECTS [IGNORE_OBJECTS ...]]

options:
  -h, --help            show this help message and exit
  -s, --scan            Run a provider scan
  -e, --explain         Explain failures using AI
  -f, --failing-only    Show only failing checks
  -c CHECKS [CHECKS ...], --checks CHECKS [CHECKS ...]
                        Filter checks by IDs
  --sort-by {object,check}
                        Sort results by 'object' (default) or 'check'
  --categories CATEGORIES [CATEGORIES ...]
                        Filter checks by category
  --services SERVICES [SERVICES ...]
                        Filter checks by services
  -l, --list-checks     List available checks
  --no-interactive      Interactive mode is not allowed. Prompts will be skipped
  --list-categories     List available categories
  --list-services       List available services
  -r, --remediate       Create remediation plan
  --ignore IGNORE [IGNORE ...]
                        Ignoring one or more checks by ID
  --ignore-objects IGNORE_OBJECTS [IGNORE_OBJECTS ...]
                        Ignoring one or more objects by name
```

<!-- ROADMAP -->
## Roadmap

- [ ] K8s checks - in progress
- [ ] MySQL checks - in progress
- [ ] Elastic Search checks
- [ ] AWS checks
- [ ] GCP checks

<!-- CONTACT -->
## Contact

Abhishek Saxena: abhishek@unskript.com

Official website: https://unskript.com/
