# Copyright 2023-SomItCoop SCCL(<https://gitlab.com/somitcoop>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "SomItCoop ODOO helpdesk autoclose",
    "version": "12.0.0.1.0",
    "depends": [
        "helpdesk_mgmt",
    ],
    "author": "Som It Cooperatiu SCCL",
    "category": "Auth",
    "website": "https://gitlab.com/somitcoop/erp-research/odoo-helpdesk",
    "license": "AGPL-3",
    "summary": """
        ODOO helpdesk customizations for social cooperatives.
        Handle mails through ODOO and link them to knowledge.
    """,
    "data": [
        'views/helpdesk_ticket_stage_autoclose.xml',
        'data/helpdesk_autoclose_cron.xml'
    ],
    "application": False,
    "installable": True,
}
