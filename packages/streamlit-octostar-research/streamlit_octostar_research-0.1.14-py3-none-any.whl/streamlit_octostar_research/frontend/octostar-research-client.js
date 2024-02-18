const os = window.octostar;
const DESKTOP_PREFIX = "octostar:desktop:";
const ONTOLOGY_PREFIX = "octostar:ontology:";
export const OctostarClient = {
  desktop: {
    openWorkspace(ws) {
      return os.call("".concat(DESKTOP_PREFIX, "openWorkspace"), ws);
    },
    closeWorkspace(ws) {
      return os.call("".concat(DESKTOP_PREFIX, "closeWorkspace"), ws);
    },
    listAllWorkspaces() {
      return os.call("".concat(DESKTOP_PREFIX, "listAllWorkspaces"));
    },
    getWorkspace(ws) {
      return os.call("".concat(DESKTOP_PREFIX, "getWorkspace"), ws);
    },
    getItem(ws) {
      return os.call("".concat(DESKTOP_PREFIX, "getItem"), ws);
    },
    getItems(ws) {
      return os.call("".concat(DESKTOP_PREFIX, "getItems"), ws);
    },
    createWorkspace(name) {
      return os.call("".concat(DESKTOP_PREFIX, "createWorkspace"), name);
    },
    save(item) {
      return os.call("".concat(DESKTOP_PREFIX, "save"), item);
    },
    opeen(item) {
      return os.call("".concat(DESKTOP_PREFIX, "open"), item);
    },
    searchXperience() {
      return os.call("".concat(DESKTOP_PREFIX, "searchXperience"));
    },
    showTab(props) {
      return os.call("".concat(DESKTOP_PREFIX, "showTab"), props);
    },
    showNotification(notification) {
      return os.call(
        "".concat(DESKTOP_PREFIX, "showNotification"),
        notification
      );
    },

    showConfirm(props) {
      return os.call("".concat(DESKTOP_PREFIX, "showConfirm"), props);
    },
    getOpenWorkspaceIds() {
      return os.call("".concat(DESKTOP_PREFIX, "getOpenWorkspaceIds"));
    },
    setOpenWorkspaceIds(ids) {
      return os.call("".concat(DESKTOP_PREFIX, "setOpenWorkspaceIds"), ids);
    },
    onOpenWorkspaceIdsChanged(callback) {
      return os.subscribe(
        "".concat(DESKTOP_PREFIX, "onOpenWorkspaceIdsChanged"),
        callback
      );
    },

    onWorkspaceChanged(ws, callback) {
      return os.subscribe(
        "".concat(DESKTOP_PREFIX, "onWorkspaceChanged"),
        callback,
        ws
      );
    },
    onWorkspaceItemChanged(item, callback) {
      return os.subscribe(
        "".concat(DESKTOP_PREFIX, "onWorkspaceItemChanged"),
        callback,
        item
      );
    },

    onOpenWorkspacesChanged(callback) {
      return os.subscribe(
        "".concat(DESKTOP_PREFIX, "onOpenWorkspacesChanged"),
        callback
      );
    },
  },

  ontology: {
    cancelQueries(context) {
      return os.call("".concat(ONTOLOGY_PREFIX, "cancelQueries"), context);
    },
    getAvailableOntologies() {
      return os.call("".concat(ONTOLOGY_PREFIX, "getAvailableOntologies"));
    },
    getAllConnectedEntities(entity, relationship) {
      return os.call(
        "".concat(ONTOLOGY_PREFIX, "getAllConnectedEntities"),
        entity,
        relationship
      );
    },
    getConceptByName(conceptName) {
      return os.call(
        "".concat(ONTOLOGY_PREFIX, "getConceptByName"),
        conceptName
      );
    },

    getConcepts() {
      return os.call("".concat(ONTOLOGY_PREFIX, "getConcepts"));
    },
    getEntityByID(entity) {
      return os.call("".concat(ONTOLOGY_PREFIX, "getEntityByID"), entity);
    },
    getOntologyName() {
      return os.call("".concat(ONTOLOGY_PREFIX, "getOntologyName"));
    },
    getRelationshipCount(entity, rel) {
      return os.call(
        "".concat(ONTOLOGY_PREFIX, "getRelationshipCount"),
        entity,
        rel
      );
    },
    getRelationshipsForEntity(entity) {
      return os.call(
        "".concat(ONTOLOGY_PREFIX, "getRelationshipsForEntity"),
        entity
      );
    },

    sendQuery(query, options) {
      return os.call("".concat(ONTOLOGY_PREFIX, "sendQuery"), query, options);
    },
    sendQueryT(query, options) {
      return os.call("".concat(ONTOLOGY_PREFIX, "sendQueryT"), query, options);
    },
    getSysInheritance() {
      return os.call("".concat(ONTOLOGY_PREFIX, "getSysInheritance"));
    },
  },
};
