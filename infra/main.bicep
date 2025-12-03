@description('Location for all resources')
param location string = 'westeurope'

@description('Name of the resource group')
param resourceGroupName string = 'rg-devops-graduation'

@description('Name of the Azure Container Registry')
param acrName string = 'acrdevopsgraduation'

@description('SKU for Azure Container Registry')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param acrSku string = 'Basic'

@description('Enable admin user for ACR')
param acrAdminUserEnabled bool = true

@description('Tags to apply to all resources')
param tags object = {
  Environment: 'Development'
  Project: 'DevOps-Graduation'
  ManagedBy: 'Bicep'
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: acrAdminUserEnabled
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: 'Disabled'
    anonymousPullEnabled: false
    dataEndpointEnabled: false
    encryption: {
      status: 'disabled'
    }
  }
}

// Output values
output acrLoginServer string = containerRegistry.properties.loginServer
output acrName string = containerRegistry.name
output acrId string = containerRegistry.id
