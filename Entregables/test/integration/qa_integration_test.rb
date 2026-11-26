require_relative '../test_helper'
class QaIntegrationTest < ActionDispatch::IntegrationTest
  def pair
    group=qa_group
    [qa_team(group,0),qa_team(group,1)]
  end
  def test_INT_001
    a,b=pair; game=qa_match(a,b)
    patch "/partidos_grupo/#{game.id}/registrar_resultado",params:{partido:{goles_local:2,goles_visitante:1}}
    assert_response :redirect
    assert_equal [2,1,'finalizado'],game.reload.attributes.values_at('goles_local','goles_visitante','estado')
    assert_equal [3,0], [a.reload.puntos,b.reload.puntos]
  end
  def test_INT_002
    a,b=pair; game=qa_match(a,b)
    game.registrar_resultado!(2,1);game.registrar_resultado!(0,0)
    assert_equal [1,1,0,0],[a.reload.puntos,b.reload.puntos,a.goles_favor,b.goles_favor]
  end
  def test_INT_003
    a,b=pair;game=qa_match(a,b)
    patch "/partidos/#{game.id}/registrar_resultado",params:{partido:{goles_local:2,goles_visitante:1}}
    assert_response :redirect
    assert_equal [3,2,0,2],[a.reload.puntos,a.goles_favor,b.reload.puntos,b.goles_contra]
  end
  def test_INT_004
    group=qa_group
    assert_difference('Seleccion.count',1) do
      post '/selecciones',params:{seleccion:{nombre:'Equipo QA nuevo',acronimo:'QAA',grupo_id:group.id}}
    end
    assert_response :redirect
    assert_equal group.id,Seleccion.find_by!(acronimo:'QAA').grupo_id
  end
  def test_INT_005
    group=qa_group;4.times { |i| qa_team(group,i) }
    before=Seleccion.order(:id).pluck(:id,:nombre,:grupo_id)
    assert_no_difference('Seleccion.count') do
      post '/selecciones',params:{seleccion:{nombre:'Quinto QA',acronimo:'QAZ',grupo_id:group.id}}
    end
    assert_response :unprocessable_entity
    assert_equal before,Seleccion.order(:id).pluck(:id,:nombre,:grupo_id)
  end
  def test_INT_006
    group=qa_group;team=qa_team(group,0)
    get "/grupos/#{group.id}";assert_response :success
    assert_includes response.body,'Grupo A'
    assert_no_difference('Grupo.count') { delete "/grupos/#{group.id}" }
    assert_response :redirect
    assert_equal group.id,team.reload.grupo_id
  end
  def test_INT_007
    qa_full(true)
    result=DeterminarClasificados.obtener
    assert DeterminarClasificados.new.fase_grupos_completa?
    assert_equal [12,12,8,32],result.values_at(:primeros,:segundos,:terceros_clasificados,:total_clasificados).map(&:length)
    assert_equal 32,result[:total_clasificados].map(&:id).uniq.length
    assert_equal 72,Partido.fase_grupos.finalizados.count
  end
  def test_INT_008
    qa_full(true);teams=DeterminarClasificados.obtener[:total_clasificados]
    teams.each_slice(2).with_index { |(a,b),i| qa_match(a,b,73+i,true).registrar_resultado!(2,1) }
    winners=Partido.where(numero_partido:73..88).order(:numero_partido).pluck(:ganador_id)
    result=SiguienteRonda.new(qa_tournament).avanzar
    assert result[:ok],result.inspect
    round=Partido.where(numero_partido:89..96).order(:numero_partido)
    assert_equal 8,round.count
    assert_equal winners,round.flat_map { |m| [m.seleccion_local_id,m.seleccion_visitante_id] }
    assert_no_difference('Partido.count') { SiguienteRonda.new(qa_tournament).avanzar }
  end
  def test_INT_009
    group=qa_group;teams=4.times.map { |i| qa_team(group,i) }
    qa_match(teams[2],teams[3],103,true).registrar_resultado!(2,1)
    qa_match(teams[0],teams[1],104,true).registrar_resultado!(3,1)
    assert qa_tournament.reload.finalizado?
    assert_equal [teams[0].id,teams[1].id,teams[2].id],qa_tournament.attributes.values_at('campeon_id','subcampeon_id','tercero_id')
  end
end
