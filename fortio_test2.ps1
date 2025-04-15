# Ruta de la carpeta
$IMAGES_FOLDER = "C:\Users\emili\Downloads\150MIL-Files"

# Obtener los archivos
$files = Get-ChildItem -Path $IMAGES_FOLDER | Select-Object -First 1

# Ejecutar en paralelo con ForEach-Object -Parallel
$files | ForEach-Object -Parallel {

    $file = $_

    Write-Host "Procesando archivo: $($file.Name)"
    # Variables de configuración
    $BASE_URL = "http://127.0.0.1:5000"
    $UPLOAD_ENDPOINT = "$BASE_URL/upload"
    $INFO_ENDPOINT = "$BASE_URL/images/{0}"
    $FORTIOPATH = ".\fortio.exe"

    # Opciones para Fortio
    $options = @(
        "load",
        "-c", "1",          # 1 hilo concurrente
        "-qps", "0",        # Sin límite de QPS
        "-uniform",
        "-nocatchup",
        "-n", 1             # 1 solicitud por imagen
    )

    try {
        # Leer imagen y codificar en base64
        $ext = [System.IO.Path]::GetExtension($file.FullName).TrimStart('.').ToLower()
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $base64 = [Convert]::ToBase64String($bytes)
        $dataUri = "data:image/$ext;base64,$base64"

        $json = @{
            name  = $file.BaseName
            image = $dataUri
        } | ConvertTo-Json

        $guid = [guid]::NewGuid()
        $jsonPath = "$env:TEMP\$($file.BaseName)_$guid.json"
        $json | Set-Content -Path $jsonPath -Encoding utf8

        # POST con fortio
        & $FORTIOPATH $options -payload-file $jsonPath -content-type 'application/json' $UPLOAD_ENDPOINT

        # GET con fortio
        $getUrl = $INFO_ENDPOINT -f $file.BaseName
        & $FORTIOPATH $options $getUrl

        # Eliminar JSON temporal
        Remove-Item -Path $jsonPath -ErrorAction SilentlyContinue
    }
    catch {
        Write-Error "Error con archivo $($file.FullName): $_"
    }
} -ThrottleLimit 6

Write-Host "Proceso finalizado para todas las imágenes"
