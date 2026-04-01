
variable "kubeconfig_path" {
  description = "Path to kubeconfig used by oc/kubectl"
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "Optional kubeconfig context name (leave null to use current/default)"
  type        = string
  default     = null
}
