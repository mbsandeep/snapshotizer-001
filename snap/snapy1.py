import boto3
import click
import botocore

session=boto3.Session(profile_name='sandy')
ec2=session.resource('ec2')

def filter_instances(project):
    instances=[]

    if project:
        filters=[{'Name':'tag:Project','Values':[project]}]
        instances=ec2.instances.filter(Filters=filters)
    else:
        instances=ec2.instances.all()
    return instances
@click.group()
def cli():
    "sandy manages snapshots"

@cli.group('snapshots')
def snapshots():
    "commands for volumes"

@snapshots.command('list')
@click.option('--project',default=None)
def list_snapshots(project):
    "list ec2 snapshots"
    instances=filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print("  ".join((
                i.id,
                v.id,
                s.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))
    return


@cli.group('volumes')
def volumes():
    "commands for volumes"

@volumes.command('list')
@click.option('--project',default=None)
def list_volumes(project):
    "list ec2 volumes"
    instances=filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            print("  ".join((
            i.id,
            v.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Non Encrypted"
            )))
    return


@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshots',help='create snapshots of all volumes')
@click.option('--project',default=None)
def create_snapshots(project):
    "create snapshots for ec2 instances"
    instances=filter_instances(project)

    for i in instances:
        print("stopping {0}".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("  creating snapshots of {0}".format(v.id))
            v.create_snapshot(Description="Created by snapshot analyzer 001")

            print("Starting {0}".format(i.id))
            i.start()
            i.wait_until_running()
            print("Job's Done")
    return

@instances.command('list')
@click.option('--project',default=None)
def list_instances(project):
    "list ec2 instances"
    instances=filter_instances(project)
    for i in instances:
        tags={t['Key']:t['Value']for t in i.tags or []}
        print('   '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project','<no projecct>')
            )))
    return


@instances.command('start')
@click.option('--project',default=None,help='only instances for project')
def stop_instances(project):
    "start instances"
    instances=filter_instances(project)

    for i in instances:
        print('Starting {0}...'.format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}  ".format(i.id) + str(e))
            continue
    return

@instances.command('stop')
@click.option('--project',default=None,help='only instances for project')
def stop_instances(project):
    "stop instances"
    instances=filter_instances(project)

    for i in instances:
        print('Stopping {0}...'.format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}  ".format(i.id) + str(e))
            continue
    return

if __name__ == '__main__':
    cli()
