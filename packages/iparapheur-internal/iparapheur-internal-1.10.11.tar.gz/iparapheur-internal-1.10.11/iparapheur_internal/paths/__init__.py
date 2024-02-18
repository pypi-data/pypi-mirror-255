# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from iparapheur_internal.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    API_INTERNAL_CURRENT_USER_PASSWORD = "/api/internal/currentUser/password"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_LAYER_LAYER_ID = "/api/internal/admin/tenant/{tenantId}/layer/{layerId}"
    API_INTERNAL_ADMIN_CONFIG_CHORUSCONFIGURATION = "/api/internal/admin/config/chorus-configuration"
    API_INTERNAL_TENANT_TENANT_ID_TEMPLATES_TEMPLATE_TYPE_EXAMPLE = "/api/internal/tenant/{tenantId}/templates/{templateType}/example"
    API_INTERNAL_TENANT_TENANT_ID_FOLDER_FOLDER_ID_SIGNATUREREPORT = "/api/internal/tenant/{tenantId}/folder/{folderId}/signature-report"
    API_INTERNAL_TENANT_TENANT_ID_DESK_DESK_ID_SEARCH_STATE = "/api/internal/tenant/{tenantId}/desk/{deskId}/search/{state}"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_TESTSIGNATUREPDFTEMPLATE = "/api/internal/admin/tenant/{tenantId}/test-signature-pdf-template"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_TESTMAILTEMPLATE = "/api/internal/admin/tenant/{tenantId}/test-mail-template"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_TESTDOCKETPDFTEMPLATE = "/api/internal/admin/tenant/{tenantId}/test-docket-pdf-template"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_LAYER = "/api/internal/admin/tenant/{tenantId}/layer"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_LAYER_LAYER_ID_STAMP = "/api/internal/admin/tenant/{tenantId}/layer/{layerId}/stamp"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_LAYER_EXAMPLEPDF = "/api/internal/admin/tenant/{tenantId}/layer/example-pdf"
    API_INTERNAL_TENANT_TENANT_ID_TYPOLOGY_TYPE_TYPE_ID = "/api/internal/tenant/{tenantId}/typology/type/{typeId}"
    API_INTERNAL_TENANT_TENANT_ID_TYPOLOGY_TYPE_TYPE_ID_SUBTYPE_SUBTYPE_ID = "/api/internal/tenant/{tenantId}/typology/type/{typeId}/subtype/{subtypeId}"
    API_INTERNAL_TENANT_TENANT_ID_DESK_DESK_ID_WORKFLOWDEFINITION_WORKFLOW_DEFINITION_KEY = "/api/internal/tenant/{tenantId}/desk/{deskId}/workflow-definition/{workflowDefinitionKey}"
    API_INTERNAL_TENANT_TENANT_ID_DESK_DESK_ID_ASSOCIATED_DESKS = "/api/internal/tenant/{tenantId}/desk/{deskId}/associatedDesks"
    API_INTERNAL_SERVER_INFO_PASSWORD_POLICIES = "/api/internal/serverInfo/passwordPolicies"
    API_INTERNAL_SERVER_INFO_GDPR = "/api/internal/serverInfo/gdpr"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_TYPOLOGY = "/api/internal/admin/tenant/{tenantId}/typology"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_TRASHBIN = "/api/internal/admin/tenant/{tenantId}/trash-bin"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_SEAL_CERTIFICATE_SEAL_CERTIFICATE_ID_SUBTYPE_USAGE = "/api/internal/admin/tenant/{tenantId}/sealCertificate/{sealCertificateId}/subtypeUsage"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_SEAL_CERTIFICATE_SEAL_CERTIFICATE_ID_SIGNATURE_IMAGE = "/api/internal/admin/tenant/{tenantId}/sealCertificate/{sealCertificateId}/signatureImage"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_DESK = "/api/internal/admin/tenant/{tenantId}/desk"
    API_INTERNAL_ADMIN_CONFIG_CHORUS = "/api/internal/admin/config/chorus"
    API_INTERNAL_ADMIN_TENANT_TENANT_ID_LAYER_LAYER_ID_STAMP_STAMP_ID = "/api/internal/admin/tenant/{tenantId}/layer/{layerId}/stamp/{stampId}"
