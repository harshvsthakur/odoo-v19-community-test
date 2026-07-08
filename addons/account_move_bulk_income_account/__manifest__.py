{
    "name": "Bulk Update Income Account on Invoice",
    "version": "19.0.1.0.0",
    "summary": "Add a button to bulk-set the income account across all lines of a draft customer invoice",
    "description": """
Adds a header button on draft Customer Invoices that opens a confirmation
wizard to pick an income account and apply it to every product/service
line's account in one action.
""",
    "author": "Harshvsthakur",
    "license": "LGPL-3",
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/account_move_bulk_income_account_wizard_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
