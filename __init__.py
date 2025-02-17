# coding: utf-8
"""
Base para desarrollo de modulos externos.
Para obtener el modulo/Funcion que se esta llamando:
     GetParams("module")

Para obtener las variables enviadas desde formulario/comando Rocketbot:
    var = GetParams(variable)
    Las "variable" se define en forms del archivo package.json

Para modificar la variable de Rocketbot:
    SetVar(Variable_Rocketbot, "dato")

Para obtener una variable de Rocketbot:
    var = GetVar(Variable_Rocketbot)

Para obtener la Opcion seleccionada:
    opcion = GetParams("option")


Para instalar librerias se debe ingresar por terminal a la carpeta "libs"
    
   sudo pip install <package> -t .

"""

base_path = tmp_global_obj["basepath"]
cur_path = base_path + "modules" + os.sep + "O365" + os.sep + "libs" + os.sep
if cur_path not in sys.path:
    sys.path.append(cur_path)
from copy import deepcopy
from enum import Enum
import trace
from O365 import Account
import traceback
from bs4 import BeautifulSoup
import os

module = GetParams("module")

global mod_o365_session
global OutlookWellKnowFolderNames

OutlookWellKnowFolderNames= {
        'Inbox': 'Inbox',
        'Junk': 'JunkEmail',
        'Deleted Items': 'DeletedItems',
        'Drafts': 'Drafts',
        'Sent': 'SentItems',
        'Outbox': 'Outbox',
        'Archive': 'Archive'
    }

session = GetParams("session")
if not session:
    session = ''

try:
    if not mod_o365_session : #type:ignore
        mod_o365_session = {}
except NameError:
    mod_o365_session = {}

