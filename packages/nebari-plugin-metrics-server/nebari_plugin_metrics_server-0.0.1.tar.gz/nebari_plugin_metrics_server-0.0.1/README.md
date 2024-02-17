
# Nebari Plugin - Metrics Server

[![PyPI - Version](https://img.shields.io/pypi/v/nebari-plugin-metrics-server.svg)](https://pypi.org/project/nebari-plugin-metrics-server)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nebari-plugin-metrics-server.svg)](https://pypi.org/project/nebari-plugin-metrics-server)

-----

## Overview
This plugin integrates Metrics Server into the Nebari platform, allowing container resource metrics for Kubernetes built-in autoscaling pipelines within Nebari. Utilizing Python, Terraform, and Helm, the plugin provides a configurable deployment.

## Design and Architecture
The plugin follows a modular design, leveraging Terraform to define the deployment of Metrics Server within a Kubernetes cluster. Key component is:
**Terraform Configuration**: Defines variables and Helm release for deployment.

## Installation Instructions


```console
pip install nebari-plugin-metrics-server
```


## Usage Instructions
**Configurations**: Various configurations are available, including name, namespace, and affinity settings.

## Configuration Details

### Public
Configuration of the Metrics Server plugin is controlled through the `metrics_server` section of the `nebari-config.yaml` for the environment.

``` yaml
metrics_server:
  # helm release name - default metrics-server
  name: metrics-server
  # target namespace - default kube-system
  namespace: kube-system
  # configure default affinity/selector for chart components
  affinity:
    enabled: true # default
    selector: general # default
    # -- or --
    selector:
      default: general
      worker: worker
      db: general
      auth: general
  # helm chart values overrides
  values: {}
```

### Internal
The following configuration values apply to the internally managed terraform module and are indirectly controlled through related values in `nebari-config.yaml`.

- `name`: Chart name for Helm release.
- `namespace`: Kubernetes namespace configuration.
- `affinity`: Affinity configuration for Helm release.
- `overrides`: Map for overriding default configurations.

## License

`nebari-plugin-metrics-server` is distributed under the terms of the [Apache](./LICENSE.md) license.