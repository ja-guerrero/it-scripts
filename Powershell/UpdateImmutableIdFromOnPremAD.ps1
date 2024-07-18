# Import necessary modules
Import-Module ActiveDirectory
Import-Module AzureAD

# Function to generate Immutable ID from GUID
function Convert-GuidToImmutableId {
    param (
        [Parameter(Mandatory = $true)]
        [Guid]$Guid
    )

    $guidBytes = $Guid.ToByteArray()
    $immutableId = [Convert]::ToBase64String($guidBytes)
    return $immutableId
}

# Function to get on-prem AD user object GUID
function Get-OnPremUserGuid {
    param (
        [Parameter(Mandatory = $true)]
        [string]$UserPrincipalName
    )

    $user = Get-ADUser -Filter { UserPrincipalName -eq $UserPrincipalName } -Properties objectGUID
    if ($user) {
        return $user.objectGUID
    } else {
        Write-Error "User not found in on-prem AD: $UserPrincipalName"
        return $null
    }
}

# Function to set the Immutable ID for a given user in Azure AD
function Set-AzureADUserImmutableId {
    param (
        [Parameter(Mandatory = $true)]
        [string]$UserPrincipalName,
        [Parameter(Mandatory = $true)]
        [string]$ImmutableId
    )

    try {
        $user = Get-AzureADUser -ObjectId $UserPrincipalName
        if ($user) {
            Set-AzureADUser -ObjectId $user.ObjectId -ImmutableId $ImmutableId
            Write-Output "Immutable ID set for user: $UserPrincipalName"
        } else {
            Write-Error "User not found in Azure AD: $UserPrincipalName"
        }
    } catch {
        Write-Error "Failed to set Immutable ID for user: $UserPrincipalName. Error: $_"
    }
}

# Connect to Azure AD
Connect-AzureAD

# Get all users in Azure AD
$azureADUsers = Get-AzureADUser -All $true

foreach ($azureADUser in $azureADUsers) {
    $upn = $azureADUser.UserPrincipalName
    $onPremUserGuid = Get-OnPremUserGuid -UserPrincipalName $upn

    if ($onPremUserGuid) {
        $immutableId = Convert-GuidToImmutableId -Guid $onPremUserGuid
        Set-AzureADUserImmutableId -UserPrincipalName $upn -ImmutableId $immutableId
    }
}

# Disconnect from Azure AD
Disconnect-AzureAD

Write-Output "Immutable ID update completed for all users."
