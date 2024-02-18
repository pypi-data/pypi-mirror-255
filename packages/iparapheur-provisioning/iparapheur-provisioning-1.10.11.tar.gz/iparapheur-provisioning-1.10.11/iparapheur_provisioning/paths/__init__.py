# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from iparapheur_provisioning.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    API_PROVISIONING_V1_ADMIN_USER_USER_ID = "/api/provisioning/v1/admin/user/{userId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID = "/api/provisioning/v1/admin/tenant/{tenantId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_WORKFLOWDEFINITION_WORKFLOW_DEFINITION_KEY = "/api/provisioning/v1/admin/tenant/{tenantId}/workflow-definition/{workflowDefinitionKey}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_USER_USER_ID = "/api/provisioning/v1/admin/tenant/{tenantId}/user/{userId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_TYPOLOGY_TYPE_TYPE_ID = "/api/provisioning/v1/admin/tenant/{tenantId}/typology/type/{typeId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_TYPOLOGY_TYPE_TYPE_ID_SUBTYPE_SUBTYPE_ID = "/api/provisioning/v1/admin/tenant/{tenantId}/typology/type/{typeId}/subtype/{subtypeId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_TEMPLATES_TEMPLATE_TYPE = "/api/provisioning/v1/admin/tenant/{tenantId}/templates/{templateType}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_SEAL_CERTIFICATE_SEAL_CERTIFICATE_ID = "/api/provisioning/v1/admin/tenant/{tenantId}/sealCertificate/{sealCertificateId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_METADATA_METADATA_ID = "/api/provisioning/v1/admin/tenant/{tenantId}/metadata/{metadataId}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_DESK_DESK_ID = "/api/provisioning/v1/admin/tenant/{tenantId}/desk/{deskId}"
    API_PROVISIONING_V1_ADMIN_USER = "/api/provisioning/v1/admin/user"
    API_PROVISIONING_V1_ADMIN_TENANT = "/api/provisioning/v1/admin/tenant"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_WORKFLOWDEFINITION = "/api/provisioning/v1/admin/tenant/{tenantId}/workflow-definition"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_USER = "/api/provisioning/v1/admin/tenant/{tenantId}/user"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_TYPOLOGY_TYPE = "/api/provisioning/v1/admin/tenant/{tenantId}/typology/type"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_TYPOLOGY_TYPE_TYPE_ID_SUBTYPE = "/api/provisioning/v1/admin/tenant/{tenantId}/typology/type/{typeId}/subtype"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_SEAL_CERTIFICATE = "/api/provisioning/v1/admin/tenant/{tenantId}/sealCertificate"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_METADATA = "/api/provisioning/v1/admin/tenant/{tenantId}/metadata"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_DESK = "/api/provisioning/v1/admin/tenant/{tenantId}/desk"
    API_PROVISIONING_V1_TENANT_TENANT_ID_TEMPLATES_TEMPLATE_TYPE = "/api/provisioning/v1/tenant/{tenantId}/templates/{templateType}"
    API_PROVISIONING_V1_TEMPLATES_TEMPLATE_TYPE = "/api/provisioning/v1/templates/{templateType}"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_WORKFLOW_DEFINITION = "/api/provisioning/v1/admin/tenant/{tenantId}/workflowDefinition"
    API_PROVISIONING_V1_ADMIN_INTERNALMETADATA = "/api/provisioning/v1/admin/internal-metadata"
    API_PROVISIONING_V1_ADMIN_TENANT_TENANT_ID_WORKFLOW_DEFINITION_WORKFLOW_DEFINITION_KEY = "/api/provisioning/v1/admin/tenant/{tenantId}/workflowDefinition/{workflowDefinitionKey}"
