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
    timestamp         = timestamp()
    node_count        = length(local.nodes)
    node_names        = [for n in local.nodes : n.name]
    worker_only_nodes = [for n in local.worker_only_nodes : n.name]
  cordoned_worker_nodes = local.cordoned_worker_nodes }
}
