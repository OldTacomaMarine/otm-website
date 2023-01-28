Jekyll::Hooks.register :site, :post_write do |site|
  ["images", "manuals"].each do |dir|
    File.symlink(File.join(site.source, dir), File.join(site.dest, dir))
  end
end
