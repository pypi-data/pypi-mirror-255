# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

{
    "name": "Revenue Recognition",
    "version": "14.0.3.5.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "ssi_financial_accounting",
        "ssi_cost_accounting",
        "ssi_master_data_mixin",
        "ssi_service",
        "ssi_analytic_budget",
        "base_automation",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "security/ir_rule_data.xml",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "data/policy_template_data.xml",
        "data/approval_template_data.xml",
        "data/account_journal_data.xml",
        "data/ir_actions_server_data.xml",
        "data/base_automation_data.xml",
        "menu.xml",
        "views/account_analytic_account_views.xml",
        "views/service_contract_views.xml",
        "views/revenue_recognition_type_views.xml",
        "views/performance_obligation_acceptance_views.xml",
        "views/service_contract_performance_obligation_views.xml",
        "views/revenue_recognition_views.xml",
        "views/service_type_views.xml",
    ],
    "demo": [
        "demo/account_account_demo.xml",
        "demo/account_journal_demo.xml",
        "demo/product_usage_type_demo.xml",
        "demo/revenue_recognition_type_demo.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
