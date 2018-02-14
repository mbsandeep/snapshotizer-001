# snapshotizer-001
Demo project to manage aws ec2 instances snapshots

# About
this project is demo for ec2 instances snapshots

#Configure
sandy uses the configuration file creted by awscli  e.g.

`aws configure --profile sandy`

#running

python snap/snapy1.py <command> <subcommand> <--project=PROJECT>

*command* is instances, volume, snapshots
*subcommand* is list, start, stop (depends on commands)
*Project* is optional
