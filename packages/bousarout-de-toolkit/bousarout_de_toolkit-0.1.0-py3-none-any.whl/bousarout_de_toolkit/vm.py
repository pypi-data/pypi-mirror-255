import click
import subprocess

@click.command()
def start():
    """Start your vm"""
    try:
        result = subprocess.run(
            ["gcloud", "compute", "instances", "start", "lewagon-data-eng-vm-mbo3224", "--zone=europe-west9-a"],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

@click.command()
def stop():
    """Stop your vm"""
    try:
        result = subprocess.run(
            ["gcloud", "compute", "instances", "stop", "lewagon-data-eng-vm-mbo3224", "--zone=europe-west9-a"],
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

@click.command()
def connect():
    """Connect to your vm in vscode inside your ~/code/bousarout/folder """
    try:
        result = subprocess.run(
            "code --folder-uri vscode-remote://ssh-remote+moahmed.bousarout@lewagon-data-eng-vm-ip-mbo3224/code/BOUSAROUT",
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
