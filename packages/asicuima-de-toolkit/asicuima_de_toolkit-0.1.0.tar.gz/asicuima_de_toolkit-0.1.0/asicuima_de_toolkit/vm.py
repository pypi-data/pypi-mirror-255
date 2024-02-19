import click
import subprocess

@click.command()
def start():
    """Start your vm"""
    subprocess.run(["ls", "-l", "gcloud compute instances start --zone=europe-west1-d lewagon-data-eng-vm-asicuima"])

@click.command()
def stop():
    """Stop your vm"""
    subprocess.run(["ls", "-l", "gcloud compute instances stop --zone=europe-west1-d lewagon-data-eng-vm-asicuima"])

@click.command()
def connect():
    """Connect to your vm in vscode inside your ~/code/asicuima/folder """
    subprocess.run(["ls", "-l", "code --folder-uri vscode-remote://ssh-remote+liangma422@34.38.114.25/home/liangma422/"])
