# Isolated methods: no Rails application, DB connection, HTTP or persistent models.
ENV['BUNDLE_GEMFILE'] = File.expand_path('../../qa/unit.Gemfile', __dir__)
require_relative '../../qa/boot'
require 'simplecov'
SimpleCov.root(QA_APP_ROOT.to_s)
SimpleCov.coverage_dir(ENV.fetch('QA_COVERAGE', QA_ROOT.join('qa/reports/coverage-unit').to_s))
SimpleCov.start do
  track_files QA_APP_ROOT.join('app/**/*.rb').to_s
  add_filter do |source_file|
    !source_file.filename.tr('\\', '/').start_with?(QA_APP_ROOT.join('app').to_s.tr('\\', '/') + '/')
  end
  add_filter '/test/'
  add_filter '/qa/'
end
require 'minitest/autorun'
require 'minitest/mock'
require 'active_support/all'
require 'active_model'
require 'active_model/validations'
require 'active_record'
require_relative '../qa_reporter'
require QA_APP_ROOT.join('app/models/application_record').to_s
%w[grupo seleccion partido torneo].each { |f| require QA_APP_ROOT.join("app/models/#{f}").to_s }
%w[calcular_ganador_partido actualizar_estadisticas_seleccion determinar_clasificados].each do |f|
  require QA_APP_ROOT.join("app/services/#{f}").to_s
end

class QaUnitTest < Minitest::Test
  Match = Struct.new(:goles_local, :goles_visitante, :seleccion_local_id, :seleccion_visitante_id,
                     :goles_penales_local, :goles_penales_visitante, :finished, :knockout,
                     :seleccion_local, :seleccion_visitante, keyword_init: true) do
    def finalizado? = finished
    def eliminacion_directa? = knockout
  end
  Team = Struct.new(:id, :puntos, :goles_favor, :goles_contra, :diferencia_goles, keyword_init: true)
  def match(**values)
    Match.new(**{goles_local: 2, goles_visitante: 1, seleccion_local_id: 1, seleccion_visitante_id: 2,
                 finished: true, knockout: false, seleccion_local: :local, seleccion_visitante: :visitante}.merge(values))
  end
  def stats(game, id = 1)
    service = ActualizarEstadisticasSeleccion.new(Team.new(id: id))
    service.define_singleton_method(:partidos_finalizados) { [game] }
    service
  end
  # Allocate real model behavior, with only attribute/association access replaced.
  def isolated(klass, attrs)
    klass.allocate.tap do |object|
      attrs.each do |key, value|
        object.instance_variable_set("@qa_#{key}", value)
        object.define_singleton_method(key) { instance_variable_get("@qa_#{key}") }
        object.define_singleton_method("#{key}=") { |v| instance_variable_set("@qa_#{key}", v) }
      end
    end
  end
  def test_UT_001 = assert_equal(:local, CalcularGanadorPartido.new(match).calcular_ganador)
  def test_UT_002 = assert_nil(CalcularGanadorPartido.new(match(goles_local: 0,goles_visitante: 0)).calcular_ganador)
  def test_UT_003
    assert_equal({puntos: 3,goles_favor: 2,goles_contra: 1,diferencia_goles: 1}, stats(match).calcular)
  end
  def test_UT_004 = assert_equal([1,0,0,0],stats(match(goles_local: 0,goles_visitante: 0)).calcular.values_at(:puntos,:goles_favor,:goles_contra,:diferencia_goles))
  def test_UT_005
    result = stats(match, 2).calcular
    assert_equal [0,1,2], result.values_at(:puntos,:goles_favor,:goles_contra)
  end
  def test_UT_006
    service=stats(match)
    assert_equal service.calcular, service.calcular
  end
  def test_UT_007
    team=isolated(Seleccion,nombre:'Equipo QA',acronimo:'QAA',grupo:Struct.new(:letra).new('A'))
    assert_equal 'QAA - Equipo QA (Grupo A)',team.to_s
  end
  def test_UT_008
    team=isolated(Seleccion,goles_favor:7,goles_contra:3,diferencia_goles:0)
    team.send(:calcular_diferencia_goles)
    assert_equal 4,team.diferencia_goles
  end
  def test_UT_009
    group=isolated(Grupo,letra:' a ')
    group.send(:normalizar_letra)
    assert_equal 'A',group.letra
  end
  def test_UT_010
    assert isolated(Grupo,selecciones:Struct.new(:count).new(4)).completo?
  end
  def test_UT_011
    assert isolated(Grupo,selecciones:Struct.new(:count).new(3)).tiene_espacio?
  end
  def test_UT_012
    captured=nil
    association=Object.new
    association.define_singleton_method(:reorder) { |**order| captured=order; :ordered }
    assert_equal :ordered,isolated(Grupo,selecciones:association).tabla_posiciones
    assert_equal({puntos: :desc,diferencia_goles: :desc,goles_favor: :desc,id: :asc},captured)
  end
  def test_UT_013
    game=match(goles_local:1,goles_visitante:1,goles_penales_local:5,goles_penales_visitante:4,knockout:true)
    assert_equal :local,CalcularGanadorPartido.new(game).calcular_ganador
  end
  def test_UT_014
    assert_nil CalcularGanadorPartido.new(match(finished:false,goles_local:nil,goles_visitante:nil)).calcular_ganador
  end
  def test_UT_015
    thirds=(0..11).map { |n| Team.new(id:n,puntos:n,diferencia_goles:0,goles_favor:0) }
    groups=thirds.map { |team| Struct.new(:tercero).new(team) }
    Grupo.stub(:ordenados,groups) do
      assert_equal (4..11).to_a.reverse,DeterminarClasificados.new.mejores_terceros.map(&:puntos)
    end
  end
  def test_UT_016
    service=DeterminarClasificados.new
    service.stub(:partidos_fase_grupos_finalizados,36) { assert_equal 0.5,service.progreso_fase_grupos }
  end
  def test_UT_017
    refute isolated(Torneo,campeon_id:1,subcampeon_id:2,tercero_id:nil).finalizado?
  end
  def test_UT_018
    assert isolated(Torneo,campeon_id:1,subcampeon_id:2,tercero_id:3).finalizado?
  end
end
