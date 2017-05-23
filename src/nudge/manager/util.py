import itertools
import packaging.version
import re

import boto3
import click


class EnumType(click.Choice):

    def __init__(self, enum):
        super(EnumType, self).__init__(enum.__members__)
        self._enum = enum

    def convert(self, value, param, ctx):
        if isinstance(value, self._enum):
            return value

        return self._enum[super(EnumType, self).convert(value, param, ctx)]


_ecr_client = boto3.client('ecr')


# https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_Repository.html
_ecr_re = re.compile(
    r'\A(?P<account>[0-9]{12})'
    r'.dkr.ecr.us-east-1.amazonaws.com/'
    r'(?P<repo>(?:[a-z0-9]+(?:[._-][a-z0-9]+)*/)*[a-z0-9]+(?:[._-][a-z0-9]+)*)'
)


def get_next_image_tag(uri):
    m = _ecr_re.match(uri).groupdict()
    return '{uri}:{v}'.format(
        uri=uri,
        v=_get_next_version(m['account'], m['repo']),
    )


def get_latest_image_tag(uri):
    m = _ecr_re.match(uri).groupdict()
    return '{uri}:{v}'.format(
        uri=uri,
        v=_get_latest_version(m['account'], m['repo']),
    )


def _get_next_version(reg_id, repo):
    major, minor, build = map(int, _get_latest_version(reg_id, repo).split('.'))
    build += 1

    return '.'.join(map(str, (major, minor, build)))


def _get_latest_version(reg_id, repo):
    return max(map(
        lambda i: packaging.version.parse(i['imageTag']),
        itertools.chain.from_iterable(map(
            lambda r: r['imageIds'],
            _ecr_client.get_paginator('list_images').paginate(
                registryId=reg_id,
                repositoryName=repo,
                filter={'tagStatus': 'TAGGED'},
            ),
        )),
    )).base_version


def get_bucket(s3_uri):
    assert s3_uri.startswith('s3://')
    return s3_uri[len('s3://'):].split('/', 1)[0]