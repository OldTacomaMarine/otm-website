[![BuildStatus](https://travis-ci.org/OldTacomaMarine/otm-website.svg)](https://travis-ci.org/OldTacomaMarine/otm-website)

Run local test server: `bundle exec jekyll server`

## Adding Manuals

To add a new manual:

1. Pull down the existing media from S3: `AWS_PROFILE=otm bundle exec rake fetch_media`
1. Add the manual to a directory under manuals/
1. Add the manual's thumbnail to the same directory, with the same name but with .png
    * Thumbnail should have a width of 100px
    * Extract first page from a PDF to thumbnail: `convert -resize '100>' 'input.pdf[0]' output.png`
1. Update the appropriate .yml file in \_data/manuals/
1. Dryrun deploy: `AWS_PROFILE=otm bundle exec rake deploy`
1. Real deploy: `AWS_PROFILE=otm bundle exec rake 'deploy[false]'`

