$computerName = $env:computername
$software = Get-WmiObject -Class Win32_Product -ComputerName $computerName

foreach ($app in $software) {
    Write-Host "Name: $($app.Name) Version: $($app.Version)"
}

