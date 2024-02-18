import os
import click
import subprocess
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')), autoescape=True)

@click.group()
def cli():
    """A CLI Tool that handles creation of an Allora Worker Node"""
    pass

@click.command()
@click.option('--name', required=True, help='Name of the worker.')
@click.option('--endpoint', required=True, help='The model server URL.')
def init(name, endpoint):
    """Initialize your Allora Worker Node with necessary boilerplates"""
    
    head_peer_id = run_key_generate_command(name)

    file_configs = [
        {
            "template_name": "Dockerfile.j2",
            "file_name": "Dockerfile",
            "context": {}
        },
        {
            "template_name": "main.py.j2",
            "file_name": "main.py",
            "context": {"model_server_url": endpoint}
        },
        {
            "template_name": "docker-compose.yaml.j2",
            "file_name": "docker-compose.yaml",
            "context": {"head_peer_id": head_peer_id}
        },
        {
            "template_name": "requirements.txt.j2",
            "file_name": "requirements.txt",
            "context": {}
        },
        {
            "template_name": ".gitignore.j2",
            "file_name": ".gitignore",
            "context": {}
        },
        {
            "template_name": ".env.j2",
            "file_name": ".env",
            "context": {}
        }
    ]

    generate_all_files(file_configs, name)

@click.command()
@click.option('--logs', is_flag=True, help="Follow logs immediately after starting services.")
def run(logs):
    """Starts worker and head nodes locally for development and testing"""

    compose_dir = os.path.join(os.getcwd(), 'eth-predict') # remove path before deploy
    
    compose_file_path = os.path.join(compose_dir, 'docker-compose.yaml')
    if not os.path.exists(compose_file_path):
        print("docker-compose.yaml file does not exist in the expected directory.")
        return
    
    try:
        print("starting worker and head node for local machine...")
        result = subprocess.run(['docker-compose', 'up', '-d'], cwd=compose_dir, check=True)
        
        if result.returncode == 0:
            print("nodes started successfully. You can run `allora-wkr run --logs` to follow the logs or `allora-wkr stop` to stop the local nodes.")
        else:
            print("starting node unsucessful.")
    except subprocess.CalledProcessError as e:
        print("encountered error while starting nodes.")
        return

    if logs:
        click.echo("Following logs (press Ctrl-C to stop logs)...")
        try:
            subprocess.run(["docker-compose", "logs", "-f"], cwd=compose_dir, check=True)
        except subprocess.CalledProcessError:
            click.echo("Error following logs.")

@click.command()
def terminate():
    """Terminates worker and head nodes locally"""

    compose_dir = os.path.join(os.getcwd(), 'eth-predict') # remove path before deploy
    
    compose_file_path = os.path.join(compose_dir, 'docker-compose.yaml')
    if not os.path.exists(compose_file_path):
        print("docker-compose.yaml file does not exist in the expected directory.")
        return
    
    try:
        print("terminates worker and head node on local machine...")
        result = subprocess.run(['docker-compose', 'stop'], cwd=compose_dir, check=True)
        
        if result.returncode == 0:
            print("nodes terminated successfully.")
        else:
            print("terminate node unsucessful.")
    except subprocess.CalledProcessError as e:
        print("encountered error while terminating nodes.")
        return

@click.command()
def deploy():
    """Deploy worker node to your production kubernetes cluster"""

    click.echo('')
    click.echo('REQUIRMENTS')
    click.echo('1. Ensure to have the Dockerfile built and docker image pushed to your preferred registry.')
    click.echo('   You should have your image uri and tag available')
    click.echo(' ')
    click.echo('2. Ensure you have your kubernetes cluster configured to your kubeconfig as current context.')

    worker_name = os.path.join(os.getcwd(), 'eth-predict').split('/')[-1] # remove before deploy
    worker_image_uri = click.prompt('worker image URI', type=str)
    worker_image_tag = click.prompt('worker image tag', type=str)
    boot_nodes = click.prompt('boot nodes', type=str)
    chain_rpc_address = click.prompt('chain RPC address', type=str)
    chain_topic_id = click.prompt('chain topic ID', type=str)
    mnemonic = click.prompt('mnemonic', type=str)

    file_configs = [
        {
            "template_name": "values.yaml.j2",
            "file_name": "values.yaml",
            "context": {"worker_image_uri": worker_image_uri, "worker_image_tag": worker_image_tag, "worker_name": worker_name, "boot_nodes": boot_nodes, "chain_rpc_address": chain_rpc_address, "chain_topic_id": chain_topic_id, "mnemonic": mnemonic}
        }
    ]

    generate_all_files(file_configs, worker_name)

    try:
        current_context = subprocess.run(["kubectl", "config", "current-context"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
        click.echo(f"Current Kubernetes context: {current_context}")
    except subprocess.CalledProcessError:
        click.echo("Failed to get current Kubernetes context. Is kubectl configured correctly?", err=True)
        return

    try:
        subprocess.run(["helm", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("Helm is already installed.")
    except subprocess.CalledProcessError:
        try:
            click.echo("Attempting to install Helm...")
            subprocess.run("curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash", shell=True, check=True)
            click.echo("Helm installed successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to install Helm: {e}", err=True)
            return

    try:

        click.echo("Adding the 'upshot' Helm repository...")
        subprocess.run(["helm", "repo", "add", "upshot", "https://upshot-tech.github.io/helm-charts"], check=True)
        subprocess.run(["helm", "repo", "update"], check=True)
        click.echo("'upshot' repository added and updated successfully.")
        
        click.echo("Installing the Helm chart 'universal-helm' from 'upshot' repository...")
        compose_dir = os.path.join(os.getcwd(), 'eth-predict', '') # remove path before deploy
        values_file_path = os.path.join(compose_dir, "values.yaml")
        if not os.path.exists(values_file_path):
            click.echo("Values file not found.", err=True)
            return
        subprocess.run(["helm", "install", worker_name, "upshot/universal-helm", "-f", values_file_path], check=True)
        click.echo("Helm chart 'universal-helm' installed successfully.")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred: {e}", err=True)
        return
    
    

def generate_all_files(file_configs, worker_name):
    for config in file_configs:
        template = env.get_template(config["template_name"])
        file_path = os.path.join(os.getcwd(), f'{worker_name}/{config["file_name"]}')
        content = template.render(**config["context"])
        with open(file_path, 'w') as f:
            f.write(content)
        click.echo(f'{config["file_name"]} generated successfully at {file_path}.')

def run_key_generate_command(worker_name):
    command = (
        f'docker run -it --entrypoint=bash -v "$(pwd)/{worker_name}":/data '
        '696230526504.dkr.ecr.us-east-1.amazonaws.com/upshot-compute-node:dev-latest '
        '-c "mkdir -p /data/keys/head /data/keys/worker && (cd /data/keys/head && /app/upshot-keys) && (cd /data/keys/worker && /app/upshot-keys)"'
    )
    try:
        subprocess.run(command, shell=True, check=True)
        peer_id_path = os.path.join(os.getcwd(), f'{worker_name}/keys/head', 'peerid.txt')
        with open(peer_id_path, 'r') as file:
            click.echo("local workers identity generated successfully.")
            head_peer_id = file.read().strip()
            return head_peer_id
    except subprocess.CalledProcessError as e:
        click.echo(f"error generating local workers identity: {e}", err=True)

cli.add_command(init)
cli.add_command(run)
cli.add_command(terminate)
cli.add_command(deploy)

if __name__ == '__main__':
    cli()
