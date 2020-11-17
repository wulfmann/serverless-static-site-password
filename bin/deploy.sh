#!/bin/bash
set -e

rm -rf dist

cp -R src/ dist

export SHA="master"
export S3_BUCKET=""

aws s3 cp ./dist s3://$S3_BUCKET/builds/$SHA \
  --cache-control immutable,max-age=100000000,public \
  --acl public-read \
  --recursive

aws s3 sync \
  s3://$S3_BUCKET/builds/$SHA \
  s3://$S3_BUCKET/current \
  --delete \
  --cache-control max-age=0,no-cache \
  --acl public-read
