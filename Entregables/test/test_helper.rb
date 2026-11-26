require_relative '../qa/boot'
require 'simplecov'
SimpleCov.root(QA_APP_ROOT.to_s)
SimpleCov.coverage_dir(ENV.fetch('QA_COVERAGE',QA_ROOT.join('qa/reports/coverage-integration').to_s))
SimpleCov.start do
  track_files QA_APP_ROOT.join('app/**/*.rb').to_s
  add_filter do |source_file|
    !source_file.filename.tr('\\', '/').start_with?(QA_APP_ROOT.join('app').to_s.tr('\\', '/') + '/')
  end
  add_filter '/test/'
  add_filter '/qa/'
end
require QA_APP_ROOT.join('config/environment').to_s
require 'rails/test_help'
require 'minitest/mock'
require_relative 'qa_reporter'
require_relative '../qa/data/dataset'
abort 'QA DB guard failed' unless Rails.env.test? && ActiveRecord::Base.connection_db_config.database.tr('\\','/').end_with?('/qa/data/qa.sqlite3')
load Rails.root.join('db/schema.rb') unless ActiveRecord::Base.connection.table_exists?(:torneos)
class ActiveSupport::TestCase
  self.use_transactional_tests = true
  include QaDataset
end
