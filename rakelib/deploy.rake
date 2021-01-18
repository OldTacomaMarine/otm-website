# frozen_string_literal: true
require 'digest'
require 'pathname'
require 'aws-sdk-s3'
require 'aws-sdk-cloudfront'
require 'mime-types'
require 'optparse'
require 'rainbow/refinement'

using Rainbow

SITE_S3_BUCKET = "oldtacomamarine.com"
IMG_S3_BUCKET = "img.#{SITE_S3_BUCKET}"
S3_REGION = "us-west-2"

task :fetch_media do
  download(IMG_S3_BUCKET, IMG_FILES)
end

task :deploy, %w[dryrun] => %w[clean test] do |t, args|
  dryrun = (args.dryrun != "false")

  dryrun_puts(dryrun, "Running in dryrun mode, will not modify remote files")
  dryrun_puts(dryrun, "To run for real, run: " + "bundle exec rake 'deploy[false]'".green)

  changed = upload(SITE_S3_BUCKET, BUILD_DIR, SITE_FILES, dryrun: dryrun)
  changed |= upload(IMG_S3_BUCKET, BUILD_DIR, IMG_FILES, dryrun: dryrun)

  if changed
    Rake::Task["invalidate_cdn"].invoke(args.dryrun)
  else
    puts "No files changed"
  end
end

task :invalidate_cdn, %w[dryrun] do |t, args|
  dryrun = (args.dryrun != "false")

  # CloudFront is global, but the client still needs a region for some reason
  cf = Aws::CloudFront::Client.new(region: "us-east-1")

  # Find the CloudFront distribution that uses the SITE_S3_BUCKET as its origin
  distributions = cf.list_distributions.flat_map { |r| r.distribution_list.items }
  distribution = distributions.select { |d| d.origins.items.any? { |o| o.id == SITE_S3_BUCKET } }.first

  invalidation = {
    distribution_id: distribution.id,
    invalidation_batch: {
      paths: { quantity: 1, items: ["/*"] },
      caller_reference: Time.now.utc.to_s
    }
  }

  if dryrun
    dryrun_puts(dryrun, "Would have invalidated CloudFront: #{invalidation}")
  else
    puts "Invalidating CloudFront distribution: #{distribution.id}"
    cf.create_invalidation(invalidation)
  end
end

def dryrun_puts(dryrun, str)
  if dryrun
    puts "[Dryrun]".yellow + " " + str
  end
end

def upload(bucket_name, build_dir, files, dryrun: true)
  puts "Uploading changed files to bucket #{bucket_name}..."
  changed = false

  paths = files.map {|f| Pathname.new(f) }
  paths.select!(&:file?)

  s3 = Aws::S3::Resource.new(region: S3_REGION)
  bucket = s3.bucket(bucket_name)

  # Find all files recursively within the build output directory
  paths.each do |p|
    # Get the S3 object key by getting the path relative to build_dir
    key = p.relative_path_from(build_dir).to_s
    obj = bucket.object(key)

    exists = begin
      obj.load
      true
    rescue Aws::S3::Errors::NotFound
      false
    end

    local_hash = Digest::MD5.file(p).hexdigest

    # Upload the file if it is different from the existing one
    unless exists && obj.metadata["hash"] == local_hash
      changed = true

      if exists
        puts "#{key} differs...uploading"
      else
        puts "#{key} doesn't exist...uploading"
      end

      mime = MIME::Types.type_for(p.to_s).first.content_type

      p.open("r") do |file|
        item = {
          body: file,
          content_type: mime,
          content_length: p.size,
          metadata: { hash: local_hash }
        }

        if dryrun
          dryrun_puts(dryrun, "Would have put item to key #{obj.key}: #{item}")
        else
          obj.put(item)
        end
      end
    end
  end

  changed
end

def download(bucket_name, existing_files)
  puts "Downloading missing files..."

  paths = existing_files.map {|f| Pathname.new(f) }
  paths.select!(&:file?)

  s3 = Aws::S3::Resource.new(region: S3_REGION)
  bucket = s3.bucket(bucket_name)

  objects = bucket.objects

  objects.each do |obj|
    path = Pathname.new(obj.key)

    # Download the file if it is different from the existing one
    unless path.exist? && obj.object.metadata["hash"] == Digest::MD5.file(path).hexdigest
      if path.exist?
        puts "#{obj.key} differs...downloading"
      else
        puts "#{obj.key} doesn't exist...downloading"
      end

      path.parent.mkpath

      obj.get(response_target: path.to_s)

      download_hash = Digest::MD5.file(path).hexdigest

      if download_hash != obj.object.metadata["hash"]
        raise "File corrupted on download: " + path
      end
    end
  end
end

