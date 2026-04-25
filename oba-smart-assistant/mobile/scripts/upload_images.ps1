# PowerShell script to upload product images to Supabase Storage
# Run from mobile folder: .\scripts\upload_images.ps1

$supabaseUrl = "https://keleythlzrtmvoetixcl.supabase.co"
$serviceKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlbGV5dGhsenJ0bXZvZXRpeGNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTE3OTMyMywiZXhwIjoyMDg0NzU1MzIzfQ.AtEPGg_hVYzJOjwPLaOdRkozemgiLL8ILCp9v2OOxV4"
$bucket = "product-images"
$imagesPath = "assets/images/products"

$files = Get-ChildItem -Path $imagesPath -Filter "*.webp"
$total = $files.Count
$current = 0
$uploaded = 0
$failed = 0
$uploadedImages = @()

Write-Host "Found $total product images to upload" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $files) {
    $current++
    $fileName = $file.Name
    # Convert to URL-safe name (replace spaces with underscores, lowercase)
    $safeName = $fileName.ToLower().Replace(" ", "_")
    $filePath = $file.FullName
    
    Write-Host "[$current/$total] Uploading: $fileName" -NoNewline
    
    try {
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        
        $headers = @{
            "Authorization" = "Bearer $serviceKey"
            "apikey" = $serviceKey
            "Content-Type" = "image/webp"
            "x-upsert" = "true"
        }
        
        $uri = "$supabaseUrl/storage/v1/object/$bucket/$safeName"
        
        $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $bytes -ErrorAction Stop
        
        Write-Host " ✓" -ForegroundColor Green
        $uploaded++
        
        $publicUrl = "$supabaseUrl/storage/v1/object/public/$bucket/$safeName"
        $uploadedImages += @{
            "original" = $fileName
            "safe" = $safeName
            "url" = $publicUrl
        }
    } catch {
        Write-Host " ✗ ($($_.Exception.Message))" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload complete!" -ForegroundColor Green
Write-Host "Uploaded: $uploaded" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "Public URL format:"
Write-Host "$supabaseUrl/storage/v1/object/public/$bucket/<filename>"
