require 'json'
require 'fileutils'
module QaReporter
  class Reporter < Minitest::AbstractReporter
    def initialize
      super
      @rows = []
    end
    def record(result)
      id = result.name[/(?:UT|INT|SEG)_\d{3}/]&.tr('_', '-')
      return unless id
      @rows << {id: id, status: result.skipped? ? 'Bloqueado' : result.passed? ? 'Aprobado' : 'Fallido',
                assertions: result.assertions, seconds: result.time,
                observed: result.failures.map { |f| "#{f.class}: #{f.message}" }.join("\n"),
                failure_kind: result.failures.any? { |f| f.is_a?(Minitest::UnexpectedError) } ? 'Error' : 'Aserción',
                trace: result.failures.flat_map { |f| f.backtrace || [] }}
    end
    def report
      path = ENV.fetch('QA_RESULTS', QA_ROOT.join('qa/reports/native-results.json').to_s)
      FileUtils.mkdir_p(File.dirname(path))
      File.write(path, JSON.pretty_generate(@rows))
    end
    def passed? = @rows.none? { |r| r[:status] == 'Fallido' }
  end
end
module Minitest
  def self.plugin_qa_init(_options)
    reporter << QaReporter::Reporter.new
  end
  extensions << 'qa'
end
