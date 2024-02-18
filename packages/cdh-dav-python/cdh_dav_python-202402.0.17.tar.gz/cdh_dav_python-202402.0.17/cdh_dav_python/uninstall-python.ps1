# Requires -RunAsAdministrator

# Get all installed Python versions
$pythonInstallations = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.DisplayName -like "Python *" }

# If no installations are found, check in the 32-bit registry path
if (-not $pythonInstallations) {
    $pythonInstallations = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
        Where-Object { $_.DisplayName -like "Python *" }
}

# Uninstall each found version
foreach ($python in $pythonInstallations) {
    $uninstallString = $python.UninstallString
    if ($uninstallString) {
        Write-Host "Uninstalling $($python.DisplayName)"
        Start-Process cmd -ArgumentList "/c $uninstallString /quiet" -Wait
    }
}

Write-Host "Uninstallation complete."
