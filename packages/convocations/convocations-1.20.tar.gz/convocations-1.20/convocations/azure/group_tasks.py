import asyncio
from raft.tasks import task
from .base import AzureTask
from ..base.utils import notice, notice_end, print_table


@task(klass=AzureTask)
def groups(ctx, name, creds=None, quiet=False, members=False, **kwargs):
    """
    shows all groups with a substring of name
    """
    from msgraph.graph_service_client import GraphServiceClient
    from msgraph.generated.models.group_collection_response import (
        GroupCollectionResponse
    )
    from msgraph.generated.groups.groups_request_builder import (
        GroupsRequestBuilder as G,
    )
    name = (name or '').lower()
    client = GraphServiceClient(credentials=creds)
    name = (name or '').lower()
    result = []

    async def yield_groups(skip=0):
        params = G.GroupsRequestBuilderGetQueryParameters(
            count=True,
            top=999,
        )
        if name:
            notice('building search')
            pieces = name.split(' ')
            search_query = [ f'"displayName:{piece}"' for piece in pieces ]
            params.search = ' AND '.join(search_query)
            notice_end(params.search)
        builder = G.GroupsRequestBuilderGetRequestConfiguration(
            query_parameters=params,
            headers={
                'ConsistencyLevel': 'eventual',
            }
        )
        notice('executing search')
        response: GroupCollectionResponse = await client.groups.get(builder)
        notice_end(f'{response.odata_count}')
        for x in response.value:
            yield x
        if response.odata_next_link:
            async for x in yield_groups(skip + len(response.value)):
                yield x

    async def get_members(g):
        from msgraph.generated.groups.item.members.members_request_builder import MembersRequestBuilder as M
        params = M.MembersRequestBuilderGetQueryParameters(
            select=[ 'id', 'userPrincipalName' ],
        )
        builder = M.MembersRequestBuilderGetRequestConfiguration(
            query_parameters=params,
        )
        response = await client.groups.by_group_id(g.id).members.get(builder)
        return response

    async def get():
        async for x in yield_groups():
            result.append(x)
            if members:
                notice(f'members / {x.display_name}')
                member_response = await get_members(x)
                notice_end()
                x.members = member_response.value

    asyncio.run(get())
    if result and not quiet:
        header = [ 'group_id', 'name', 'type', ]
        if members:
            header.append('member_id')
            header.append('user_principal_name')
        rows = []
        for row in result:
            types = []
            if row.mail_enabled:
                types.append('mail')
            if row.security_enabled:
                types.append('security')
            if not members:
                rows.append([
                    row.id,
                    row.display_name,
                    '; '.join(types),
                ])
            elif not row.members:
                rows.append([
                    row.id,
                    row.display_name,
                    '; '.join(types),
                    '',
                    '',
                ])
            else:
                for member in row.members:
                    rows.append([
                        row.id,
                        row.display_name,
                        '; '.join(types),
                        member.id,
                        member.user_principal_name,
                    ])
        if not members:
            rows.sort(key=lambda lx: lx[1].lower())
        else:
            rows.sort(key=lambda lx: (lx[1].lower(), lx[4].lower()))
        print_table(header, rows)
    else:
        return result


