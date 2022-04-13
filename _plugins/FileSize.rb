module Jekyll
  module FileSize
    def file_size(path)
      file = File.join(@context.registers[:site].source, path.strip)

      return nil unless File.exist?(file)

      # Covert to megabytes, always rounding up (similar to "ls -h")
      "#{(File.size(file) / (1024.0 ** 2)).ceil}MB"
    end
  end
end

Liquid::Template.register_filter(Jekyll::FileSize)
