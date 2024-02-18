// The `Streamlit` object exists because our html file includes
// `streamlit-component-lib.js`.
// If you get an error about "Streamlit" not being defined, that
// means you're missing that file.
function onValueChanged(data) {
  console.log(`the data to be sent to streamlit server is `, data);
  Streamlit.setComponentValue(data);
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
let firstTime = true;
function onRender(event) {
  // Get the RenderData from the event
  const { call, args, subscribe, memo, replyTo, listen } = event.detail.args;
  if (call && (firstTime || (!memo && !subscribe))) {
    if (replyTo) {
      window.octostar
        .callReplyingTo(call, replyTo, ...(args || []))
        .then(onValueChanged);
    } else {
      window.octostar.call(call, ...(args || [])).then(onValueChanged);
    }
    firstTime = subscribe ? firstTime : false;
  }
  if (firstTime && subscribe) {
    window.octostar.subscribe(subscribe, onValueChanged);
    firstTime = false;
  }
  if (firstTime && listen) {
    window.octostar.listen(listen, onValueChanged);
    firstTime = false;
  }
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
// Render with the correct height
Streamlit.setFrameHeight(0);
