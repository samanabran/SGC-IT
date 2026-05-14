# Try to get GitHub token from environment or git credentials
$token = $env:GITHUB_TOKEN

if (-not $token) {
    # Try git credential
    $credInput = @"
protocol=https
host=github.com

"@
    try {
        $credOutput = $credInput | git credential fill 2>$null
        if ($credOutput) {
            foreach ($line in $credOutput -split "`n") {
                if ($line -match "^password=(.+)$") {
                    $token = $matches[1]
                    break
                }
            }
        }
    } catch {
        Write-Host "Could not retrieve credentials from git"
    }
}

if ($token) {
    Write-Host "Found token (length: $($token.Length))"
    # Try to enable Pages using the token
    $headers = @{
        "Authorization" = "Bearer $token"
        "Accept" = "application/vnd.github+json"
    }
    $body = @{
        "source" = @{
            "branch" = "main"
            "path" = "/"
        }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest `
        -Uri "https://api.github.com/repos/samanabran/SGC-IT/pages" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -UseBasicParsing `
        -ErrorAction SilentlyContinue
    
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
        Write-Host "✓ GitHub Pages enabled successfully!"
        $result = $response.Content | ConvertFrom-Json
        Write-Host "URL: https://samanabran.github.io/SGC-IT/"
    } else {
        Write-Host "Response: $($response.StatusCode)"
        Write-Host $response.Content
    }
} else {
    Write-Host "✗ No authentication token found"
    Write-Host "Please try: https://github.com/samanabran/SGC-IT/settings/pages"
}
