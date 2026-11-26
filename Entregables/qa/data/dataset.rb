module QaDataset
  def qa_group(letter='A') = Grupo.create!(letra: letter, torneo: qa_tournament)
  def qa_tournament = (@qa_tournament ||= Torneo.create!(nombre: 'Torneo QA sintético'))
  def qa_team(group, index)
    acronym = 'Q'+(65+index/26).chr+(65+index%26).chr
    Seleccion.create!(nombre: "Equipo QA #{(65+index/4).chr} #{index%4+1}",acronimo:acronym,grupo:group)
  end
  def qa_match(local, visitor, number=1, knockout=false)
    Partido.create!(numero_partido:number,tipo_partido:knockout ? 'eliminacion_directa' : 'fase_grupos',
                    estado:'programado',grupo:knockout ? nil : local.grupo,torneo:qa_tournament,
                    seleccion_local:local,seleccion_visitante:visitor)
  end
  def qa_full(finished=false)
    ('A'..'L').each_with_index do |letter,i|
      group=qa_group(letter)
      teams=4.times.map { |j| qa_team(group,i*4+j) }
      teams.combination(2).each_with_index do |(a,b),j|
        game=qa_match(a,b,i*6+j+1)
        game.registrar_resultado!(2,1) if finished
      end
    end
  end
  def qa_clear!
    abort 'Unsafe QA database' unless Rails.env.test? && ActiveRecord::Base.connection_db_config.database.tr('\\','/').end_with?('/qa/data/qa.sqlite3')
    Torneo.update_all(campeon_id:nil,subcampeon_id:nil,tercero_id:nil)
    Partido.delete_all
    Seleccion.delete_all
    Grupo.delete_all
    Torneo.delete_all
    @qa_tournament=nil
  end
  def qa_profile(profile)
    qa_clear!
    if profile=='empty'
      qa_group
      return
    end
    qa_full(profile!='base')
    if profile=='knockout'
      teams=DeterminarClasificados.obtener[:total_clasificados]
      teams.each_slice(2).with_index { |(a,b),i| qa_match(a,b,73+i,true) }
    elsif profile=='podium'
      teams=Seleccion.order(:id).limit(4).to_a
      qa_match(teams[2],teams[3],103,true).registrar_resultado!(2,1)
      qa_match(teams[0],teams[1],104,true).registrar_resultado!(3,1)
    end
  end
end
