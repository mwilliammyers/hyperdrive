#!/usr/bin/env python
"""The main entry point. Invoke as `hyperdrive' or `python -m hyperdrive'.
"""
import argparse
import hyperdrive.provider
import sys


def _port(arg):
    host_port, container_port = arg.split(':')
    return '{}/tcp'.format(host_port), container_port


def main():
    parser = argparse.ArgumentParser(
        description=hyperdrive.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {}'.format(hyperdrive.__version__))

    parser.add_argument(
        '-m',
        '--manager',
        dest='manager_url',
        default=hyperdrive.default_docker_manager_url,
        help='the url of a manager host for the cluster')

    subparsers = parser.add_subparsers(
        dest='mode', help='interact with jobs on the cluster')

    status_parser = subparsers.add_parser('status', help='get status of job(s)')
    status_parser.add_argument('job', nargs='+', help='the name of the job')

    logs_parser = subparsers.add_parser('logs', help='get logs for job(s)')
    logs_parser.add_argument('job', nargs='+', help='the name of the job')
    logs_parser.add_argument(
        '-f',
        '--follow',
        action='store_true',
        help='keep connection open to read logs as they are sent from docker')
    logs_parser.add_argument(
        '-n', '--lines', default='all', help='number of log lines to print')

    deploy_parser = subparsers.add_parser('deploy', help='deploy a job')
    deploy_parser.add_argument(
        '--from',
        dest='base_image',
        default=hyperdrive.default_docker_base_image,
        help='the docker image to base built images from')
    deploy_parser.add_argument(
        '-p',
        '--publish',
        dest='port',
        nargs='*',
        type=_port,
        help='ports to publish to make them available externally'
        ' (example: `-p 8888:8888 -p 8081:8080`'
        ' maps external port 8888 to docker image port 8888 and 8081 to 8080)')

    args, _ = parser.parse_known_args()

    print(args)
    if args.mode == 'status':
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)
            from pprint import pprint
            pprint(pccl.status())
    elif args.mode == 'logs':
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)
            print(j)
            for line in pccl.logs(
                    timestamps=True, follow=args.follow, tail=args.lines):
                print(line.decode())
    elif args.mode == 'deploy':
        pccl.build(args.base_image, path='./', ports=dict(args.port or []))
        pccl.push()
        pccl.deploy()
        print(pccl.service.name)


if __name__ == '__main__':
    sys.exit(main())
