# READ-ONLY: If this works, Terraform is connected to the cluster API
data "kubernetes_nodes" "all" {}

# output "connected" {
#   value = length(data.kubernetes_nodes.all.nodes) > 0
# }
# output "node_count" {
#   value = length(data.kubernetes_nodes.all.nodes)
# }

# output "node_names" {
#   value = [for n in data.kubernetes_nodes.all.nodes : n.metadata[0].name]
# }

# HCO CR (HyperConverged in kubevirt-hyperconverged ns)
data "kubernetes_resource" "hco" {
  api_version = "hco.kubevirt.io/v1beta1"
  kind        = "HyperConverged"
  metadata {
    name      = "kubevirt-hyperconverged" # Default HCO name
    namespace = "openshift-cnv"           # Or kubevirt-hyperconverged
  }
}

# KubeVirt CR (managed by HCO)
data "kubernetes_resource" "kubevirt" {
  api_version = "kubevirt.io/v1"
  kind        = "KubeVirt"
  metadata {
    name      = "kubevirt-kubevirt-hyperconverged"
    namespace = "openshift-cnv"
  }
}

locals {
  # Normalize node facts we need
  nodes = [
    for n in data.kubernetes_nodes.all.nodes : {
      name          = n.metadata[0].name
      labels        = try(n.metadata[0].labels, {})
      unschedulable = try(n.spec[0].unschedulable, false)
    }
  ]

  # "Worker-only" nodes: worker label present AND NOT control-plane
  worker_only_nodes = [
    for n in local.nodes : n
    if contains(keys(n.labels), "node-role.kubernetes.io/worker") &&
    !contains(keys(n.labels), "node-role.kubernetes.io/control-plane")
  ]

  # Cordoned worker-only nodes
  cordoned_worker_nodes = [
  for n in local.worker_only_nodes : n.name if n.unschedulable]

  all_worker_nodes_schedulable = length(local.cordoned_worker_nodes) == 0

  # HCO facts we need
  # hco = {
  #   name = try(data.kubernetes_resource.hco.object.metadata[0].name, null)
  # }
  # namespace = try(data.kubernetes_resource.hco.object.metadata[0].namespace, null)
  # live_migration_config = {
  #   bandwidth_per_migration      = try(data.kubernetes_resource.hco.object.spec.liveMigrationConfig.bandwidthPerMigration, null)
  #   parallel_migrations_per_node = try(data.kubernetes_resource.hco.object.spec.liveMigrationConfig.parallelMigrationsPerNode, null)
  #   parallel_outgoing_migrations = try(data.kubernetes_resource.hco.object.spec.liveMigrationConfig.parallelOutboundMigrationsPerNode, null)
  #   parallel_incoming_migrations = try(data.kubernetes_resource.hco.object.spec.liveMigrationConfig.parallelInboundMigrationsPerNode, null)
  # }
  # eviction_strategy = try(data.kubernetes_resource.hco.object.spec.evictionStrategy, null)
  # feature_gates = {
  #   enabled = try(data.kubernetes_resource.hco.object.spec.featureGates.enable, [])
  # }

  # # KubeVirt facts we need
  # kubevirt = { name = try(data.kubernetes_resource.kubevirt.object.metadata[0].name, null)
  #   namespace = try(data.kubernetes_resource.kubevirt.object.metadata[0].namespace, null)
  #   cpu_model = try(data.kubernetes_resource.kubevirt.object.spec.configuration.cpuModel, null)
  # }

  hco = data.kubernetes_resource.hco.object
  kubevirt = data.kubernetes_resource.kubevirt.object

}

# output "worker_only_nodes" {
#   value = [for n in local.worker_only_nodes : n.name]
# }

# output "cordoned_worker_nodes" {
#   value = local.cordoned_worker_nodes
# }

# output "all_worker_nodes_schedulable" {
#   value = local.all_worker_nodes_schedulable
# }


output "facts" {
  value = {
    timestamp             = timestamp()
    node_count            = length(local.nodes)
    node_names            = [for n in local.nodes : n.name]
    worker_only_nodes     = [for n in local.worker_only_nodes : n.name]
    cordoned_worker_nodes = local.cordoned_worker_nodes
    hco                   = local.hco
    kubevirt              = local.kubevirt
  }
}
