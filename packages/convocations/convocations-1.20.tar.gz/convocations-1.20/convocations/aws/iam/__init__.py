from getpass import getpass
from raft.tasks import task

from ...base.utils import notice, notice_end, print_table
from ..base import AwsTask


__all__ = [
    'add_user',
    'set_password',
]


@task(klass=AwsTask)
def add_user(ctx, username, group, session=None, **kwargs):
    """
    Adds a user to the specified group
    """
    notice(f'creating user {username}')
    iam = session.resource('iam')
    user = iam.User(username)
    user_created = False
    try:
        user.load()
        notice_end('found')
    except iam.meta.client.exceptions.NoSuchEntityException:
        user.create()
        user.reload()
        notice_end('created')

    notice(f'has group {group}?')
    has_group = False
    for x in user.groups.all():
        if x.name.lower() == group.lower():
            has_group = True
            break
    notice_end(f'{has_group}')

    if not has_group:
        notice(f'adding {username} to {group}')
        user.add_group(GroupName=group)
        notice_end()

    if user_created:
        set_password(ctx, username, session=session)


@task(klass=AwsTask)
def list_users(ctx, username=None, session=None, **kwargs):
    """
    Adds a user to the specified group
    """
    from ..base import yielder
    notice('getting users')
    iam = session.client('iam')
    users = yielder(iam, 'list_users', session=session)
    users = list(users)
    notice_end(f'{len(users)}')
    st = (username or '').lower()
    header = [ 'username', 'userid',  ]
    rows = []
    for x in users:
        username = x['UserName']
        if st in username.lower():
            rows.append([
                username,
                x['UserId'],
            ])
    print_table(header, rows)


@task(klass=AwsTask)
def set_password(ctx, username, session=None):
    """
    sets the password for the provided username
    """
    iam = session.resource('iam')
    user = iam.User(username)
    notice(f'loading user {username}')
    try:
        user.load()
        notice_end('found')
    except iam.meta.client.exceptions.NoSuchEntityException:
        notice_end('not found')
        return

    notice('profile exists?')
    profile = user.LoginProfile()
    try:
        profile.load()
        fn = profile.update
        notice_end('yes')
    except iam.meta.client.exceptions.NoSuchEntityException:
        fn = profile.create
        notice_end('no')
    password = getpass('Please enter your password: ')
    confirm = getpass('Confirm                   : ')
    if password == confirm:
        notice('updating password')
        fn(Password=password)
        notice_end()
    else:
        notice_end('passwords do not match')