if module == "connect":
    client_id = GetParams("client_id")
    client_secret = GetParams("client_secret")
    tenant = GetParams("tenant")
    sharepoint_ = GetParams('sharepoint')

    if session == '':
        filename = "o365_token.txt"
    else:
        filename = "o365_token_{s}.txt".format(s=session)
    
    scopes_ = ['basic', 'message_all']
    
    if sharepoint_:
        if eval(sharepoint_):
            scopes_.append('sharepoint')
    
    try:
        credentials = (client_id, client_secret)
        mod_o365_session[session] = Account(credentials, tenant_id = tenant, token_filename = filename)
        if not mod_o365_session[session].is_authenticated:
            mod_o365_session[session].authenticate(scopes=scopes_)
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "sendEmail":
    to_ = GetParams("to_")
    cc = GetParams("cc")
    subject = GetParams("subject")
    body = GetParams("body")
    attached_file = GetParams("attached_file")
    attached_folder = GetParams("attached_folder")
    
    try:
        message = mod_o365_session[session].new_message()
        if not to_:
            raise Exception("'To' field must not be empty.")
        list_to = to_.split(",")
        message.to.add(list_to)
        if cc:
            list_cc = cc.split(",")
            message.cc.add(list_cc)
        message.subject = subject
        message.body = body
        if attached_file:
            message.attachments.add(attached_file)
        if attached_folder:
            filenames = []
            for f in os.listdir(attached_folder):
                f = os.path.join(attached_folder, f)
                filenames.append(f)
            message.attachments.add(filenames)
        message.send()
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "replyEmail":
    id_ = GetParams("id_")
    cc = GetParams("cc")
    body = GetParams("body")
    attached_file = GetParams("attached_file")
    attached_folder = GetParams("attached_folder")
    read = GetParams("markasread")
    
    if not id_:
        raise Exception("Missing Email ID...")
    
    try:
        message = mod_o365_session[session].mailbox().get_message(id_)
        reply = message.reply()
        if cc:
            list_cc = cc.split(",")
            reply.cc.add(list_cc)
        reply.body = body
        
        if attached_file:
            reply.attachments.add(attached_file)
        if attached_folder:
            filenames = []
            for f in os.listdir(attached_folder):
                f = os.path.join(attached_folder, f)
                filenames.append(f)
            reply.attachments.add(filenames)
        reply.send()
        
        if read:
            if eval(read) == True:
                message.mark_as_read()
        
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "forwardEmail":
    to_ = GetParams("to_")
    cc = GetParams("cc")
    id_ = GetParams("id_")
    body = GetParams("body")
    attached_file = GetParams("attached_file")
    attached_folder = GetParams("attached_folder")
    read = GetParams("markasread")
    
    if not id_:
        raise Exception("Missing Email ID...")
    
    try:
        message = mod_o365_session[session].mailbox().get_message(id_)
        forward = message.forward()
        if not to_:
            raise Exception("'To' field must not be empty.")
        list_to = to_.split(",")
        forward.to.add(list_to)
        if cc:
            list_cc = cc.split(",")
            forward.cc.add(list_cc)
        forward.body = body
        
        if attached_file:
            forward.attachments.add(attached_file)
        if attached_folder:
            filenames = []
            for f in os.listdir(attached_folder):
                f = os.path.join(attached_folder, f)
                filenames.append(f)
            forward.attachments.add(filenames)
        forward.send()
        
        if read:
            if eval(read) == True:
                message.mark_as_read()
        
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "getAllEmails":
    folder = GetParams("folder")
    res = GetParams("res")
    limit = GetParams("limit")
    filter = GetParams("filtro") or GetParams("filter")
    
    if OutlookWellKnowFolderNames.get(folder) == None:
        pass
    else:
        folder = OutlookWellKnowFolderNames.get(folder)
    
    if folder == "" or folder == None:
        folder = "Inbox"
    
    if limit and limit != "":
        limit = int(limit)
    else:
        limit = None
    
    try:
        list_messages = mod_o365_session[session].mailbox().folder_constructor(parent=mod_o365_session[session].mailbox(), name=folder,
                                                             folder_id=folder).get_messages(limit=limit, query=filter)
        list_object_id = []
        for message in list_messages:
            list_object_id.append(message.object_id)
        SetVar(res, list_object_id)
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "getUnreadEmails":
    folder = GetParams("folder")
    res = GetParams("res")
    limit = GetParams("limit")
    
    if OutlookWellKnowFolderNames.get(folder) == None:
        pass
    else:
        folder = OutlookWellKnowFolderNames.get(folder)
    
    if folder == "" or folder == None:
        folder = "Inbox"
    
    if limit and limit != "":
        limit = int(limit)
    else:
        limit = None
    
    try:
        list_messages = mod_o365_session[session].mailbox().folder_constructor(parent=mod_o365_session[session].mailbox(), name=folder,
                                                             folder_id=folder).get_messages(limit=limit, query='isRead eq false')
        list_object_id = []
        for message in list_messages:
            list_object_id.append(message.object_id)
        SetVar(res, list_object_id)
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "readEmail":
    att_folder = GetParams("att_folder")
    download_att = GetParams("down")
    res = GetParams("res")
    id_ = GetParams("id_")
    read = GetParams("markasread")
    not_parsed = GetParams("not_parsed")
    
    from mailparser import mailparser
    import base64
    
    if not id_:
        raise Exception("Missing Email ID...")
    
    try:
        # It creates a message object and makes available attachments to be downloaded
        message = mod_o365_session[session].mailbox().get_message(id_, download_attachments=True)
        # Get number of attachments using API
        att_q = int(message._Message__attachments.__str__().split(': ')[1])
        
        files = []
        if message._Message__has_attachments == True:
            files_down = []
            # Get actual recognized attachments and compare the quantitiy with the theorical one
            for att in message.attachments:
                files.append(att.name)
                files_down.append(att)
            if (len(files) == att_q) and download_att:
                print('API')
                # If all the conditions are fulfilled then it download the attachments usind the API
                if eval(download_att) == True:
                    for att_down in files_down:
                        att_down.save(att_folder)
            else:
                # If the condition is not fulfilled, then it goes through the alternative method using the Mail Parser library
                print('Parser')
                parsed_mail = mailparser.parse_from_bytes(message.get_mime_content())
                files = []
                for att in parsed_mail.attachments:
                    name = att['filename']
                    name = name.replace("\r","").replace("\n","")
                    files.append(name)
                    
                    if download_att:
                        if eval(download_att) == True:
                            if not os.path.isdir(att_folder):
                                raise Exception('The path does not exist.')
                            
                            cont = base64.b64decode(att['payload'])
                            with open(os.path.join(att_folder, name), 'wb') as file_:
                                file_.write(cont)
                                file_.close()
        
        # This is for the case of an email with no body
        html_body = BeautifulSoup(message.body, "html.parser").body
        
        links = {}
        if html_body:
            for a in html_body.find_all("a"):
                # First checks the text of the a tag    
                if a.get_text():
                    key = a.get_text()
                # If None, then checks if the a tag has 'title'
                elif a.get("title"):
                    key = a["title"]
                # If also None, the it gives a generic key
                else:
                    key = 'URL'
                # Finally it checks if the key already exists and adds a '(n°)' at the end
                x = int()
                while key in links.keys():
                    x += 1
                    key = key + '(' + str(x) + ')'    
                links[key]= a["href"]
                
            if not not_parsed or eval(not_parsed) == False:
                body = html_body.get_text()
            else:
                body = html_body
                    
        message_all = {
            # Recipient object
            'sender': message.sender.address,
            # Iterate over a Recipients object (List of Recipient objects) and parses each element into string
            'cc': [str(rec) for rec in message.cc._recipients],
            'subject': message.subject,
            # Parses elements datetime.datetime into string
            'sent_time': message.sent.strftime('%d-%m-%Y %H:%M'),
            'received': message.received.strftime('%d-%m-%Y %H:%M'),
            'body': body,
            'links': links,
            'files': files
        }
        
        if read:
            if eval(read) == True:
                message.mark_as_read()
        
        SetVar(res, message_all)
    except Exception as e:
        SetVar(res, False)
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e
    
