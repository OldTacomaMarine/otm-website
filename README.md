Run local test server: `bundle exec jekyll server`

## Manuals

## Adding Manuals

To add a new manual:

1. Pull down the existing media from S3: `AWS_PROFILE=otm bundle exec rake fetch_media`
1. Add the manual to a directory under manuals/
1. Add the manual's thumbnail to the same directory, with the same name but with .png
    * Thumbnail should have a width of 100px
    * See below for commands
1. Update the appropriate .yml file in \_data/manuals/
1. Dryrun deploy: `AWS_PROFILE=otm bundle exec rake deploy`
1. Real deploy: `AWS_PROFILE=otm bundle exec rake 'deploy[false]'`

## Creating a Manual from Images

TODO

## Generating Thumbnails

### Single

```
cd manuals/atlas
magick 'AI_parts-catalog_4HM763.pdf[0]' -set filename:original %t -resize "100x200>" -quality 100 -define png:color-type=6 "%[filename:original].png"
zopflipng --iterations=500 --filters=01234mepb --lossy_8bit --lossy_transparent --prefix=zopfli_ -y AI_parts-catalog_4HM763.png
zmv -f zopfli_*.png '*.png'
```

### In Bulk

```
cd manuals/atlas
ls -1 | xargs -t -I '{}' magick '{}[0]' -set filename:original %t -resize "100x200>" -quality 100 -define png:color-type=6 "%[filename:original].png"
zopflipng --iterations=500 --filters=01234mepb --lossy_8bit --lossy_transparent --prefix=zopfli_ *.png
zmv -f zopfli_*.png '*.png'
```
