# Test PowerShell syntax (no ampersand errors)
Write-Host "== Testing PowerShell Hashtable form encoding ==" -ForegroundColor Cyan

# This should NOT cause ampersand parse errors
$inboundForm = @{
  From = "+12223334444"
  To   = "+19998887777"
  Body = "TEST From FastGoLive"
  MessageSid = "SM1234567"
}

Write-Host "Form data created successfully:" -ForegroundColor Green
$inboundForm | ConvertTo-Json

Write-Host "== Testing JSON encoding ==" -ForegroundColor Cyan
$jsonBody = @{ email="a@b.c"; password="x" } | ConvertTo-Json
Write-Host "JSON body: $jsonBody" -ForegroundColor Green

Write-Host "== PowerShell syntax test PASSED ==" -ForegroundColor Green
