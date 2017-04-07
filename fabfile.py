#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys
from functools import wraps

from django.conf import settings
from fabric.api import cd, env, prefix, quiet, require, run, sudo, task
from fabric.colors import green, yellow
from fabric.contrib import django

# put project directory in path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

django.project('owri')

REPOSITORY = 'https://github.com/kingsdigitallab/languageacts-django.git'

env.user = settings.FABRIC_USER
env.hosts = ['languageacts.kdl.kcl.ac.uk']
env.root_path = '/vol/languageacts/webroot/'
env.envs_path = os.path.join(env.root_path, 'envs')


def server(func):
    """Wraps functions that set environment variables for servers"""
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            env.servers.append(func)
        except AttributeError:
            env.servers = [func]

        return func(*args, **kwargs)
    return decorated


@task
@server
def dev():
    env.srvr = 'dev'
    set_srvr_vars()


@task
@server
def stg():
    env.srvr = 'stg'
    set_srvr_vars()


@task
@server
def liv():
    env.srvr = 'liv'
    set_srvr_vars()


def set_srvr_vars():
    env.path = os.path.join(env.root_path, env.srvr, 'django',
                            'owri-django')
    env.within_virtualenv = 'source {}'.format(
        os.path.join(env.envs_path, env.srvr, 'bin', 'activate'))


@task
def install_system_packages():
    sudo('apt-get -y --force-yes install apt-transport-https')
    sudo(('wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | '
          'apt-key add -'))
    sudo(('echo '
          '"deb https://packages.elastic.co/elasticsearch/2.x/debian '
          'stable main" | '
          'tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list'))
    sudo('apt-get update')
    sudo(('apt-get -y --force-yes install '
          'python-dev python-pip python-setuptools python-virtualenv '
          'openjdk-7-jre elasticsearch '
          'libjpeg-dev libxml2-dev libxslt-dev '
          'libldap2-dev libsasl2-dev '
          'libpq-dev postgresql-client '
          'git git-core'))
    sudo('sudo update-rc.d elasticsearch defaults 95 10')


@task
def setup_environment(version=None):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    create_virtualenv()
    clone_repo()
    update(version)
    install_requirements()


@task
def create_virtualenv():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    with quiet():
        env_vpath = os.path.join(env.envs_path, env.srvr)
        if run('ls {}'.format(env_vpath)).succeeded:
            print(
                green('virtual environment at [{}] exists'.format(env_vpath)))
            return

    print(yellow('setting up virtual environment in [{}]'.format(env_vpath)))
    run('virtualenv {}'.format(env_vpath))


def get_virtual_env_path():
    '''Returns the absolute path to the python virtualenv for the server
    (dev, stg, live) we are working on.
    E.g. /vol/tvof/webroot/envs/dev
    '''
    return os.path.join(env.envs_path, env.srvr)


@task
def clone_repo():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)
    with quiet():
        if run('ls {}'.format(os.path.join(env.path, '.git'))).succeeded:
            print(green(('repository at'
                         ' [{}] exists').format(env.path)))
            return

    print(yellow('cloneing repository to [{}]'.format(env.path)))
    run('git clone {} {}'.format(REPOSITORY, env.path))


@task
def install_requirements():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    reqs = 'requirements-{}.txt'.format(env.srvr)

    try:
        assert os.path.exists(reqs)
    except AssertionError:
        reqs = 'requirements.txt'

    with cd(env.path), prefix(env.within_virtualenv):
        run('pip install --no-cache -U -r {}'.format(reqs))


@task
def reinstall_requirement(which):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('pip uninstall {0} && pip install --no-deps {0}'.format(which))


@task
def deploy(version=None):
    update(version)
    install_requirements()
    own_django_log()
    fix_permissions()
    migrate()
    collect_static()
    # update_index()
    # clear_cache()
    restart_uwsgi()


@task
def update(version=None):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if version:
        # try specified version first
        to_version = version
    elif not version and env.srvr in ['local', 'vagrant', 'dev']:
        # if local, vagrant or dev deploy to develop branch
        to_version = 'develop'
    else:
        # else deploy to master branch
        to_version = 'master'

    with cd(env.path), prefix(env.within_virtualenv):
        run('git pull')
        run('git checkout {}'.format(to_version))


@task
def own_django_log():
    """ make sure logs/django.log is owned by www-data"""
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with quiet():
        log_path = os.path.join(env.path, 'logs', 'django.log')
        if run('ls {}'.format(log_path)).succeeded:
            sudo('chown www-data:www-data {}'.format(log_path))


@task
def fix_permissions(category='static'):
    '''
    Reset the permissions on various paths.
    category: determines which set of paths to work on:
        'static' (default): django static path + general project path
        'virtualenv': fix the virtualenv permissions
    '''
    # GN: why do we need VE?
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    processed = False

    with quiet():
        if category == 'static':
            processed = True
            log_path = os.path.join(env.path, 'logs', 'django.log')
            if run('ls {}'.format(log_path)).succeeded:
                sudo('setfacl -R -m g:www-data:rwx {0}/logs {0}/static'.
                     format(env.path))
                sudo('setfacl -R -d -m g:www-data:rwx {0}/logs {0}/static'.
                     format(env.path))
                sudo('setfacl -R -m g:kdl-staff:rwx {0}/logs {0}/static'.
                     format(env.path))
                sudo('setfacl -R -d -m g:kdl-staff:rwx {0}/logs {0}/static'.
                     format(env.path))
                sudo('chgrp -Rf kdl-staff {}'.format(env.path))
                sudo('chmod -Rf g+w {}'.format(env.path))
        if category == 'virtualenv':
            path = get_virtual_env_path()
            sudo('chgrp -Rf kdl-staff {}'.format(path))
            sudo('chmod -Rf g+rw {}'.format(path))
            processed = True

    if not processed:
        raise Exception(
            'fix_permission(category="{}"): unrecognised category name.'.
            format(category)
        )


@task
def migrate(app=None):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py migrate {}'.format(app if app else ''))


@task
def collect_static(process=False):
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    if env.srvr in ['local', 'vagrant']:
        print(yellow('Do not run collect_static on local servers'))
        return

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py collectstatic {process} --noinput'.format(
            process=('--no-post-process' if not process else '')))


@task
def update_index():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py update_index')


@task
def clear_cache():
    require('srvr', 'path', 'within_virtualenv', provided_by=env.servers)

    with cd(env.path), prefix(env.within_virtualenv):
        run('./manage.py clear_cache')


@task
def restart_uwsgi():
    sudo('service uwsgi restart django-{}'.format(env.srvr))
