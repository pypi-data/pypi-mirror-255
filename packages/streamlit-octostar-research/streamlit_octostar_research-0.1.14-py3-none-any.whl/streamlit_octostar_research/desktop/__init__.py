from streamlit_octostar_research.configure import octostar_component_func as _component_func
from streamlit_octostar_research.support import require

def get_current_workspace_id(): 
    component_value = _component_func(
        call='octostar:remoteapp:getCurrentWorkspaceId',
        memo=True,
        args=[]
    )
    return component_value

def open_workspace(ws): 
    component_value = _component_func(
        call='octostar:desktop:openWorkspace',
        args=[ws]
    )
    return component_value

def close_workspace(ws): 
    component_value = _component_func(
        call='octostar:desktop:closeWorkspace',
        args=[ws]
    )
    return component_value

def list_all_workspaces(): 
    component_value = _component_func(
        call='octostar:desktop:listAllWorkspaces',
        args=[]
    )
    return component_value

def get_workspace(ws): 
    component_value = _component_func(
        call='octostar:desktop:getWorkspace',
        args=[ws]
    )
    return component_value

def get_item(ws): 
    component_value = _component_func(
        call='octostar:desktop:getItem',
        args=[ws]
    )
    return component_value

def open(ws): 
    component_value = _component_func(
        call='octostar:desktop:open',
        memo=True,
        args=[ws]
    )
    return component_value

def get_items(ws): 
    component_value = _component_func(
        call='octostar:desktop:getItems',
        args=[ws]
    )
    return component_value

def create_workspace(name): 
    component_value = _component_func(
        call='octostar:desktop:createWorkspace',
        args=[name]
    )
    return component_value

@require('key')
def searchXperience(**kwargs): 
    component_value = _component_func(
        call='octostar:desktop:searchXperience',
        replyTo=kwargs['key'],
        args=[]
    )
    return component_value

@require('key')
def result(**kwargs):
    component_value = _component_func(
        listen=kwargs['key']
    )
    return component_value

def show_tab(props): 
    component_value = _component_func(
        call='octostar:desktop:showTab',
        args=[props]
    )
    return component_value

def show_notification(notification): 
    component_value = _component_func(
        call='octostar:desktop:showNotification',
        args=[notification]
    )
    return component_value

def show_confirm(props): 
    component_value = _component_func(
        call='octostar:desktop:showConfirm',
        args=[props]
    )
    return component_value

def on_workspace_changed(ws): 
    component_value = _component_func(
        subscribe='octostar:desktop:onWorkspaceChanged',
        args=[ws]
    )
    return component_value

def on_open_workspaces_changed(): 
    component_value = _component_func(
        subscribe='octostar:desktop:onOpenWorkspacesChanged',
        args=[]
    )
    return component_value

def on_workspace_item_changed(item): 
    component_value = _component_func(
        subscribe='octostar:desktop:onWorkspaceItemChanged',
        args=[item]
    )
    return component_value

def get_open_workspace_ids(): 
    component_value = _component_func(
        call='octostar:desktop:getOpenWorkspaceIds',
        subscribe='octostar:desktop:onOpenWorkspaceIdsChanged',
        args=[]
    )
    return component_value

def on_open_workspace_ids_changed(): 
    component_value = _component_func(
        subscribe='octostar:desktop:onOpenWorkspaceIdsChanged',
        args=[]
    )
    return component_value

def set_open_workspace_ids(ids): 
    component_value = _component_func(
        call='octostar:desktop:setOpenWorkspaceIds',
        args=[ids]
    )
    return component_value

def get_context(): 
    component_value = _component_func(
        subscribe='octostar:remoteapp:context',
        args=[]
    )
    return component_value

@require('key')
@require('record')
def get_paste_context(**kwargs): 
    component_value = _component_func(
        call='octostar:desktop:getPasteContext',
        replyTo=kwargs['key'],
        args=[{
            "record": kwargs['record'],
            "limit1": kwargs['limit1'] if 'limit1' in kwargs else None,
            "limit2": kwargs['limit2'] if 'limit2' in kwargs else None,
        }]
    )
    return component_value


def call_app_service(service, options=None, **kwargs):
    """
    Call a service on a remote app.
    If a reply is expected, the key must be provided in the options.
    """
    component_value = _component_func(
        call='octostar:desktop:callAppService',
        args=[{"service": service, "options": options, "context": kwargs}],
        replyTo=options["key"] if options and "key" in options else "/dev/null"
    )
    return component_value