if module == "downAtt":
    res = GetParams("res")
    att_folder = GetParams("att_folder")
    id_ = GetParams("id_")
    read = GetParams("markasread")
    
    from mailparser import mailparser
    import base64
    
    if not id_:
        raise Exception("Missing Email ID...")
    
    try:
        # It creates a message object and makes available attachments to be downloaded
        message = mod_o365_session[session].mailbox().get_message(id_, download_attachments=True)

        att_q = int(message._Message__attachments.__str__().split(': ')[1])
                     
        if message._Message__has_attachments == True:
            files = []
            files_down = []
            # Get actual recognized attachments and compare the quantitiy with the theorical one
            for att in message.attachments:
                files.append(att.name)
                files_down.append(att)
            if (len(files) == att_q):
                print('API')
                # If the conditios is fulfilled then it download the attachments usind the API
                for att_down in files_down:
                    att_down.save(att_folder)
            else:
                print('Parser')
                parsed_mail = mailparser.parse_from_bytes(message.get_mime_content())
                files = []
                for att in parsed_mail.attachments:
                    name = att['filename']
                    name = name.replace("\r","").replace("\n","")
                    files.append(name)
                    
                    if not os.path.isdir(att_folder):
                        raise Exception('The path does not exist.')
                    
                    cont = base64.b64decode(att['payload'])
                    with open(os.path.join(att_folder, name), 'wb') as file_:
                        file_.write(cont)
                        file_.close()
        
        if read:
            if eval(read) == True:
                message.mark_as_read()
        
        SetVar(res, True)
    except Exception as e:
        SetVar(res, False)
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "markUnread":
    res = GetParams("res")
    id_ = GetParams("id_")
    
    if not id_:
        raise Exception("Missing Email ID...")
    
    try:
        # It creates a message object and makes available attachments to be downloaded
        message = mod_o365_session[session].mailbox().get_message(id_)
   
        unread = message.mark_as_unread()
        
        SetVar(res, unread)
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "moveEmail":
    folderId = GetParams("folderId")
    id_ = GetParams("id_")
    res = GetParams("res")
    
    if folderId == "" or folderId == None:
        folderId = "Inbox"
    
    try:
        message = mod_o365_session[session].mailbox().get_message(id_)
        move = message.move(folderId)
        
        SetVar(res, move)
    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "getFolders":
    
    folders = GetParams('res')
    
    try:
        
        data, list_folders = mod_o365_session[session].mailbox().get_folders()
        final_list = deepcopy(data['value'])
        
        while True:
            try:
                list_folders_aux = []
                for folder in list_folders:
                    if isinstance(folder, list):
                        folder = folder[0]
                    child_data, list_child = folder.get_folders()
                    if child_data['value'] == []:
                        continue
                    final_list.append(child_data['value'])
                    list_folders_aux.append(list_child)
                list_folders = list_folders_aux
                print(list_folders)
                if list_folders == []:
                    break
            except:
                print(traceback.format_exc())
                break
        
        SetVar(folders, final_list)
    
    except Exception as e:
        SetVar(folders, False)
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e
    
