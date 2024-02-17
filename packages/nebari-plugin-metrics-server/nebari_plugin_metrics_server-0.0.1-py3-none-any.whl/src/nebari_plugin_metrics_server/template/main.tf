locals {
  name      = var.name
  namespace = var.namespace
  overrides = var.overrides

  affinity = var.affinity != null && lookup(var.affinity, "enabled", false) ? {
    enabled = true
    selector = try(
      { for k in ["default"] : k => length(var.affinity.selector[k]) > 0 ? var.affinity.selector[k] : var.affinity.selector.default },
      {
        default = var.affinity.selector
      },
    )
    } : {
    enabled  = false
    selector = null
  }

}

resource "helm_release" "metrics_server" {
  name             = local.name
  create_namespace = true
  namespace        = local.namespace

  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = "3.11.0"

  values = [
    yamlencode({
      affinity = local.affinity.enabled ? {
        nodeAffinity = {
          requiredDuringSchedulingIgnoredDuringExecution = {
            nodeSelectorTerms = [
              {
                matchExpressions = [
                  {
                    key      = "eks.amazonaws.com/nodegroup"
                    operator = "In"
                    values   = [local.affinity.selector.default]
                  }
                ]
              }
            ]
          }
        }
      } : {}
    }),
    yamlencode(lookup(local.overrides, "metrics-server", {})),
  ]
}