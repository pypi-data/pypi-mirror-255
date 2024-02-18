from streamlit_octostar_research.configure import octostar_component_func as _component_func
from streamlit_octostar_research.support import require

def cancel_queries(context): 
    component_value = _component_func(
        call='octostar:ontology:cancelQueries',
        args=[context]
    )
    return component_value
def get_available_ontologies(): 
    component_value = _component_func(
        call='octostar:ontology:getAvailableOntologies',
        args=[]
    )
    return component_value

def get_concept_by_name(conceptName): 
    component_value = _component_func(
        call='octostar:ontology:getConceptByName',
        args=[conceptName]
    )
    return component_value
def get_concepts(): 
    component_value = _component_func(
        call='octostar:ontology:getConcepts',
        args=[]
    )
    return component_value
def get_entity_by_id(e):
    component_value = _component_func(
        call='octostar:ontology:getEntityByID',
        args=[e]
    )
    return component_value
def get_ontology_name(): 
    component_value = _component_func(
        call='octostar:ontology:getOntologyName',
        args=[]
    )
    return component_value

def get_relationship_count(entity, rel): 
    component_value = _component_func(
        call='octostar:ontology:getRelationshipCount',
        args=[entity, rel]
    )
    return component_value

def get_relationships_for_entity(entity): 
    component_value = _component_func(
        call='octostar:ontology:getRelationshipsForEntity',
        args=[entity]
    )
    return component_value

@require("key")
def send_query(query, options=None, **kwargs):
    component_value = _component_func(
        call='octostar:ontology:sendQuery',
        replyTo=kwargs["key"],
        args=[query,options]
    )
    return component_value

@require("key")
def send_query_t(query, options=None, **kwargs):
    component_value = _component_func(
        call='octostar:ontology:sendQueryT',
        replyTo=kwargs["key"],
        args=[query,options]
    )
    return component_value

def get_sys_inheritance(): 
    component_value = _component_func(
        call='octostar:ontology:getSysInheritance',
    )
    return component_value


