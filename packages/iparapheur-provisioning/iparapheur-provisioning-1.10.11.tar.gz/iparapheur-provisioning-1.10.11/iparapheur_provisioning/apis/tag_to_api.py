import typing_extensions

from iparapheur_provisioning.apis.tags import TagValues
from iparapheur_provisioning.apis.tags.admin_template_api import AdminTemplateApi
from iparapheur_provisioning.apis.tags.admin_tenant_user_api import AdminTenantUserApi
from iparapheur_provisioning.apis.tags.admin_desk_api import AdminDeskApi
from iparapheur_provisioning.apis.tags.admin_metadata_api import AdminMetadataApi
from iparapheur_provisioning.apis.tags.admin_typology_api import AdminTypologyApi
from iparapheur_provisioning.apis.tags.admin_workflow_definition_api import AdminWorkflowDefinitionApi
from iparapheur_provisioning.apis.tags.admin_tenant_api import AdminTenantApi
from iparapheur_provisioning.apis.tags.admin_all_users_api import AdminAllUsersApi
from iparapheur_provisioning.apis.tags.admin_seal_certificate_api import AdminSealCertificateApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.ADMINTEMPLATE: AdminTemplateApi,
        TagValues.ADMINTENANTUSER: AdminTenantUserApi,
        TagValues.ADMINDESK: AdminDeskApi,
        TagValues.ADMINMETADATA: AdminMetadataApi,
        TagValues.ADMINTYPOLOGY: AdminTypologyApi,
        TagValues.ADMINWORKFLOWDEFINITION: AdminWorkflowDefinitionApi,
        TagValues.ADMINTENANT: AdminTenantApi,
        TagValues.ADMINALLUSERS: AdminAllUsersApi,
        TagValues.ADMINSEALCERTIFICATE: AdminSealCertificateApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.ADMINTEMPLATE: AdminTemplateApi,
        TagValues.ADMINTENANTUSER: AdminTenantUserApi,
        TagValues.ADMINDESK: AdminDeskApi,
        TagValues.ADMINMETADATA: AdminMetadataApi,
        TagValues.ADMINTYPOLOGY: AdminTypologyApi,
        TagValues.ADMINWORKFLOWDEFINITION: AdminWorkflowDefinitionApi,
        TagValues.ADMINTENANT: AdminTenantApi,
        TagValues.ADMINALLUSERS: AdminAllUsersApi,
        TagValues.ADMINSEALCERTIFICATE: AdminSealCertificateApi,
    }
)
