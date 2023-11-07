module Jekyll
  module NilSort
    # Liquid templates built-in sort does not support nil elements.
    # This will sort the items putting nil first.
    def nilsort(array)
      return nil unless array
      return array.sort
    end
  end
end

Liquid::Template.register_filter(Jekyll::NilSort)
