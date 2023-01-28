Run local test server: `bundle exec jekyll serve`

## Images

### Creating Small Image from Big

The small images shown on an engine page are 360 pixels high, unless the original is less than that.

`cd images/atlas`

`ls -1 *_big.(jpg|png) | xargs -t -I '{}' magick '{}' -colorspace RGB -set filename:original %t -filter lanczos -set filename:original %t -resize "x360>" -unsharp 0x0.75+0.75+0.008 -quality 90 -colorspace sRGB -strip "%[filename:original]_small.jpg"`

`zmv -f '(*)_big_small.jpg' '$1.jpg'`

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

## Creating a Manual from Scratch

### PDF to Images

Use `pdfimages` to extract images from PDF files. It is installed from popper-utils.

**Do not use ImageMagick to extract the images**, it causes loss of quality due to trying to do weird things with the PDF's DPI. While that can be mitigated, `pdfimages` is much simpler.

Example: `pdfimages original.pdf image`

The above example would extract all images from the PDF into files image-000.ppm, image-001.ppm, etc. PPM files are an intermediate lossless image format.

### Images to PDF

```
magick sm_*.jpg -density 104 -define 'pdf:title=6HM2124 Instructions and Parts Catalog' -define 'pdf:author=Atlas Imperial Diesel Engine Co.' -define 'pdf:producer=Atlas Imperial Diesel Engine Co.' AI_instructions_6HM2124_sm.pdf
```

Use `pdfimages -list` on the original PDF to see its DPI (called ppi in the tool), which can be used to calculate the new DPI (called -density by ImageMagick) based on how the images have been scaled to the point.

### Processing Images

Use ImageMagick to process the images from the manual. It can deal with pretty much any input and output image format, including PPM files. All examples below use ImageMagick v7.

Each manual likely requires individual processing. Here are some example commands that are useful for bulk processing:

#### Image/PDF Info

The following commands all give slightly different info about an image or PDF:

`magick identify <img/pdf>`

`magick identify -verbose <img/pdf>`

`pdfinfo <pdf>`

`pdfimages -list <pdf>`

#### Convert Between Formats


```
magick *.ppm -set filename:original %t -quality 100 -define png:color-type=6 "%[filename:original].png"
```

png:color-type=6 forces the output PNG to be truecolor with alpha. Otherwise ImageMagick will output greyscale images if the input only contains grey colors, causing annoying warnings.

#### Auto-crop White Border

```
magick *.ppm -set filename:original %t -define 'trim:percent-background=80%' -background white -fuzz '5%' -trim +repage -quality 100 -define png:color-type=6 "%[filename:original].png"
```

percent-background controls how much of the background color (white in this case) is allow to be in a row or column before it is trimmed off. Rows and columns are trimmed off until one is reached with less than that percentage of the color.

fuzz allows colors that are close to the background color to be considered the same color. Useful for scanned images where the "white" border is slightly noisy.

+repage is required to shrink the canvas to the new size of the image after trimming.

#### Scale down and compress to JPG

Scale down to a width of 740, preserving aspect ratio. The unsharping is needed because scaling down causes slight blurriness.

```
magick scanned*.png -set filename:original %t -filter lanczos -resize 740 -unsharp 0x0.75+0.75+0.008 -quality 90 -strip "sm_%[filename:original].jpg"
```

## Generating Thumbnails

Use the original quality manual when possible.

### Single

```
cd manuals/atlas
magick 'AI_parts-catalog_4HM763.pdf[0]' -colorspace RGB -set filename:original %t -resize "100x200>" -unsharp 0x0.75+0.75+0.008 -quality 100 -define png:color-type=6 -colorspace sRGB "%[filename:original].png"
zopflipng --iterations=500 --filters=01234mepb --lossy_8bit --lossy_transparent --prefix=zopfli_ -y AI_parts-catalog_4HM763.png
zmv -f zopfli_*.png '*.png'
```

### In Bulk

```
cd manuals/atlas
ls -1 | xargs -t -I '{}' magick '{}[0]' -colorspace RGB -set filename:original %t -resize "100x200>" -unsharp 0x0.75+0.75+0.008 -quality 100 -define png:color-type=6 -colorspace sRGB "%[filename:original].png"
zopflipng --iterations=500 --filters=01234mepb --lossy_8bit --lossy_transparent --prefix=zopfli_ *.png
zmv -f zopfli_*.png '*.png'
```

