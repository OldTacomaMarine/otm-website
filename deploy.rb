require 'digest'
require 'pathname'
require 'aws-sdk-s3'
require 'aws-sdk-cloudfront'
require 'mime-types'

s3 = Aws::S3::Resource.new

bucket = s3.bucket(ENV["S3_BUCKET"])
build_dir = Pathname.new(ENV["BUILD_DIR"])

# Find all files recursively within the build output directory
files = Pathname.glob(File.join(build_dir, "**/*")).lazy.select(&:file?)
files.each do |f|
  # Get the S3 object key by getting the path relative to build_dir
  key = f.relative_path_from(build_dir).to_s
  obj = bucket.object(key)

  exists = begin
    obj.load
    true
  rescue Aws::S3::Errors::NotFound
    false
  end

  local_hash = Digest::MD5.file(f).hexdigest

  # Upload the file if it is different from the existing one
  unless exists && obj.metadata["hash"] == local_hash
    if exists
      puts "#{key} differs...uploading"
    else
      puts "#{key} doesn't exist...uploading"
    end

    mime = MIME::Types.type_for(f.to_s).first.content_type

    File.open(f, "r") do |file|
      obj.put(body: file,
              content_type: mime,
              content_length: File.size(f),
              metadata: { hash: local_hash }
             )
    end
  end
end

# Invalidate cloudfront
cf = Aws::CloudFront::Client.new
cf.create_invalidation(
  distribution_id: ENV["CF_DIST_ID"],
  invalidation_batch: {
    paths: { quantity: 1, items: ["/*"] },
    caller_reference: Time.now.utc.to_s
  }
)

