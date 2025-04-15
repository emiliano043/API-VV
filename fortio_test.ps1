$BASE_URL = "http://127.0.0.1:5000"
$UPLOAD_ENDPOINT = "$BASE_URL/upload"
$INFO_ENDPOINT = "$BASE_URL/images/{0}"  
$FORTIOPATH = ".\fortio.exe"

$IMAGES_FOLDER = "C:\Users\emili\Downloads\150MIL-Files" 

# Opciones para Fortio
$options = @(
    "load",
    "-c", "1",          # 1 hilo por cada archivo
    "-qps", "0",        # Sin límite de QPS
    "-uniform",
    "-nocatchup",
    "-n", 1             # 1 solicitud por imagen
)

$MAX_CONCURRENT_JOBS = 6
$jobs = @()

foreach ($file in Get-ChildItem -Path $IMAGES_FOLDER) {
    # Si hay más de 6 trabajos en curso, espera
    if ($jobs.Count -ge $MAX_CONCURRENT_JOBS) {
        $jobs | ForEach-Object { Wait-Job $_; Remove-Job $_ }
        $jobs = @()  # Limpiar la lista de jobs completados
    }

    # Lanzar un nuevo trabajo
    $jobs += Start-Job -ScriptBlock {
        param ($fileName, $filePath, $FORTIOPATH, $UPLOAD_ENDPOINT, $INFO_ENDPOINT, $options)

        # Leer la imagen y codificar a base64
        $ext = [System.IO.Path]::GetExtension($filePath).TrimStart('.').ToLower()
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        $base64 = [Convert]::ToBase64String($bytes)
        $dataUri = "data:image/$ext;base64,$base64"

        $json = @{
            name  = $fileName
            image = $dataUri
        } | ConvertTo-Json

        $jsonPath = "$env:TEMP\$($fileName)_payload.json"
        $json | Set-Content -Path $jsonPath -Encoding utf8

        # Ejecutar POST con Fortio
        Write-Host "Ejecutando POST para: $($fileName)"
        & $FORTIOPATH @options -payload-file $jsonPath -content-type 'application/json' $UPLOAD_ENDPOINT

        # Construir la URL para el GET
        $getUrl = $INFO_ENDPOINT -f $fileName

        # Ejecutar GET con Fortio
        Write-Host "Ejecutando GET en: $getUrl"
        & $FORTIOPATH @options $getUrl

    } -ArgumentList $file.BaseName, $file.FullName, $FORTIOPATH, $UPLOAD_ENDPOINT, $INFO_ENDPOINT, $options
}

# Esperar a que todos los trabajos terminen
$jobs | ForEach-Object { Wait-Job $_; Receive-Job $_; Remove-Job $_ }

Write-Host "Proceso finalizado para todas las imágenes"
