import os
import tempfile
import time
from contextlib import suppress

import pytest

from fan_tools.unix import ExecError, succ, wait_socket


def create_database():
    print('Create database')
    c = 0
    while c < 30:
        try:
            succ(
                'echo create database plugin | '
                'PGPASSWORD=password psql -h localhost -p 40001 -U postgres'
            )
            return
        except ExecError as e:
            print(e)
            c += 1
            time.sleep(1)
    print('Cannot create database')
    c, out, err = succ('docker logs testpostgres')
    print('\n'.join(out))
    print('=' * 80)
    print('\n'.join(err))
    exit(1)


def pytest_configure(config):
    if config.getoption('docker_skip'):
        return

    with suppress(Exception):
        print('Stop old container if exists')
        os.system('docker stop testpostgres')
        time.sleep(1)
    with suppress(Exception):
        os.system('docker rm testpostgres')
    try:
        print('Start docker')
        tmp_dir = tempfile.mkdtemp()
        succ(
            'docker run -d -p 40001:5432  -e POSTGRES_PASSWORD=password '
            f'-v {tmp_dir}:/var/lib/postgresql/data '
            '--name=testpostgres postgres:15 '
        )
        time.sleep(5)
        wait_socket('localhost', 40001, timeout=15)
        create_database()
    except Exception as e:
        print('EXCEPTION: {}'.format(e))
        exit(1)


def pytest_unconfigure(config):
    if config.getoption('docker_skip') or config.getoption('keep_db'):
        return
    os.system('docker stop -t 2 testpostgres')
    os.system('docker rm testpostgres')


@pytest.fixture(autouse=True)
def autodatabase(module_transaction):
    pass


def pytest_addoption(parser):
    group = parser.getgroup('fan_group')
    group.addoption(
        '--docker-skip', action='store_true', default=False, help='skip docker initialization'
    )
    group.addoption('--keep-db', action='store_true', default=False, help='skip shutting down db')
