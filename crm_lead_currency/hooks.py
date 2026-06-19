def post_init_hook(env):
    """Align existing leads with their company currency during installation."""
    env.cr.execute(
        """
        UPDATE crm_lead AS lead
        SET customer_currency_id = COALESCE(company.currency_id, %s)
        FROM res_company AS company
        WHERE company.id = lead.company_id
            AND lead.customer_currency_id IS DISTINCT FROM company.currency_id
        """,
        (env.company.currency_id.id,),
    )
    env.cr.execute(
        """
        UPDATE crm_lead
        SET customer_currency_id = %s
        WHERE company_id IS NULL
            AND customer_currency_id IS DISTINCT FROM %s
        """,
        (env.company.currency_id.id, env.company.currency_id.id),
    )
