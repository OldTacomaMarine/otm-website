#!/usr/bin/env python

import boto3
import os
from subprocess import check_output
import mimetypes

bucket_name = os.environ['S3_BUCKET']
local_dir = 'www'

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

git_ls = check_output(['git', 'ls-files', '-s', local_dir])

hashes = [(os.path.relpath(n, local_dir), c, n) for (_, c, _, n) in [s.split() for s in git_ls.splitlines()]]

for (filename, local_hash, path) in hashes:
  obj = bucket.Object(filename)
  obj.load()
  s3_hash = obj.metadata.get('hash')

  if s3_hash != local_hash:
    print "{} differs, uploading".format(path)
    (mime, _) = mimetypes.guess_type(path)
    obj.upload_file(path, ExtraArgs={'ContentType': mime, 'Metadata': {'hash': local_hash}})
