STDOUT.binmode
STDERR.binmode
puts "Ruby #{RUBY_VERSION}"
begin
  require 'stringio'
  require 'etc'
  require 'minitest'
  puts "Minitest #{Minitest::VERSION} ready"
rescue Exception => error
  puts "#{error.class}: #{error.message}"
  exit 2
end
