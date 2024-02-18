import streamlit.components.v1 as components
import uuid
from pathlib import Path

def os_dropzone(key=None, label="Drop records from sidebar here or click to search"):
    if key is None:
        key = str(uuid.uuid4())
    frontend_dir = (Path(__file__).parent / "frontend").absolute()
    component_js_path = frontend_dir / 'streamlit-component-lib.js'

    with open(component_js_path, 'r', encoding='utf-8') as file:
        component_js_ = file.read()
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Drag and Drop Component</title>
        <script>
{component_js_}
        </script>

   <style>
        .antd-uploader {{
            border: 1px dashed #d9d9d9;
            border-radius: 4px;
            text-align: center;
            background-color: #fafafa;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }}

        .antd-uploader:hover {{
            border-color: #40a9ff;
        }}

        .upload-icon {{
            color: #40a9ff;
            font-size: 30px;
            margin-bottom: 8px;
        }}

        .upload-text {{
            display: block;
            color: rgba(0, 0, 0, 0.45);
            font-size: 18px;
            margin-bottom: 16px;
        }}
    </style>    </head>
    <body>
            <div id="osDropZone" class="antd-uploader">
        <div class="upload-icon">+</div>
        <span class="upload-text">{label}</span>
    </div>

    <script>

        document.addEventListener('DOMContentLoaded', function () {{
            const el = document.getElementById('osDropZone');
            let visible = false;
            function debounce(func, wait) {{
                let timeout;
                return function() {{
                    const context = this, args = arguments;
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(context, args), wait);
                }};
            }}

            const updateHandler = () => {{
                const rect = el.getBoundingClientRect();
                const newVisible = rect.width !== 0 && rect.height !== 0;
                if (true ||  newVisible || newVisible !== visible) {{
                    visible = newVisible;
                    publishDropZone();
                }}
            }};

            const debouncedUpdateHandler = debounce(updateHandler, 200); // Adjust the debounce time as needed

            const observer = new ResizeObserver(entries => {{
                for (let entry of entries) {{
                    debouncedUpdateHandler();
                }}
            }});

            observer.observe(el);
            observer.observe(document.body, {{childList: true, subtree: true, attributes: true }});

            window.addEventListener('scroll', debouncedUpdateHandler, true);


            function adjustCoordinatesForIframe(windowObj, coords) {{
                if (windowObj.parent === windowObj || !windowObj.frameElement) {{
                    return coords; // Base case: top-level window reached or no frameElement found
                }}

                const rect = windowObj.frameElement.getBoundingClientRect();
                // Recursive call with parent window and adjusted coordinates
                return adjustCoordinatesForIframe(windowObj.parent, {{
                    ...coords,
                    x: coords.x + rect.left,
                    y: coords.y + rect.top
                }});
            }}

            const onDropTopic = "{key}";
            function publishDropZone() {{
                console.log("publishDropZone")
                const rect = el.getBoundingClientRect();
                const request = adjustCoordinatesForIframe(window, {{
                    id: "{key}",
                    x: rect.left,
                    y: rect.top,
                    width: rect.width,
                    height: rect.height,
                    onDropTopic,
                }});

                const DROP_ZONE_REQUEST = "octostar:remoteapp:dropZoneRequest";
                window.parent.octostar.call(DROP_ZONE_REQUEST, request);
            }}
            const DRAG_START_TOPIC = "octostar:remoteapp:onDragStart";
            window.parent.octostar.subscribe(DRAG_START_TOPIC, publishDropZone);
            window.parent.octostar.on(onDropTopic, (data) => {{
                console.log("onDropTopic", data);
                  Streamlit.setComponentValue(data);
            }})
            el.onclick = ()=> window.parent.octostar.callReplyingTo(
                    'octostar:desktop:searchXperience', onDropTopic, 
                    []);

        }});
    </script>
    </body>
    </html>
    """
    components.html(html, height=100)
