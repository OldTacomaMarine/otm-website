# frozen_string_literal: true
require 'rake/clean'
require 'html-proofer'

# The directory that jekyll outputs to
BUILD_DIR = "_site"
SITE_FILES = FileList[File.join(BUILD_DIR, "**/*")]
  .exclude(File.join(BUILD_DIR, "images/**/*"))
  .exclude(File.join(BUILD_DIR, "manuals/**/*"))
IMG_FILES = FileList[
  File.join(BUILD_DIR, "images/**/*"),
  File.join(BUILD_DIR, "manuals/**/*")
]

CLEAN.include(FileList[File.join(BUILD_DIR, "**/*")])

task default: %w[test]

task :build do
  sh({"JEKYLL_ENV" => "production"}, "jekyll", "build")
end

task test: %w[build] do
  HTMLProofer.check_directory(
    BUILD_DIR,
    checks: ["Links", "Images", "Scripts", "Favicon"],
    url_ignore: [%r{^/manuals/(atlas|enterprise|fairbanks|washington)/[^/]+\.(pdf|png)$}],
  ).run
end

# see rakelib/deploy.rake for the deploy task

