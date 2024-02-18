import sys
import requests
import datetime
import socket
import json
import argparse
from requests_toolbelt.adapters.socket_options import SocketOptionsAdapter


class TCPKeepAliveAdapter(SocketOptionsAdapter):

    def __init__(self, **kwargs):
        socket_options = kwargs.pop('socket_options', SocketOptionsAdapter.default_options)

        platform = sys.platform

        idle = kwargs.pop('idle', 60)
        interval = kwargs.pop('interval', 20)
        count = kwargs.pop('count', 5)

        socket_options = socket_options + [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        ]

        # TCP Keep Alive Probes for Linux
        if platform == 'linux' and hasattr(socket, 'TCP_KEEPIDLE') \
                and hasattr(socket, 'TCP_KEEPINTVL') \
                and hasattr(socket, 'TCP_KEEPCNT'):
            socket_options += [
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, idle),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, count),
            ]

        # TCP Keep Alive Probes for Windows OS
        elif platform == 'win32' and hasattr(socket, 'TCP_KEEPIDLE'):
            socket_options += [
                (socket.SOL_TCP, socket.TCP_KEEPIDLE, idle),
                (socket.SOL_TCP, socket.TCP_KEEPINTVL, interval),
                (socket.SOL_TCP, socket.TCP_KEEPCNT, count)
            ]

        # TCP Keep Alive Probes for Mac OS
        elif platform == 'darwin':
            # On OSX, TCP_KEEPALIVE from netinet/tcp.h is not exported
            # by python's socket module
            TCP_KEEPALIVE = getattr(socket, 'TCP_KEEPALIVE', 0x10)
            socket_options += [
                (socket.IPPROTO_TCP, TCP_KEEPALIVE, idle),
                (socket.SOL_TCP, socket.TCP_KEEPINTVL, interval),
                (socket.SOL_TCP, socket.TCP_KEEPCNT, count)
            ]

        super(TCPKeepAliveAdapter, self).__init__(
            socket_options=socket_options, **kwargs
        )


def do_request(commit, branch, percent):
    URL = "https://benchling.appsurify.com/api/external/prioritized-tests/"
    # URL = "http://127.0.0.1:8000/api/external/prioritized-tests/"

    PAYLOAD = {
        'name_type': 'junit',
        'filename': 'True',
        'filename_separator': '#',
        'project_name': 'Benchling',
        'test_suite_name': 'cypress',
        'priority': '9',
        'classname': 'False',
        'testsuitename': 'False',
        'commit_type': 'LastRun',
        'percent': percent,
        'target_branch': branch,
        'commit': commit
    }
    
    HEADERS = {
        'user-agent': 'Testbrain/1.0 Python/3.x.x SocketTun/1.0',
        'token': 'ODk6NnAtbHlnY2RiU2NlckREQ0MtM1oyWHE3Yy1JTEk1YmNlNUlzUkRIekV5UQ'
    }

    adapter = TCPKeepAliveAdapter()

    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(URL, params=PAYLOAD, headers=HEADERS, timeout=1200)

    status = response.status_code
    if status == 200:
        content = response.json()
    else:
        print(f'[REQ] {status} with {response.content}')
        content = []
    return status, content


def main(commit, branch, percent):
    #print(f"START: {datetime.datetime.now()}")
    status, content = do_request(commit, branch, percent)
    #print(f"FINISH: {datetime.datetime.now()}")
    data = []

    for element in content:
        filename, test_name = None, None
        name = element.get('name', '#')
        name_lst = name.split('#', maxsplit=1)

        if len(name_lst) > 1:  # Check returned filename and testname, empty if only testname
            filename, test_name = name_lst[0], name_lst[1]
        elif len(name_lst) == 1:  # if need add testname
            test_name = name_lst[0]

        data.append(filename)

    # Clean empty elem
    data = list(filter(lambda x: x, data))

    # Uniq
    data = list(set(data))

    count = len(data)

    # Merge to string
    data = ', '.join(data)
    
    print("Prioritized files")
    #print(f"Prioritized count - {count}")
    print(data)
    return status, data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get list of files for prioritized run')
    parser.add_argument('--commit', type=str, required=True,
                    help='Enter your commit')
    parser.add_argument('--branch', type=str, required=True,
                    help='Enter your branch')
    parser.add_argument('--percent', type=str, required=False, default="50",
                    help='Percentage of tests run')
    args = parser.parse_args()
    #commit = "6354b3afb2dac48fec687ebe0b40ea719d5505fa"
    #branch = "gh/aschwartzbenchling/42/head"
    branch = args.branch
    commit = args.commit
    percent = args.percent
    result = main(commit, branch, percent)
    print(result[0])
