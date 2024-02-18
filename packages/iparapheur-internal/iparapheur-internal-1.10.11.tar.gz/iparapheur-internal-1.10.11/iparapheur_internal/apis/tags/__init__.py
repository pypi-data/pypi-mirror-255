# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from iparapheur_internal.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    ADMINTEMPLATE = "admin-template"
    WORKFLOW = "workflow"
    ADMINTRASHBIN = "admin-trash-bin"
    SERVERINFO = "server-info"
    ADMINADVANCEDCONFIG = "admin-advanced-config"
    TYPOLOGY = "typology"
    ADMINSEALCERTIFICATE = "admin-seal-certificate"
    CURRENTUSER = "current-user"
    ADMINDESK = "admin-desk"
    TEMPLATE = "template"
    ADMINTYPOLOGY = "admin-typology"
    ADMINLAYER = "admin-layer"
    FOLDER = "folder"
    DESK = "desk"
