import sys

import textwrap

from . import billing
from . import context
from . import connectors


def override_replace(metric, usage_override, usage_min, usage_max, usage_step):
    if usage_override is None:
        usage_override = []
    usage_min = None if usage_min is None else int(usage_min)
    usage_max = None if usage_max is None else int(usage_max)
    usage_step = None if usage_step is None else int(usage_step)
    for idx, x in enumerate(usage_override):
        if x["metric"] == metric:
            usage_override.remove(x)
    if usage_min is not None or usage_max or usage_step is not None:
        rec = {"metric": metric}
        if usage_min is not None:
            rec["min_quantity"] = usage_min
        if usage_max is not None:
            rec["max_quantity"] = usage_max
        if usage_step is not None:
            rec["step_quantity"] = usage_step
        usage_override.append(rec)
    return usage_override


def set_subscription_info(ctx, **kwargs):
    """Update various parameters associated with the subscription.
    e.g. the usage-metrics of min/max/step size."""
    result = billing.list_subscriptions(ctx, org_id=kwargs["org_id"])

    for bi in result.billing_subscriptions:
        billing_account_id = bi.spec.billing_account_id
        for org in bi.status.orgs:
            if org.id == kwargs["org_id"]:
                subscription_id = bi.metadata.id
                break

    if subscription_id is None:
        print(f"ERROR: could not find account info for {kwargs['org_id']}")
        sys.exit(1)

    subscription = billing.get_billing_subscription(
        ctx, billing_subscription_id=subscription_id
    )
    subscription_id = subscription.metadata.id
    usage_override = subscription.spec.usage_override

    usage_override = override_replace(
        "active_users",
        usage_override,
        kwargs["min_user"],
        kwargs["max_user"],
        kwargs["step_user"],
    )
    usage_override = override_replace(
        "active_connectors",
        usage_override,
        kwargs["min_connector"],
        kwargs["max_connector"],
        kwargs["step_connector"],
    )

    subscription.spec.usage_override = usage_override

    billing.update_subscription(
        ctx, billing_subscription_id=subscription_id, subscription=subscription
    )
    res = billing.create_usage_record(ctx, billing_account_id=billing_account_id)
    print(res)


def _show_billing(ctx, org, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    billing_account = apiclient.billing_api.get_billing_account(
        billing_account_id=org.billing_account_id
    )
    if kwargs["markdown"]:
        dl = "| "
    else:
        dl = " "
    if "billing_subscription_id" in org and org.billing_subscription_id is not None:
        subscription = apiclient.billing_api.get_subscription(
            billing_subscription_id=org.billing_subscription_id
        )

        cid = billing_account.spec.customer_id
        sid = subscription.spec.subscription_id
        surl = "https://dashboard.stripe.com"
        if kwargs["markdown"]:
            print(f"{dl}STRIPE ACCOUNT:   {dl}{cid:30} [link]({surl}/customers/{cid})")
            print(
                f"{dl}STRIPE SUBSCRIPT: {dl}{sid:30} [link]({surl}/subscriptions/{sid})"
            )
        else:
            print(f"{dl}STRIPE ACCOUNT:   {dl}{cid:30} {surl}/customers/{cid}")
            print(f"{dl}STRIPE SUBSCRIPT: {dl}{sid:30} {surl}/subscriptions/{sid}")


def _show_usage(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    metrics = apiclient.org_api.get_usage_metrics(org_id=kwargs["org_id"]).metrics
    if kwargs["markdown"]:
        dl = "| "
        print("")
    else:
        dl = " "
        print("USAGE")

    print(f"{dl}METRIC               {dl}PEAK    {dl}CURRENT")
    if kwargs["markdown"]:
        print(f"{dl}------               {dl}----    {dl}-------")

    for metric in metrics:
        tname = metric.type
        if metric.type == "fileshare":
            tname = "share"
        print(
            f"{dl}{tname:20} {dl}{metric.provisioned.peak:5}   {dl}{metric.provisioned.current:5}"  # noqa: E501
        )


def _show_auth(ctx, **kwargs):
    """Sign-in usage."""
    dt_from = "-30d"
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    query_results = apiclient.audits_api.list_auth_records(
        dt_from=dt_from,
        org_id=kwargs["org_id"],
        event_name="Authentication Request",
        limit=500,
    )
    odate = None
    pids = {}
    for rx in query_results.auth_audits:
        if odate is None or rx.time > odate:
            odate = rx.time
        if rx.event == "Success" and rx.result == "Success":
            pids[rx.client_id] = pids.get(rx.client_id, 0) + 1
    if kwargs["markdown"]:
        dl = "| "
        print("")
    else:
        dl = " "
    if len(pids):
        print("\n**APPROXIMATE AUTHENTICATION**\n")

        print(f"{dl}CLIENT-ID                             {dl}AUTHS")
        if kwargs["markdown"]:
            print("| ------------------------------------- | -----")
        for p in pids:
            print(f"{dl}{p:35}   {dl}{pids[p]:5}")
    else:
        print("NO AUTHENTICATION ACTIONS")
    if odate is None:
        print("\nNO AUTHENTICATION AUDIT IN TRAILING 30d")
    else:
        print(f"\nNEWEST AUTH RECORD: {odate.isoformat()}")


def remfl(s):
    s = s.split("\n", 1)[-1]
    if s.find("\n") == -1:
        return ""
    return s.rsplit("\n", 1)[0]


def _show_connectors(ctx, **kwargs):
    kw = {}
    kw["sort_by"] = ["metadata.created"]
    kw["org_id"] = kwargs["org_id"]
    kw["show_stats"] = True
    results = connectors.query(ctx, **kw)
    table = connectors.format_connectors_as_text(ctx, results, skip_sub_table=True, **kw)
    raw = table.get_string()

    if kwargs["markdown"]:
        print("\n**CONNECTORS**\n")
        print(remfl(raw).replace("+", "|"))
        print("")
    else:
        print("\nCONNECTORS")
        print(textwrap.indent(raw, "  "))


def _show_status(ctx, org, **kwargs):
    if org is None:
        token = context.get_token(ctx)
        apiclient = context.get_apiclient(ctx, token)
        org_id = kwargs["org_id"]
        org = apiclient.org_api.get_org(org_id=org_id)
    if kwargs["markdown"]:
        dl = "| "
        print("| USAGE | VALUES")
        print("| ----- | -----")
    else:
        dl = ""

    print(f"{dl}NAME:    {dl}{org.organisation}")
    print(f"{dl}ID:      {dl}{org.id}")
    print(f"{dl}CREATED: {dl}{org.created}")
    print(f"{dl}SHARD:   {dl}{org.shard}")
    print(f"{dl}ISSUER:  {dl}{org.issuer}")
    print(f"{dl}STATUS:  {dl}{org.admin_state}")
    print(f"{dl}CLUSTER: {dl}{org.cluster}")
    kwargs["org_id"] = org.id
    _show_billing(ctx, org, **kwargs)
    _show_usage(ctx, **kwargs)
    _show_auth(ctx, **kwargs)
    _show_connectors(ctx, **kwargs)


def status(ctx, **kwargs):
    """Show snapshot of this org, trial, billing, usage, status."""
    if "org_id" in kwargs and kwargs["org_id"] is not None:
        _show_status(ctx, org=None, **kwargs)
    if kwargs["email"]:
        token = context.get_token(ctx)
        apiclient = context.get_apiclient(ctx, token)
        params = {}
        params["limit"] = 500
        org = apiclient.org_api.list_orgs(**params)
        for org in org.orgs:
            if org.contact_email == kwargs["email"]:
                _show_status(ctx, org=org, **kwargs)
