from raft.tasks import Task
from raft.context import Context


class AzureTask(Task):
    def __call__(self, *args, **kwargs):
        from azure.identity import ClientSecretCredential
        from azure.identity import InteractiveBrowserCredential
        from azure.identity import TokenCachePersistenceOptions
        from ..base.utils import get_context_value
        from ..base.utils import notice, notice_end
        ctx = args[0]
        has_context = isinstance(ctx, Context)
        client_id = kwargs.get('client_id')
        client_secret = kwargs.get('client_secret')
        tenant_id = kwargs.get('tenant_id')
        creds = kwargs.get('creds')
        if has_context:
            client_id = client_id or get_context_value(ctx, 'azure.client_id')
            client_secret = client_secret or get_context_value(ctx, 'azure.client_secret')
            tenant_id = tenant_id or get_context_value(ctx, 'azure.tenant_id')
        notice('client_id')
        notice_end(client_id)
        notice('tenant_id')
        notice_end(tenant_id)
        if not creds and client_id and client_secret and tenant_id:
            creds = ClientSecretCredential(tenant_id, client_id, client_secret)
        elif not creds:
            notice('using interactive credential')
            cache_options = TokenCachePersistenceOptions()
            creds = InteractiveBrowserCredential(
                tenant_id=tenant_id,
                cache_persistence_options=cache_options)
            notice_end()
        kwargs['creds'] = creds
        return super().__call__(*args, **kwargs)
