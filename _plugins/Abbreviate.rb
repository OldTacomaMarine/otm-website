module Jekyll
  module Abbreviate
    def abbr(text)
      return "" unless text

      abbreviations = @context.registers[:site].data["abbreviations"]

      if /^(?<city>[^,]+),\s+(?<state>.*)$/ =~ text
        a = abbreviations[state.downcase] || state
        "#{city}, #{a}"
      else
        text
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::Abbreviate)
