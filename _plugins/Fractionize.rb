module Jekyll
  module Fractionize
    def fractionize(text)
      return "" unless text

      n = Float(text) rescue nil

      if n
        int = n.to_i
        dec = (n - int).abs

        case dec
        when 0 then int.to_s
        when 0.25 then "#{int}&frac14;"
        when 0.5 then "#{int}&frac12;"
        when 0.75 then "#{int}&frac34;"
        else n.to_s
        end
      else
        text
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::Fractionize)
