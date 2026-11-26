require_relative '../boot'
Dir.chdir(QA_APP_ROOT)
require QA_APP_ROOT.join('config/environment').to_s
require_relative '../data/dataset'
abort 'Unsafe DB' unless Rails.env.test? && ActiveRecord::Base.connection_db_config.database.tr('\\','/').end_with?('/qa/data/qa.sqlite3')
load Rails.root.join('db/schema.rb') unless ActiveRecord::Base.connection.table_exists?(:torneos)
Object.new.extend(QaDataset).qa_profile(ARGV.fetch(0,'base'))
puts "QA dataset #{ARGV.fetch(0,'base')}; DB=#{ActiveRecord::Base.connection_db_config.database}"
