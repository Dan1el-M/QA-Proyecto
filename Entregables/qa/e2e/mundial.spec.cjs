const {test,expect}=require('@playwright/test');
const {spawnSync}=require('node:child_process');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
function reset(profile='base') {
  const result=spawnSync('ruby',['qa/scripts/prepare.rb',profile],{cwd:root,env:process.env,encoding:'utf8',windowsHide:true});
  if(result.status!==0) throw Error('Dataset preparation failed: '+result.stdout+result.stderr);
}
test.beforeEach(async({page})=>{
  await page.route('**/*',route=>{
    const u=new URL(route.request().url());
    return ['127.0.0.1','localhost'].includes(u.hostname)||u.protocol==='data:' ? route.continue() : route.abort();
  });
});
test('E2E-001 Consulta de selecciones',async function test_E2E_001({page}){
  reset();await page.goto('/');await expect(page.locator('tr[data-seleccion-id]').first()).toContainText('Equipo QA A 1');
  await page.screenshot({path:path.join(process.env.QA_RUN_DIR,'pantalla_selecciones.png'),fullPage:true});
});
test('E2E-002 Registro de selección',async function test_E2E_002({page}){
  reset('empty');await page.goto('/');await page.locator('#seleccion_nombre').fill('Equipo UI');
  await page.locator('#seleccion_acronimo').fill('QAZ');await page.locator('#seleccion_grupo_id').selectOption({label:'A'});
  await page.getByRole('button',{name:/Registrar Seleccion/}).click();await page.reload();
  await expect(page.locator('tr[data-seleccion-id]').filter({hasText:'Equipo UI'})).toBeVisible();
});
test('E2E-003 Consulta de grupo',async function test_E2E_003({page}){
  reset();await page.goto('/');const group=await page.locator('#seleccion_grupo_id option').filter({hasText:/^A$/}).getAttribute('value');
  await page.goto('/grupos/'+group);await expect(page.getByRole('heading',{name:/Detalles del Grupo A/})).toBeVisible();
  await expect(page.getByText('Equipo QA A 1',{exact:true}).first()).toBeVisible();
  await page.screenshot({path:path.join(process.env.QA_RUN_DIR,'pantalla_grupo.png'),fullPage:true});
});
test('E2E-004 Registro de marcador por calendario',async function test_E2E_004({page}){
  reset();await page.goto('/partidos_grupo/calendario');const form=page.locator('article form').first();
  await expect(form.locator('[name="partido[goles_visitante]"]')).toHaveCount(1);
  await form.locator('[name="partido[goles_local]"]').fill('2');await form.locator('[name="partido[goles_visitante]"]').fill('1');
  await form.getByRole('button',{name:/Guardar marcador/}).click();await page.reload();
  await expect(page.locator('article').first()).toContainText('Finalizado');
  await expect(page.locator('article').first().locator('[name="partido[goles_visitante]"]')).toHaveValue('1');
});
test('E2E-005 Frontera de marcador negativo',async function test_E2E_005({page}){
  reset();await page.goto('/partidos_grupo/calendario');const field=page.locator('article input[type=number]').first();
  await field.fill('-1');expect(await field.evaluate(el=>el.checkValidity())).toBe(false);
  await page.reload();await expect(field).toHaveValue('');
});
test('E2E-006 Consulta de tabla de posiciones',async function test_E2E_006({page}){
  reset('finished');await page.goto('/partidos_grupo/calendario');
  await expect(page.getByText('Tabla del Grupo A',{exact:true})).toBeVisible();
  await expect(page.locator('table')).toContainText('Equipo QA A 1');
  await page.screenshot({path:path.join(process.env.QA_RUN_DIR,'pantalla_calendario.png'),fullPage:true});
});
test('E2E-007 Bloqueo de avance prematuro',async function test_E2E_007({page}){
  reset();const response=await page.goto('/fase_eliminatoria');expect(response.status()).toBeLessThan(400);
  await expect(page.locator('body')).toContainText(/progreso|completa|pendiente/i);
  await expect(page.locator('[name*="resultados["]')).toHaveCount(0);
});
test('E2E-008 Guardar eliminatoria y generar octavos',async function test_E2E_008({page}){
  reset('knockout');await page.goto('/fase_eliminatoria');
  const locals=page.locator('input[data-gol-local]:enabled');const visitors=page.locator('input[data-gol-visitante]:enabled');
  const count=await locals.count();expect(count).toBe(16);
  for(let i=0;i<count;i++){await locals.nth(i).fill('2');await visitors.nth(i).fill('1');}
  await page.getByRole('button',{name:/Guardar|Actualizar/}).first().click();
  await expect(page.locator('body')).not.toContainText(/NoMethodError|Internal Server Error|undefined method/);
  await expect(page.locator('body')).toContainText(/generados automáticamente|generados automaticamente/i);
});
test('E2E-009 Podio final en interfaz',async function test_E2E_009({page}){
  reset('podium');await page.goto('/campeones/podio');
  await expect(page.locator('body')).toContainText('Equipo QA A 1');
  await expect(page.locator('body')).toContainText('Equipo QA A 2');
  await expect(page.locator('body')).toContainText('Equipo QA A 3');
  await page.screenshot({path:path.join(process.env.QA_RUN_DIR,'pantalla_podio.png'),fullPage:true});
});
