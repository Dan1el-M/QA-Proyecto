require_relative '../test_helper'
class QaSecurityTest < ActionDispatch::IntegrationTest
  def base
    group=qa_group;a=qa_team(group,0);b=qa_team(group,1)
    [group,a,b,qa_match(a,b)]
  end
  def test_SEG_001
    base;before=Seleccion.order(:id).pluck(:id,:puntos)
    get '/selecciones',params:{grupo_letra:"A' OR 1=1 --"}
    assert_response :success
    assert_no_match(/SQLite3::|SELECT .*FROM selecciones/i,response.body)
    assert_equal before,Seleccion.order(:id).pluck(:id,:puntos)
    assert_select 'tr[data-seleccion-id]',count:0
  end
  def test_SEG_002
    group,a=base
    a.update!(nombre:'<script>window.qaXss=1</script>')
    get '/'
    assert_response :success
    assert_includes response.body,'&lt;script&gt;window.qaXss=1&lt;/script&gt;'
    assert_not_includes response.body,'<script>window.qaXss=1</script>'
  end
  def test_SEG_003
    group=qa_group;before=Seleccion.count
    post '/selecciones',params:{seleccion:{nombre:'Escritura anonima QA',acronimo:'QAZ',grupo_id:group.id}}
    assert_includes [401,403],response.status,'Criterio derivado: requiere ratificar política de acceso'
    assert_equal before,Seleccion.count
  end
  def test_SEG_004
    group=qa_group;before=Seleccion.count
    original=ActionController::Base.allow_forgery_protection
    ActionController::Base.allow_forgery_protection=true
    begin
      begin
        post '/selecciones',params:{seleccion:{nombre:'CSRF QA',acronimo:'QAZ',grupo_id:group.id}}
        assert_equal 422,response.status
      rescue ActionController::InvalidAuthenticityToken
        assert true
      end
      assert_equal before,Seleccion.count
    ensure
      ActionController::Base.allow_forgery_protection=original
    end
  end
  def test_SEG_005
    base;before=Seleccion.order(:id).pluck(:id,:puntos)
    get '/grupos/999999999'
    assert_includes [302,303,404],response.status
    assert_no_match(/Traceback|SQLite3::|secret_key_base/i,response.body)
    assert_equal before,Seleccion.order(:id).pluck(:id,:puntos)
  end
  def test_SEG_006
    _,a,b,game=base
    before=game.attributes.slice('estado','goles_local','goles_visitante')
    patch "/partidos_grupo/#{game.id}/registrar_resultado",params:{partido:{goles_local:'abc',goles_visitante:'1'}}
    assert_equal before,game.reload.attributes.slice('estado','goles_local','goles_visitante')
    assert_equal [0,0],[a.reload.puntos,b.reload.puntos]
  end
end
