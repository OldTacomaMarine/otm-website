module Jekyll
  module NilSort
    # Liquid templates built-in sort does not support nil elements.
    # This will sort the items putting nil first.
    def nilsort(array)
      return nil unless array

      sorted = array.compact.sort

      if array.any?(nil)
        sorted.prepend(nil)
      end

      sorted
    end
  end
end

Liquid::Template.register_filter(Jekyll::NilSort)
