# FastGoLive.ps1 - PowerShell 5.x safe, ASCII-only
[CmdletBinding()]
param(
  [Parameter(Mandatory=$false)][string]$ApiDomain = "leadnest-api.onrender.com",
  [Parameter(Mandatory=$false)][string]$FrontendDomain = "leadnest.vercel.app",
  [string]$Email = "a@b.c",
  [string]$Password = "x"
)

$ErrorActionPreference = "Stop"
$Base = "https://$ApiDomain"

Write-Host "== Go-Live: Health checks ==" -ForegroundColor Cyan
$r1 = Invoke-WebRequest -Uri "$Base/healthz" -Method GET
$r2 = Invoke-WebRequest -Uri "$Base/readyz"  -Method GET
Write-Host "Healthz: $($r1.StatusCode)  Readyz: $($r2.StatusCode)" -ForegroundColor Green

Write-Host "== Login & token ==" -ForegroundColor Cyan
$login = Invoke-RestMethod -Uri "$Base/auth/login" -Method POST -ContentType "application/json" -Body (@{ email=$Email; password=$Password } | ConvertTo-Json)
$token = $login.token
if (-not $token) { throw "No JWT token returned from /auth/login" }
$auth = @{ Authorization = "Bearer $token" }

Write-Host "== Protected route /leads ==" -ForegroundColor Cyan
$leads = Invoke-RestMethod -Uri "$Base/leads" -Headers $auth -Method GET
Write-Host "Leads OK (count: $($leads.Count))" -ForegroundColor Green

Write-Host "== Twilio outbound (expect 200 if configured, 503 if not) ==" -ForegroundColor Cyan
try {
  $out = Invoke-RestMethod -Uri "$Base/twilio/send" -Method POST -Headers $auth -ContentType "application/json" -Body (@{ lead_id=7; body="Hello from GoLive" } | ConvertTo-Json)
  Write-Host "Twilio outbound response: $($out | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
  Write-Host "Twilio outbound status (expected if not configured): $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "== Twilio inbound webhook simulation ==" -ForegroundColor Cyan
# Use form body (Hashtable) so PS does the encoding, no '&' needed
$inboundForm = @{
  From = "+12223334444"
  To   = "+19998887777"
  Body = "TEST From FastGoLive"
  MessageSid = "SM1234567"
}
$inb = Invoke-RestMethod -Uri "$Base/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $inboundForm
Write-Host "Inbound OK: $($inb)" -ForegroundColor Green

Write-Host "== All go-live checks completed ==" -ForegroundColor Green