if module == "newFolder":
    parent = GetParams("parent")
    new_folder = GetParams("new_folder")
    res = GetParams("res")
    
    try:
        try:
            parent = mod_o365_session[session].mailbox().get_folder(folder_id = parent)
        except:
            parent = mod_o365_session[session].mailbox()
        
        parent.create_child_folder(new_folder)
        SetVar(res, True)
    
    except Exception as e:
        SetVar(res, False)
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

"""-----------------------------------------------------------------------------------------------------------------------------------------------------"""

global mod_o365_endpoints

mod_o365_endpoints = {
    'get_user_groups': '/users/{user_id}/memberOf',
    'get_group_by_id': '/groups/{group_id}',
    'get_group_by_mail': '/groups/?$search="mail:{group_mail}"&$count=true',
    'list_groups': '/groups',
    'get_group_site': '/groups/{group_id}/sites/{site_name}',
    'get_site_lists': '/groups/{group_id}/sites/{site_name}/lists',
    'get_list': '/groups/{group_id}/sites/{site_name}/lists/{list_id}/items/'
    }

def list_groups(gs):
    """ Returns list of groups orderer alphabetically by name
    
    :rtype: list[{Group Name: name, Group Id: ID}]
    
    """

    url = gs.build_url(mod_o365_endpoints.get('list_groups'))
    print(url)
    response = gs.con.get(url)

    if not response:
        return None

    data = response.json()

    groups = []
    for g in data['value']:
        group = {}  
        group['displayName'] = g['displayName']
        group['id'] = g['id']
        groups.append(group)
        groups.sort(key = lambda g: g['displayName'])

    return groups

def get_group_by_id(gs, group_id = None):
    """ Returns Microsoft O365/AD group with given id
    :param group_id: group id of group
    :rtype: Group
    """

    if not group_id:
        raise RuntimeError('Provide the group_id')

    if group_id:
        # get channels by the team id
        url = gs.build_url(mod_o365_endpoints.get('get_group_by_id').format(group_id=group_id))

    response = gs.con.get(url)

    if not response:
        return None

    data = response.json()

    return data

def get_group_site(gs, group_id = None, group_site = None):
    """ Returns Microsoft O365/AD group with given id
    :param group_id: group id of group
    :rtype: Group
    """

    if not group_id:
        raise RuntimeError('Provide the group_id')

    if group_id:
        # get channels by the team id
        url = gs.build_url(mod_o365_endpoints.get('get_group_site').format(group_id=group_id, site_name=group_site))

    response = gs.con.get(url)

    if not response:
        return None

    data = response.json()

    return data

def get_site_lists(gs, group_id = None, group_site = None):
    """ Returns Microsoft O365/AD group with given id
    :param group_id: group id of group
    :rtype: Group
    """

    if not group_id:
        raise RuntimeError('Provide the group_id')

    if group_id:
        # get channels by the team id
        url = gs.build_url(mod_o365_endpoints.get('get_site_lists').format(group_id=group_id, site_name=group_site))

    response = gs.con.get(url)

    if not response:
        return None

    data = response.json()

    return data

def get_list(gs, group_id = None, group_site = None, list_id= None):
    """ Returns Microsoft O365/AD group with given id
    :param group_id: group id of group
    :rtype: Group
    """

    if not group_id:
        raise RuntimeError('Provide the group_id')

    if not list_id:
        raise RuntimeError('Provide the group_id')
    
    if group_id and list_id:
        # get channels by the team id
        url = gs.build_url(mod_o365_endpoints.get('get_list').format(group_id=group_id, site_name=group_site, list_id=list_id))

    response = gs.con.get(url)

    if not response:
        return None

    data = response.json()

    return data


