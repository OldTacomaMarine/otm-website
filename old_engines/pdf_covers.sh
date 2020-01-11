ls -1 | xargs -t -I '{}' magick convert '{}[0]' -set filename:original %t -resize "100x200>" -quality 100 "%[filename:original].png"
zopflipng --iterations=500 --filters=01234mepb --lossy_8bit --lossy_transparent --prefix *.png
