import click
import subprocess

@click.group()
def cli():
    pass

@click.command()
def start():
    subprocess.run(["gcloud", "compute", "instances", "start", "--zone=europe-west9-c", "lewagon-data-eng-vm-gplumey"])
    pass
@click.command()
def stop():
    subprocess.run(["gcloud", "compute", "instances", "stop", "--zone=europe-west9-c", "lewagon-data-eng-vm-gplumey"])
    pass

@click.command()
def connect():
    
    pass

cli.add_command(start)
cli.add_command(stop)
cli.add_command(connect)


if __name__ == '__main__':
    start()