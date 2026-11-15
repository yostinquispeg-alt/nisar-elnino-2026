# Oculta en el explorador de VS Code lo interno (.env, cache, __pycache__...). No borra nada.
# Uso: powershell -ExecutionPolicy Bypass -File .\ocultar.ps1
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path (Join-Path $raiz ".vscode") | Out-Null
$settings = @'
{
  "files.exclude": {
    ".env": true,
    ".vscode": true,
    ".gitignore": true,
    "ocultar.ps1": true,
    "cache": true,
    "**/__pycache__": true,
    "**/.ipynb_checkpoints": true,
    "**/.gitkeep": true
  },
  "jupyter.notebookFileRoot": "${fileDirname}"
}
'@
Set-Content -Path (Join-Path $raiz ".vscode\settings.json") -Value $settings -Encoding UTF8
Write-Host "Listo: lo interno queda oculto en VS Code."