if module == "listGroups":

    res = GetParams("res")

    try:
        groups_list = list_groups(mod_o365_session[session].groups())

        SetVar(res, groups_list) 

    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "group":

    group_ = GetParams("groupId")
    res = GetParams("res")

    try:

        group = get_group_by_id(mod_o365_session[session].groups(), group_)

        SetVar(res, group)

    except Exception as e:
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "site":

    group_ = GetParams("groupId")
    res = GetParams("res")

    try:
        
        site = get_group_site(mod_o365_session[session].groups(), 
                              group_, 
                              get_group_by_id(mod_o365_session[session].groups(), group_)['displayName']
                              )

        SetVar(res, site)

    except Exception as e:
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "siteLists":

    group_ = GetParams("groupId")
    res = GetParams("res")

    try:
          
        sp_lists = get_site_lists(mod_o365_session[session].groups(), 
                              group_, 
                              get_group_by_id(mod_o365_session[session].groups(), group_)['displayName']
                              )

        SetVar(res, sp_lists)

    except Exception as e:
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "createList":
    
    site_ = GetParams("siteId") # site_id: a comma separated string of (host_name, site_collection_id, site_id)
    listInfo = GetParams("listInfo")
    res = GetParams("res")

    try:
        
        new_list = mod_o365_session[session].sharepoint().get_site(site_).create_list(eval(listInfo))
        
        SetVar(res, new_list)

    except Exception as e:
        SetVar(res, False)
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "listItems":
    
    site_ = GetParams("siteId") # site_id: a comma separated string of (host_name, site_collection_id, site_id)
    listName = GetParams("listName")
    res = GetParams("res")

    try:
        
        sp_list = mod_o365_session[session].sharepoint().get_site(site_).get_list_by_name(listName).get_items()
        
        items = []
        for item in sp_list:
            # I modified the return statement of the 'get_item_by_id' method to bring the whole data linked to the item
            data, item_ = mod_o365_session[session].sharepoint().get_site(site_).get_list_by_name(listName).get_item_by_id(item.object_id)
            items.append(data)
        
        
        
        SetVar(res, items)

    except Exception as e:
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "getItem":
    
    site_ = GetParams("siteId") # site_id: a comma separated string of (host_name, site_collection_id, site_id)
    listName = GetParams("listName")
    itemId = GetParams("itemId") 
    res = GetParams("res")
    
    try:
        
        data, item_ = mod_o365_session[session].sharepoint().get_site(site_).get_list_by_name(listName).get_item_by_id(itemId) 

        SetVar(res, data)

    except Exception as e:
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e
    
if module == "createItem":

    site_ = GetParams("siteId") # site_id: a comma separated string of (host_name, site_collection_id, site_id)
    listName = GetParams("listName")
    itemInfo = GetParams("newData")
    res = GetParams("res")

    try:

        new_item = mod_o365_session[session].sharepoint().get_site(site_).get_list_by_name(listName).create_list_item(eval(itemInfo))

        SetVar(res, True)
        
    except Exception as e:
        SetVar(res, False)
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "deleteItem":

    site_ = GetParams("siteId") # site_id: a comma separated string of (host_name, site_collection_id, site_id)
    listName = GetParams("listName")
    itemId = GetParams("itemId")
    res = GetParams("res")

    try:

        del_item = mod_o365_session[session].sharepoint().get_site(site_).get_list_by_name(listName).delete_list_item(itemId)

        SetVar(res, del_item)

    except Exception as e:
        SetVar(res, False)
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e

if module == "updateItem":

    site_ = GetParams("siteId") # site_id: a comma separated string of (host_name, site_collection_id, site_id)
    listName = GetParams("listName")
    itemId = GetParams("itemId")
    itemInfo = GetParams("newData")
    res = GetParams("res")

    try:

        data, item_ = mod_o365_session[session].sharepoint().get_site(site_).get_list_by_name(listName).get_item_by_id(itemId)
        item_.update_fields(eval(itemInfo))
        updated_item = item_.save_updates()
        
        SetVar(res, updated_item)

    except Exception as e:
        SetVar(res, False)
        print(traceback.format_exc())
        print("\x1B[" + "31;40mAn error occurred\x1B[" + "0m")
        PrintException()
        raise e