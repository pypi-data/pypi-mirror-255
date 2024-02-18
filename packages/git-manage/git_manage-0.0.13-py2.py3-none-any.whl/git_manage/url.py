def is_ssh_format(item):
    return item.startswith('git@')

def is_github_clone_format(item):
    return item.startswith('https://github.com/')

# def remote_urls_from_folder(local_folder):
#     r = Repo(local_folder)
#     remote = r.remote()
#     ssh = remote.url
#     return remote_url_from_ssh_address(ssh)

def remote_url_from_ssh_address(local_ssh_address):
    a = 'https://github.com/'
    b = local_ssh_address.split(':')[-1]
    c = ''.join([a,b])
    return c


def local_ssh_from_url_user(url,user):
        a,b = url.split('github.com/')
        # b1,b2 = b.split('/')
        # owner = b1
        # reponame = b2
        # reponame = (url.split('/')[-1])
        # repoowner = (url.split('/')[-2])
        newurl = 'git@'+user+'.github.com:'+b
        return newurl