# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 08:52:22 2018

@author: daukes
"""

import os
from git import Repo
import git
from github import Github
import yaml
import sys



def clean_path(path_in):
    path_out = os.path.normpath(os.path.abspath(os.path.expanduser(path_in)))
    return path_out


if hasattr(sys, 'frozen'):
    module_path = os.path.normpath(os.path.join(os.path.dirname(sys.executable),''))
else:
    module_path = sys.modules['git_manage'].__path__[0]

support_path = clean_path(os.path.join(module_path, 'support'))
personal_config_folder = clean_path('~/.config/gitman')
personal_config_path = clean_path(os.path.join(personal_config_folder,'config.yaml'))
package_config_path = clean_path(os.path.join(support_path,'config.yaml'))

def new_user():
    print('Enter the username')
    user = input('username: ')
    token = input('token: ')
    add = input('add user info to config? (y/n)')
    add = add.lower()=='y'
    return user,token,add



def process_command(args):
    module_path = ''
    
    potential_file_locations = [args.config_f,personal_config_path,package_config_path]
    potential_file_locations = [item for item in potential_file_locations if item is not None]

    for ii,item in enumerate(potential_file_locations):
        try:    
            item = clean_path(item)
            with open(item) as f:
                config = yaml.load(f,Loader=yaml.Loader)
            break
        except TypeError as e:
            if ii==len(potential_file_locations)-1:
                raise Exception('config file not found')
        except FileNotFoundError as e:
            if ii==len(potential_file_locations)-1:
                raise Exception('config file not found')
            
    p1 = clean_path(config['index_location'])

    exclude = config['exclude_local']
    exclude = [clean_path(item) for item in exclude]

    exclude_mod = exclude[:]
    exclude_mod.extend([clean_path(item) for item in config['archive_path']])

    index_cache_path = clean_path(config['index_cache'])
        
    # print('Excluded Paths:', str(exclude_mod))


    if args.command == 'pull':

        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        git_list = fetch(git_list,args.verbose)
        check_unmatched(git_list,args.verbose)

    elif args.command == 'status':
        
        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        dict1 = check_dirty(git_list,args.verbose)
        if args.verbose:
            s = yaml.dump(dict1)
            print(s)
        else:
            del dict1['git_list']
            s = yaml.dump(dict1)
            print(s)
        # print('Dirty:')
        # for item in dirty:
            # print(item)
        # print('---------')
        # print('No Path:')
        # for item,e in no_path:
            # print(item,e)
        
    elif args.command in ['branch-status','bs','branch_status']:

        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        dict1 = check_unmatched(git_list,args.verbose)
        del dict1['missing_local_branches']
        s = yaml.dump(dict1)
        print(s)

    elif args.command in ['find-remote-branches']:
        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        dict1 = check_unmatched(git_list,args.verbose)
        s = yaml.dump(dict1['missing_local_branches'])
        print(s)
        
    elif args.command in ['list-remotes']:
        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        dict1 = list_remotes(git_list,args.verbose)
        s = yaml.dump(dict1)
        print(s)

    elif args.command in ['list-upstream']:
        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        dict1 = list_upstream(git_list,args.verbose)
        s = yaml.dump(dict1)
        print(s)

    elif args.command in ['list-local-branches']:
        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        dict1 = list_local_branches(git_list,args.verbose)
        s = yaml.dump(dict1)
        print(s)

    elif args.command == 'clone':
        if args.repo is None:
            git_list = find_repos(p1,search_depth = config['index_depth'],exclude=exclude)
            

            if args.user=='all':
                for username,token in config['github_accounts'].items():
                    print('User: ',username)
                    retrieve_nonlocal_repos(git_list,clean_path(config['clone_path']), user=username,token = token,exclude_remote=config['exclude_remote'],verbose = args.verbose)    
            elif args.user == 'new':        
                user,token,add = new_user()
                retrieve_nonlocal_repos(git_list,clean_path(config['clone_path']),user,token,exclude_remote=config['exclude_remote'],verbose = args.verbose)    
                if add:
                    try:
                        config['github_accounts'][user]=token
                    except KeyError:
                        config['github_accounts']={}
                        config['github_accounts'][user]=token
            else:
                token = config['github_accounts'][args.user]
                retrieve_nonlocal_repos(git_list,clean_path(config['clone_path']), user=args.user,token = token,exclude_remote=config['exclude_remote'],verbose = args.verbose)    
        else:
            
            for user,token in config['github_accounts'].items():
                git_list,owners,owner_repo_dict = list_remote_repos(user=user,token = token)
                if args.repo in owners:
                    repo_list = [local_ssh_from_url_user(args.repo, user)]
                    clone_list(repo_list,clean_path(config['clone_path']),owners,user)    




    elif (args.command == 'list-github'):
        all_users = {}
        if args.user=='all':
            for user,token in config['github_accounts'].items():
                git_list,owners,owner_repo_dict = list_remote_repos(user=user,token = token)
                all_users[user]=owner_repo_dict
                
        elif args.user == 'new':        
            user,token,save = new_user()
            git_list,owners,owner_repo_dict = list_remote_repos(user=user,token = token)
            all_users[user]=owner_repo_dict

            if save:
                try:
                    config['github_accounts'][user]=token
                except KeyError:
                    config['github_accounts']={}
                    config['github_accounts'][user]=token
        else:
            token = config['github_accounts'][args.user]
            git_list,owners,owner_repo_dict = list_remote_repos(user=args.user,token = token)
            all_users[args.user]=owner_repo_dict
        
        print(yaml.dump(all_users))

    elif (args.command == 'list-github-nonlocal'):

        git_list = find_repos(p1,search_depth = config['index_depth'],exclude=exclude)

        # all_users = {}
        all_repos = []
        if args.user=='all':
            for user,token in config['github_accounts'].items():
                local_git_list,owners,owner_repo_dict = list_nonlocal_repos(git_list,user=user,token = token)
                # all_users[user]=owner_repo_dict
                all_repos.extend(local_git_list)
        elif args.user == 'new':        
            user,token,save = new_user()
            local_git_list,owners,owner_repo_dict = list_nonlocal_repos(git_list,user=user,token = token)
            # all_users[user]=owner_repo_dict
            all_repos.extend(local_git_list)

            if save:
                try:
                    config['github_accounts'][user]=token
                except KeyError:
                    config['github_accounts']={}
                    config['github_accounts'][user]=token
        else:
            token = config['github_accounts'][args.user]
            local_git_list,owners,owner_repo_dict = list_nonlocal_repos(git_list,user=args.user,token = token)
            # all_users[args.user]=owner_repo_dict
            all_repos.extend(local_git_list)

        all_repos = [remote_url_from_ssh_address(item) for item in all_repos]        
        print(yaml.dump(all_repos))

    elif args.command == 'reset':

        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        reset_branches(git_list)

    elif args.command == 'list-active-branch':

        git_list = index_git_list(p1,args.index,index_cache_path,config['index_depth'],exclude_mod)

        current_branch = get_current_branch(git_list)
        s = yaml.dump(current_branch)
        print(s)
    
    elif args.command == 'index':
    
        git_list = index_git_list(p1,True,index_cache_path,config['index_depth'],exclude_mod)
        if args.verbose:
            s = yaml.dump(git_list)
            print(s)

    elif args.command == 'list':
        git_list = index_git_list(p1,True,index_cache_path,config['index_depth'],exclude_mod)
        s = yaml.dump(git_list)
        print(s)

    elif args.command == 'exclude':
    
        path = clean_path(os.curdir)
        config['exclude_local'].append(path)
        print(path)
    
    else:
        raise(Exception('command does not exist'))        
        
    if args.config_f is None:
        config_save_path = personal_config_path
        if not os.path.exists(personal_config_folder):
            os.makedirs(personal_config_folder)
    else:
        config_save_path = args.config_f
    
    config_save_path = clean_path(config_save_path)
    
    if args.save_config:
        with open(config_save_path,'w') as f:
            yaml.dump(config,f)
    



def index_git_list(p1,force_index,index_cache_path,index_depth,exclude):
    if (force_index) or (not os.path.exists(index_cache_path)):
        git_list = find_repos(p1,search_depth = index_depth,exclude=exclude)
        with open(index_cache_path,'w') as f:
            yaml.dump(git_list,f)
    else:
        with open(index_cache_path) as f:
            git_list=yaml.load(f,Loader=yaml.Loader)
    return git_list


def retrieve_nonlocal_repos(git_list,repo_path,user,token,exclude_remote = None,verbose=True):
    if not (os.path.exists(repo_path) and os.path.isdir(repo_path)):
        os.mkdir(repo_path)

    if verbose:
        print('local gits: ', git_list)
    nonlocal_github_urls,owners,owner_repo_dict = list_nonlocal_repos(git_list,user,token,verbose)
    remaining =list(set(nonlocal_github_urls) - set(format_repo_list(exclude_remote,destination_format='ssh',user=user)))
    if verbose:
        print('diff: ', remaining)
    
    clone_list(remaining,repo_path,owners,user)    

def list_nonlocal_repos(git_list,user,token,verbose=False):
    gits_remote_formatted,owners,owner_repo_dict = list_remote_repos(user, token,verbose,format_local=True)
    nonlocal_github_urls=diff(git_list,gits_remote_formatted)
    return nonlocal_github_urls,owners,owner_repo_dict

def list_remote_repos(user,token,verbose=False,format_local=False):
    gits_remote,owners,owner_repo_dict = scan_github(token)
    if verbose:
        print('remote gits: ', gits_remote)
    if format_local:
        gits_remote = [local_ssh_from_url_user(item, user) for item in gits_remote]
    return gits_remote,owners,owner_repo_dict

def get_all_repos(token):
    g = Github(token)

    all_repos =  list(g.get_user().get_repos())
    return all_repos 
    
def scan_github(token):
    all_gits = []
    owners = {}
    owner_repo_dict = {}
    for repo in get_all_repos(token):
        all_gits.append(repo.clone_url)
        owners[repo.clone_url]=repo.owner.login
        try:
            owner_repo_dict[repo.owner.login].append(repo.clone_url)
        except KeyError:
            owner_repo_dict[repo.owner.login] = []
            owner_repo_dict[repo.owner.login].append(repo.clone_url)
    return all_gits,owners,owner_repo_dict

def diff(local,github):    
    local_dict = {}
    local_urls = []
    for ii,item in enumerate(local):
    
        try:
            urls = []
            
            repo = Repo(item)
            for r in repo.remotes:
                urls.extend(r.urls)
            local_dict[item] = urls
            local_urls.extend(urls)
        except:
            pass        
    
    local_urls = set(local_urls)
    github_urls = set(github)
    
    nonlocal_github_urls =  list(github_urls-local_urls)
    return nonlocal_github_urls

def find_repos(search_path=None,search_depth=5,exclude=None):
    search_path = search_path or os.path.abspath(os.path.expanduser('~'))

    fp0 = os.path.normpath(os.path.abspath(search_path))
    base_depth = len(fp0.split(os.path.sep))
    
    exclude = exclude or [] 
    
    path_list = [search_path]
    git_list = []
    
    
    while len(path_list)>0:
        current_path = path_list.pop(0)
        fp = os.path.normpath(os.path.abspath(current_path))
        depth = len(fp.split(os.path.sep))
        
#        print(current_path)
        subpath = os.path.join(current_path,'.git')
        if os.path.isdir(subpath):
            git_list.append(current_path)
        else:
            if depth-base_depth<=search_depth:
                try:
                    subdirs = os.listdir(current_path)
                    subdirs = [os.path.join(current_path,item) for item in subdirs]
                    subdirs = [item for item in subdirs if os.path.isdir(item)]
                    subdirs = [item for item in subdirs if not item in exclude]
                    
                    path_list.extend(subdirs)
                except PermissionError:
                    pass
                except FileNotFoundError:
                    pass
    return git_list

def is_ssh_format(item):
    return item.startswith('git@')

def is_github_clone_format(item):
    return item.startswith('https://github.com/')

def format_repo_list(list_in,destination_format='github',user=None):
    list_out = []
    for item in list_in:
        if is_ssh_format(item):
            if destination_format=='github':
                list_out.append(remote_url_from_ssh_address(item))
            elif destination_format=='ssh':
                list_out.append(item)
            else:
                raise(Exception('format not specified'))
        elif is_github_clone_format(item):
            if destination_format=='github':
                list_out.append(item)
            elif destination_format=='ssh':
                list_out.append(local_ssh_from_url_user(item, user))                
            else:
                raise(Exception('format not specified'))
        else:
            raise(Exception('format not identified'))
    return list_out
            

def local_ssh_from_url_user(url,user):
        a,b = url.split('github.com/')
        # b1,b2 = b.split('/')
        # owner = b1
        # reponame = b2
        # reponame = (url.split('/')[-1])
        # repoowner = (url.split('/')[-2])
        newurl = 'git@'+user+'.github.com:'+b
        return newurl
    
def remote_urls_from_folder(local_folder):
    r = Repo(local_folder)
    remote = r.remote()
    ssh = remote.url
    return remote_url_from_ssh_address(ssh)

def remote_url_from_ssh_address(local_ssh_address):
    a = 'https://github.com/'
    b = local_ssh_address.split(':')[-1]
    c = ''.join([a,b])
    return c

def clone_list(repo_addresses,full_path,owners,user):
    owners2 = dict([(local_ssh_from_url_user(url, user),owners[url]) for url in owners.keys()])
    for url in repo_addresses:
        reponame = (url.split('/')[-1])
        name=reponame.split('.')
        name='.'.join([item for item in name if item!='git'])
        
        owner = owners2[url]
        ii = 1
        local_dest = os.path.normpath(os.path.join(full_path,owner,name))
        
        while (os.path.exists(local_dest) and os.path.isdir(local_dest)):
            name = name+'_'+str(ii)
            local_dest = os.path.normpath(os.path.join(full_path,owner,name))
            ii+=1
        os.makedirs(local_dest)
            
        
        print('cloning url:',url,'to: ',local_dest)

        repo = Repo.clone_from(url,local_dest)

def list_remotes(git_list,verbose=False):

    dict1={}

    ll = len(git_list)
    for ii,item in enumerate(git_list):
        if verbose:
            print('{0:.0f}/{1:.0f}'.format(ii+1,ll),item)
        try:
            repo = Repo(item)
            remotes = repo.remotes
            remote_urls = dict([(remote.name,[url for url in remote.urls]) for remote in remotes])
            dict1[item]=remote_urls
        except git.NoSuchPathError as e:        
            print(e)
    return dict1

def list_upstream(git_list,verbose=False):

    dict1={}

    ll = len(git_list)
    for ii,item in enumerate(git_list):
        if verbose:
            print('{0:.0f}/{1:.0f}'.format(ii+1,ll),item)
        try:
            repo = Repo(item)
            branches = repo.branches
            tracking_branches = dict([(branch.name,branch.tracking_branch().path) for branch in repo.branches])
            dict1[item]=tracking_branches
        except git.NoSuchPathError as e:        
            print(e)
    return dict1

def list_local_branches(git_list,verbose=False):

    dict1={}

    ll = len(git_list)
    for ii,item in enumerate(git_list):
        if verbose:
            print('{0:.0f}/{1:.0f}'.format(ii+1,ll),item)
        try:
            repo = Repo(item)
            branches = repo.branches
            branch_names= [branch.name for branch in branches]
            dict1[item]=branch_names
        except git.NoSuchPathError as e:        
            print(e)
    return dict1

def check_dirty(git_list,verbose=False):    
    
    dict1 = {}
    dict1['dirty'] = []
    dict1['no_path'] = []
    dict1['git_list']= []

    ll = len(git_list)
    for ii,item in enumerate(git_list):
        if verbose:
            print('{0:.0f}/{1:.0f}'.format(ii+1,ll),item)
        try:
            repo = Repo(item)
            if repo.is_dirty(untracked_files=True):
                dict1['dirty'].append(item)
            dict1['git_list'].append(item)
        except git.NoSuchPathError as e:        
            dict1['no_path'].append((item,e))

    # if verbose:
        # print('---------')


    # return git_list2,dirty,no_path
    
    return dict1

def get_current_branch(git_list):    
    current_branch={}

    ll = len(git_list)
    for ii,item in enumerate(git_list):
        print('{0:.0f}/{1:.0f}'.format(ii+1,ll),item)
        repo = Repo(item)
        current_branch[item]=str(repo.active_branch)

    return current_branch

def fetch(git_list,verbose = False):    

    git_command_errors = {}
    git_list2 = []

    ll = len(git_list)
    for ii,item in enumerate(git_list):
        print('{0:.0f}/{1:.0f}'.format(ii+1,ll),item)
        try:
            repo = Repo(item)
            
            fetches = repo.remotes[0].fetch()
            # if repo.commit().hexsha != fetches[0].commit.hexsha:
                # unmatched.append(item)
            git_list2.append(item)
        except git.NoSuchPathError as e:     
            try:   
                git_command_errors[str(e)].append(item)
            except KeyError:
                git_command_errors[str(e)]=[]
                git_command_errors[str(e)].append(item)
        except git.GitCommandError as e:        
            try:   
                git_command_errors[str(e)].append(item)
            except KeyError:
                git_command_errors[str(e)]=[]
                git_command_errors[str(e)].append(item)
            
    if len(git_command_errors)>0:

        print("------------------")
        print("Errors:")
        print(yaml.dump(git_command_errors))
        print("------------------")
    
    
    return git_list2
    
def check_unmatched(git_list,verbose=False):    
    
    dict1 = {}
    dict1['git_command_error'] = {}
    dict1['no_path'] = []
    dict1['missing_local_branches'] = {}
    dict1['missing_remote_branches'] = {}
    dict1['unsynced_branches'] = {}

    ll = len(git_list)
    for ii,repo_path in enumerate(git_list):
        if verbose:
            print('{0:.0f}/{1:.0f}'.format(ii+1,ll),repo_path)
        try:
            r = Repo(repo_path)
            
            remote_branches = []
            for rr in r.remote().refs:
                if not rr.name.lower().endswith('/head'):
                    remote_branches.append(rr)
            remote_branches_s = set(remote_branches)
            
            
            for branch in r.branches:
                if branch.tracking_branch() is not None:
                    try:
                        if branch.commit.hexsha != branch.tracking_branch().commit.hexsha:
                            try:
                                dict1['unsynced_branches'][repo_path].append(branch.name)
                            except KeyError:
                                dict1['unsynced_branches'][repo_path]=[]
                                dict1['unsynced_branches'][repo_path].append(branch.name)
                    except ValueError:
                        try:
                            dict1['missing_remote_branches'][repo_path].append(branch.name)
                        except KeyError:
                            dict1['missing_remote_branches'][repo_path]=[]
                            dict1['missing_remote_branches'][repo_path].append(branch.name)

                else:
                    try:
                        dict1['missing_remote_branches'][repo_path].append(branch.name)
                    except KeyError:
                        dict1['missing_remote_branches'][repo_path]=[]
                        dict1['missing_remote_branches'][repo_path].append(branch.name)
                
            b_s = [branch.tracking_branch() for branch in r.branches]
            b_s = [branch for branch in b_s if branch is not None]
            b_s = set(b_s)
            not_local = list(remote_branches_s.difference(b_s))
            for ref in not_local:
                try:
                    dict1['missing_local_branches'][repo_path].append(ref.name)
                except KeyError:
                    dict1['missing_local_branches'][repo_path]=[]
                    dict1['missing_local_branches'][repo_path].append(ref.name)
                        
            
        except git.NoSuchPathError as e:        
            dict1['no_path'].append(repo_path)
                
        except git.GitCommandError as e:        
            dict1['git_command_error'].append(repo_path)
                
    
    # print('---------')
    # print('Missing Local Branches:')
    # for item in dict1['missing_local_branches']:
    #     print(item)
    # print('---------')
    # print('Missing Remote Branches:')
    # for item in dict1['missing_remote_branches']:
    #     print(item)
    # print('---------')
    # print('Branches Unsynced:')
    # for item in dict1['unsynced_branches']:
    #     print(item)
    # print('---------')
    # print('No Path:')
    # for item,e in dict1['no_path']:
    #     print(item,e)
    # print('---------')
    # print('Git Command:')
    # for item,e in dict1['git_command_error']:
    #     print(item,e)
    # print('---------')

    # return git_list2,unmatched,no_path,git_command_error   

    return dict1

def reset_branches(git_list,verbose=True):    

    git_command_error = []
    no_path = []
    
    ll = len(git_list)
    for ii,repo_path in enumerate(git_list):
        print('{0:.0f}/{1:.0f}'.format(ii+1,ll),repo_path)
        try:
            r = Repo(repo_path)
            
            # remote_branches = []
            # for rr in r.remote().refs:
                # if not rr.name.lower().endswith('/head'):
                    # remote_branches.append(rr)
            # remote_branches_s = set(remote_branches)
            
            active_branch = r.active_branch
            
            try:
                
                if not r.is_dirty(untracked_files=True):
                    
                    for branch in r.branches:
                        if branch.tracking_branch() is not None:
    
                            tb = branch.tracking_branch()
                            if r.is_ancestor(branch.commit,tb.commit):
                                if branch.commit.hexsha != tb.commit.hexsha:
                                    branch.checkout()
                                    r.head.reset(tb.commit,index=True,working_tree=True)
                                    print('Yes')
            except Exception as e:
                print(e)
            finally:
                active_branch.checkout()
        except git.NoSuchPathError as e:        
         no_path.append((repo_path,e))
        except git.GitCommandError as e:        
            git_command_error.append((repo_path,e))   

if __name__=='__main__':
    # r = get_all_repos()
    pass
    
