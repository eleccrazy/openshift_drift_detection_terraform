# Uses the same kubeconfig as oc (since oc already works)
provider "kubernetes" {
  config_path = pathexpand(var.kubeconfig_path)
  config_context = var.kubeconfig_context
}