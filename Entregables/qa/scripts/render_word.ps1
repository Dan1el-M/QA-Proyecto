param([string]$DocumentPath='docs/Informe_Final_QA_Mundial.docx',[string]$OutputDirectory='qa/reports/document-render')
$ErrorActionPreference='Stop'
$qaDeliverablesRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(-not [IO.Path]::IsPathRooted($DocumentPath)) {$DocumentPath=Join-Path $qaDeliverablesRoot $DocumentPath}
if(-not [IO.Path]::IsPathRooted($OutputDirectory)) {$OutputDirectory=Join-Path $qaDeliverablesRoot $OutputDirectory}
$qaDocPath=(Resolve-Path -LiteralPath $DocumentPath).Path
$qaOutPath=[IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $qaOutPath | Out-Null
$qaWord=$null
$qaDocument=$null
try {
  $qaWord=New-Object -ComObject Word.Application
  $qaWord.Visible=$false
  $qaWord.DisplayAlerts=0
  $qaWord.AutomationSecurity=3
  $qaDocument=$qaWord.Documents.Open($qaDocPath,$false,$false,$false)
  $qaDocument.Fields.Update() | Out-Null
  foreach($qaToc in $qaDocument.TablesOfContents) {$qaToc.Update()}
  foreach($qaIndex in $qaDocument.TablesOfFigures) {$qaIndex.Update()}
  $qaDocument.Repaginate()
  $qaDocument.Fields.Update() | Out-Null
  $qaPages=$qaDocument.ComputeStatistics(2)
  $qaDocument.Save()
  $qaPdf=Join-Path $qaOutPath 'Informe_Final_QA_Mundial.pdf'
  $qaDocument.ExportAsFixedFormat($qaPdf,17)
  @{renderer='Microsoft Word COM';pages=$qaPages;pdf=$qaPdf;field_update=$true;rendered_at=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $qaOutPath 'render.json') -Encoding UTF8
  Write-Output "Word rendered: $qaPages pages."
} finally {
  if($qaDocument){try {$qaDocument.Close($false)} catch {Write-Verbose $_}}
  if($qaWord){try {$qaWord.Quit()} catch {Write-Verbose $_}}
}
