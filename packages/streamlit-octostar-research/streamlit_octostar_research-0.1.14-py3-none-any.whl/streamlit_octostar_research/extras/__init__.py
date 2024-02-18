from streamlit_octostar_research.configure import octostar_component_func as _component_func
from streamlit_octostar_research.support import require

@require("key")
@require("path")
@require("name")
@require("nodes")
def create_link_chart(key=None,path=None,name=None,nodes=None,edges=None,draft=True,os_workspace=None):
    component_value = _component_func(
        call='octostar:desktop:extras:createLinkChart',
        replyTo=key,
        args=[{"path": path, "name": name, "nodes": nodes, "edges": edges, "draft": draft, "os_workspace": os_workspace}]
    )
    return component_value

def set_transform_result(result): 
    component_value = _component_func(
        call='octostar:remoteapp:setTransformResult',
        args=[result]
    )
    return component_value
