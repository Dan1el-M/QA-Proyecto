# QA-only process environment; never writes development or production databases.
STDOUT.binmode
STDERR.binmode
require 'pathname'
require 'uri'
QA_ROOT = Pathname.new(__dir__).parent.expand_path
QA_APP_ROOT = QA_ROOT.parent
abort 'QA application root is missing' unless QA_APP_ROOT.join('config/application.rb').file?
abort 'QA requires RAILS_ENV=test' unless ENV.fetch('RAILS_ENV', 'test') == 'test'
ENV['RAILS_ENV'] = 'test'
ENV['BUNDLE_GEMFILE'] ||= QA_ROOT.join('qa/Gemfile').to_s
db = URI::RFC2396_Parser.new.escape(QA_ROOT.join('qa/data/qa.sqlite3').to_s.tr('\\', '/'))
abort 'Override DATABASE_URL is forbidden in QA' if ENV['DATABASE_URL'] && ENV['DATABASE_URL'] != "sqlite3:#{db}"
ENV['DATABASE_URL'] = "sqlite3:#{db}"
ENV['RI_FORCE_PATH_FOR_DLL'] ||= '1' if Gem.win_platform?
require 'bundler/setup'
