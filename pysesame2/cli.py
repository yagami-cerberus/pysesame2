
from json import dumps
from uuid import UUID
import argparse
import sys
import os

from .pysesame2 import get_sesames, Sesame, SesameAuthorityError


def main(params=None):
    parser = argparse.ArgumentParser(description='Control Sesame', epilog='')
    parser.add_argument('--apikey', dest='apikey', type=str, default=None)
    parser.add_argument('--json', dest='json_output', action='store_const', const=True, default=False)
    subparsers = parser.add_subparsers(help='Sesame Action', dest='action')
    subparsers.required = True

    subparsers.add_parser('list', help='List available sesames')

    status_parser = subparsers.add_parser('status', help='Get sesame status')
    status_parser.add_argument(dest='device_id', type=UUID, help='Sesame Device ID')

    lock_parser = subparsers.add_parser('lock', help='Lock sesame')
    lock_parser.add_argument(dest='device_id', type=UUID, help='Sesame Device ID')

    unlock_parser = subparsers.add_parser('unlock', help='Lock sesame')
    unlock_parser.add_argument(dest='device_id', type=UUID, help='Sesame Device ID')

    flush_parser = subparsers.add_parser('flush', help='Forced server update sesame status immediately')
    flush_parser.add_argument(dest='device_id', type=UUID, help='Sesame Device ID')

    options = parser.parse_args(params)

    if not options.apikey:
        options.apikey = os.environ.get('SESAME_APIKEY')

    if not options.apikey:
        sys.stderr.write('apikey is missiong\n')
        sys.exit(1)

    try:
        if options.action == 'list':
            sys.exit(action_list(options))
        elif options.action == 'status':
            sys.exit(action_status(options))
        elif options.action in ('lock', 'unlock', 'flush'):
            sys.exit(action_command(options))
    except SesameAuthorityError:
        sys.stderr.write('apikey is invalid\n')
        sys.exit(1)

    sys.exit(1)


def action_list(options):
    sesames = get_sesames(options.apikey)
    if options.json_output:
        output = tuple({'device_id': str(sesame.id),
                        'serial': sesame.serial,
                        'nickname': sesame.nickname} for sesame in sesames)
        sys.stdout.write(dumps(output))
        sys.stdout.write('\n')
    else:
        sys.stdout.write('%36s%14s %s\n' % ('Device ID', 'Serial', 'Nickame'))
        sys.stdout.write('=' * 70)
        sys.stdout.write('\n')
        for sesame in sesames:
            sys.stdout.write('%36s%14s %s\n' % (sesame.id, sesame.serial, sesame.nickname))
    return 0


def action_status(options):
    sesame = Sesame(options.device_id, options.apikey)
    output = sesame.get_status()

    if options.json_output:
        sys.stdout.write(dumps(output))
        sys.stdout.write('\n')
    else:
        sys.stdout.write('Locked: %(locked)s\n'
                         'Battery: %(battery)s\n'
                         'Responsive: %(responsive)s\n' % output)
    return 0


def action_command(options):
    sesame = Sesame(options.device_id, options.apikey)
    if options.action == 'lock':
        task = sesame.lock()
    elif options.action == 'unlock':
        task = sesame.unlock()
    elif options.action == 'flush':
        task = sesame.flush_status()

    if task.is_successful:
        return 0
    else:
        sys.stderr.write('%s' % task.error)
        return 1
