ENV['BUNDLE_GEMFILE']=File.expand_path('../unit.Gemfile',__dir__)
require_relative '../boot'
require 'active_support/all'
require 'active_model'
require 'active_model/validations'
puts "Presence: #{ActiveModel::Validations.const_defined?(:PresenceValidator)}"
base=Gem.loaded_specs['activemodel'].full_gem_path
puts "Absolute glob: #{Dir[File.join(base,'lib/active_model/validations/*.rb')].length}"
puts "Relative glob: #{Dir['.qa-runtime/gems/gems/activemodel-7.1.6/lib/active_model/validations/*.rb'].length}"
require 'active_model/validations/presence'
puts "Explicit presence loaded: #{ActiveModel::Validations.const_defined?(:PresenceValidator)}"
