from deploy.templates import *
from deploy.machines import *
from fabric.contrib.project import *

import fileinput
import sys


@task
def install_app(name="", virtual_install_dir=None, venv=True, offline=True):
    """
    Instal a specific Application through FasbSim3
    
    """
    if virtual_install_dir is not None:
        local('echo "Installing PJM on localHost"') 
        local('virtualenv -p python3 %s/venv' %install_dir)
        local('. %s/venv/bin/activate && pip3 install --upgrade git+https://github.com/vecma-project/QCG-PilotJob.git && deactivate' %(install_dir))
    else:
        # Offline cluster installation - --user install
        config = yaml.load(
            open(os.path.join(env.localroot, 'deploy', 'applications.yml'))
            )
        info = config[name]
        local('echo %s' %info['repository'])
        if offline is True:
            # Temporary folder 
            tmp_app_dir = "%s/tmp_app" %(env.localroot)
            local('mkdir -p %s' %(tmp_app_dir)) 
            
            # Download all the dependencies of the application  
            local('pip3 download -d %s git+https://github.com/vecma-project/QCG-PilotJob.git' %tmp_app_dir)
            # or
            #for dep in info['dependencies']:
            #    local('pip3 download --platform=manylinux1_x86_64 --only-binary=:all: -d %s %s\
            #         ||pip3 download -d %s %s' %(tmp_app_dir, dep, tmp_app_dir, dep))

            # Send the dependencies (and the dependencies of dependencies) to the remote machine 
            for whl in os.listdir(tmp_app_dir):
                local(
                    template(
                        "rsync -pthrvz -e 'ssh -p 8522'  %s/%s $username@$remote:/home_nfs_robin_ib/bmonniern/FabSim3/results" %(tmp_app_dir, whl)
                    )
                )
            # Install all the dependencies in the remote machine
            run(
                template(
                    "pip3 install --no-index --find-links=file:/home_nfs_robin_ib/bmonniern/FabSim3/results /home_nfs_robin_ib/bmonniern/FabSim3/results/QCGPilotManager-0.1.zip --user" 
                )
            )
            # or
            #for dep in info['dependencies']:
            #    run(
            #        template(
            #            "pip3 install --no-index --find-links=file:/home_nfs_robin_ib/bmonniern/FabSim3/results %s --user" %(dep)
            #        )   
            #    )
            
            
        

@task
def install_plugin(name):
    """
    Install a specific FabSim3 plugin.
    """
    config = yaml.load(
        open(os.path.join(env.localroot, 'deploy', 'plugins.yml'))
        )
    info = config[name]
    plugin_dir = "%s/plugins" % (env.localroot)
    local("mkdir -p %s" % (plugin_dir))
    local("rm -rf %s/%s" % (plugin_dir, name))
    local("git clone %s %s/%s" % (info["repository"], plugin_dir, name))


@task
def remove_plugin(name):
    """
    Remove the specified plug-in.
    """
    config = yaml.load(
        open(os.path.join(env.localroot, 'deploy', 'plugins.yml'))
        )
    info = config[name]
    plugin_dir = '{}/plugins'.format(env.localroot)
    local('rm -rf {}/{}'.format(plugin_dir, name))


def add_local_paths(module_name):
    # This variable encodes the default location for templates.
    env.local_templates_path.insert(
        0, "$localroot/plugins/%s/templates" % (module_name)
        )
    # This variable encodes the default location for blackbox scripts.
    env.local_blackbox_path.insert(
        0, "$localroot/plugins/%s/blackbox" % (module_name)
        )
    # This variable encodes the default location for Python scripts.
    env.local_python_path.insert(
        0, "$localroot/plugins/%s/python" % (module_name)
        )
    # This variable encodes the default location for config files.
    env.local_config_file_path.insert(
        0, "$localroot/plugins/%s/config_files" % (module_name)
        )


def get_setup_fabsim_dirs_string():
    """
    Returns the commands required to set up the fabric directories. This
    is not in the env, because modifying this is likely to break FabSim
    in most cases. This is stored in an individual function, so that the
    string can be appended in existing commands, reducing the
    performance overhead.
    """
    return(
        'mkdir -p $config_path; mkdir -p $results_path; mkdir -p $scripts_path'
        )


@task
def setup_fabsim_dirs(name=''):
    """
    Sets up directories required for the use of FabSim.
    """
    """
    Creates the necessary fab dirs remotely.
    """
    run(template(get_setup_fabsim_dirs_string()))


@task
def setup_ssh_keys(password=""):
    """
    Sets up SSH key pairs for FabSim access.
    """
    import os.path
    if os.path.isfile("%s/.ssh/id_rsa.pub" % (os.path.expanduser("~"))):
        print("local id_rsa key already exists.")
    else:
        local(
            "ssh-keygen -q -f %s/.ssh/id_rsa -t rsa -b 4096 -N \"%s\"" %
            (os.path.expanduser("~"), password)
            )
    local(template("ssh-copy-id -i ~/.ssh/id_rsa.pub %s" % env.host_string))


@task
def setup_fabsim(password=""):
    """
    Combined command which sets up both the SSH keys and creates the
    FabSim directories.
    """
    setup_ssh_keys(password)
    setup_fabsim_dirs()
    # FabSim3 ships with FabDummy by default,
    # to provide a placeholder example for a plugin.
    install_plugin("FabDummy")
