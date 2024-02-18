import typing_extensions

from iparapheur_internal.apis.tags import TagValues
from iparapheur_internal.apis.tags.admin_template_api import AdminTemplateApi
from iparapheur_internal.apis.tags.workflow_api import WorkflowApi
from iparapheur_internal.apis.tags.admin_trash_bin_api import AdminTrashBinApi
from iparapheur_internal.apis.tags.server_info_api import ServerInfoApi
from iparapheur_internal.apis.tags.admin_advanced_config_api import AdminAdvancedConfigApi
from iparapheur_internal.apis.tags.typology_api import TypologyApi
from iparapheur_internal.apis.tags.admin_seal_certificate_api import AdminSealCertificateApi
from iparapheur_internal.apis.tags.current_user_api import CurrentUserApi
from iparapheur_internal.apis.tags.admin_desk_api import AdminDeskApi
from iparapheur_internal.apis.tags.template_api import TemplateApi
from iparapheur_internal.apis.tags.admin_typology_api import AdminTypologyApi
from iparapheur_internal.apis.tags.admin_layer_api import AdminLayerApi
from iparapheur_internal.apis.tags.folder_api import FolderApi
from iparapheur_internal.apis.tags.desk_api import DeskApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.ADMINTEMPLATE: AdminTemplateApi,
        TagValues.WORKFLOW: WorkflowApi,
        TagValues.ADMINTRASHBIN: AdminTrashBinApi,
        TagValues.SERVERINFO: ServerInfoApi,
        TagValues.ADMINADVANCEDCONFIG: AdminAdvancedConfigApi,
        TagValues.TYPOLOGY: TypologyApi,
        TagValues.ADMINSEALCERTIFICATE: AdminSealCertificateApi,
        TagValues.CURRENTUSER: CurrentUserApi,
        TagValues.ADMINDESK: AdminDeskApi,
        TagValues.TEMPLATE: TemplateApi,
        TagValues.ADMINTYPOLOGY: AdminTypologyApi,
        TagValues.ADMINLAYER: AdminLayerApi,
        TagValues.FOLDER: FolderApi,
        TagValues.DESK: DeskApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.ADMINTEMPLATE: AdminTemplateApi,
        TagValues.WORKFLOW: WorkflowApi,
        TagValues.ADMINTRASHBIN: AdminTrashBinApi,
        TagValues.SERVERINFO: ServerInfoApi,
        TagValues.ADMINADVANCEDCONFIG: AdminAdvancedConfigApi,
        TagValues.TYPOLOGY: TypologyApi,
        TagValues.ADMINSEALCERTIFICATE: AdminSealCertificateApi,
        TagValues.CURRENTUSER: CurrentUserApi,
        TagValues.ADMINDESK: AdminDeskApi,
        TagValues.TEMPLATE: TemplateApi,
        TagValues.ADMINTYPOLOGY: AdminTypologyApi,
        TagValues.ADMINLAYER: AdminLayerApi,
        TagValues.FOLDER: FolderApi,
        TagValues.DESK: DeskApi,
    }
)
