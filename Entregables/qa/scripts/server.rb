require_relative '../boot'
Dir.chdir(QA_APP_ROOT)
require QA_APP_ROOT.join('config/environment').to_s
# CSRF remains enabled for browser/security/performance runs, unlike Rails test default.
Rails.application.config.action_controller.allow_forgery_protection=true
ActionController::Base.allow_forgery_protection=true
require 'rails/commands/server/server_command'
Rails::Server.new(Port:3100,Host:'127.0.0.1',environment:'test',app:Rails.application).start
