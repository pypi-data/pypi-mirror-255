import click
import subprocess

@click.group()
def cli():
    cli.add_command('connect', 'start', 'stop')

if __name__ == '__main__':
    cli()

import click

@click.group()
def cli1():
    pass

@cli1.command()
def start():
    """Start your vm"""
    subprocess.run(["ls", "-l", "gcloud compute instances start --zone=europe-west1-d lewagon-data-eng-vm-asicuima"])

@click.group()
def cli2():
    pass

@cli2.command()
def stop():
    """Stop your vm"""
    subprocess.run(["ls", "-l", "gcloud compute instances stop --zone=europe-west1-d lewagon-data-eng-vm-asicuima"])

@click.group()
def cli3():
    pass

@cli3.command()
def connect():
    """Connect to your vm in vscode inside your ~/code/asicuima/folder """
    subprocess.run(["ls", "-l", "code --folder-uri vscode-remote://ssh-remote+liangma422@34.38.114.25/home/liangma422/"])

cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()
