# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from iparapheur_provisioning.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    ADMINTEMPLATE = "admin-template"
    ADMINTENANTUSER = "admin-tenant-user"
    ADMINDESK = "admin-desk"
    ADMINMETADATA = "admin-metadata"
    ADMINTYPOLOGY = "admin-typology"
    ADMINWORKFLOWDEFINITION = "admin-workflow-definition"
    ADMINTENANT = "admin-tenant"
    ADMINALLUSERS = "admin-all-users"
    ADMINSEALCERTIFICATE = "admin-seal-certificate"
