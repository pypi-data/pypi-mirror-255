variable "{{data.route_tables}}" {}

module "{{data.vpc_id}}" {
  source         = "{{data.module_source}}"
  vpc_name       = "{{data.vpc_name}}"
  vpc_id         = "{{data.vpc_id}}"
{% if data.configure_spoke_gw_hs %}
  {% if data.vpc_cidr %}
  vpc_cidr       = "{{data.vpc_cidr}}"
  {% endif %}
{% else %}
  vpc_cidr       = {{data.vpc_cidr}}
{% endif %}
{% if data.enable_spoke_egress and data.snat_policies %}
  vpc_cidr_for_snat = {{data.vpc_cidr_for_snat}}
{% endif %}
{% if data.igw_id %}
  igw_id         = {{data.igw_id}}
{% else %}
  igw_id         = ""
{% endif %}
{% if data.configure_gw_name %}
  spoke_gw_name  = "{{data.spoke_gw_name}}"
{% endif %}
{% if data.spoke_ha == "false" %}
  spoke_ha       = false
{% endif %}
{% if data.configure_gw_name %}
  transit_gw     = "{{data.transit_gw_name}}"
{% endif %}
{% if data.configure_transit_gw_egress and data.transit_gw_egress_name %}
  transit_gw_egress = "{{data.transit_gw_egress_name}}"
{% endif %}
{% if data.configure_spoke_gw_hs %}
  avtx_cidrs     = {{data.avtx_cidrs}}
  {% if data.avtx_cidr %}
  avtx_cidr      = "{{data.avtx_cidr}}"
  {% endif %}
{% else %}
  avtx_cidr      = "{{data.avtx_cidr}}"
{% endif %}
  hpe            = {{data.hpe}}
  avtx_gw_size   = "{{data.spoke_gw_size}}"
  region         = "{{data.region}}"
  gw_zones       = {{data.gw_zones}}
{% if data.eips %}
  eips           = {{data.eips}}
{% endif %}
{% if data.enable_spoke_egress %}
  enable_spoke_egress = true
{% endif %}
{% if data.onboard_account %}
  account_name   = aviatrix_account.aws_customer.account_name
{% else %}
  account_name   = "{{data.account_name}}"
{% endif %}
  route_tables   = var.{{data.route_tables}}
{% if data.domain is not none %}
  domain         = "{{data.domain}}"
{% endif %}
{% if data.inspection is not none %}
  inspection     = {{data.inspection}}
{% endif %}
{% if data.spoke_advertisement is not none %}
  spoke_adv      = "{{data.spoke_advertisement}}"
{% endif %}
{% if data.spoke_routes is not none %}
  spoke_routes   = "{{data.spoke_routes}}"
{% endif %}
{% if data.spoke_gw_tags is not none %}
  tags           = {{data.spoke_gw_tags}}
{% endif %}
{% if data.encrypt is not none and data.encrypt == "true" %}
  encrypt        = {{data.encrypt}}
{% endif %}
{% if data.encrypt_key is not none and data.encrypt == "true" %}
  encrypt_key    = "{{data.encrypt_key}}"
{% endif %}
{% if not data.pre_v2_22_3 and data.max_hpe_performance is not none %}
  max_hpe_performance     = {{ data.max_hpe_performance }}
{% endif %}
  role_arn       = local.role_arn
  switch_traffic = false

  providers = { aws = {{data.providers}} }
}

{% if data.import_resources and data.igw_id %}
resource "aws_internet_gateway" "igw-{{data.vpc_id}}" {
  vpc_id = "{{ data.vpc_id }}"
  tags = {{data.igw_tags}}
  provider = {{ data.providers }}
  lifecycle {
    prevent_destroy = true
  }
}

{% endif %}