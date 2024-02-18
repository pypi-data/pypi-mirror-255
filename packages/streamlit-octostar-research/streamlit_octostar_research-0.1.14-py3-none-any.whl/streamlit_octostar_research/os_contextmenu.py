import streamlit.components.v1 as components
import json

def os_contextmenu(item,label=None,height=30,padding="6px"):
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OsContextMenu</title>
    <script>
    const CONTEXT_MENU_REQUEST = "octostar:desktop:showContextMenu";
    const item = {json.dumps(item)};
    </script>

<style>
    body {{
        padding: 0;
        margin: 0;
    }}

    .context-menu {{
        cursor: pointer;
        width: 100%;
        padding: {padding};
    }}

    .context-menu:hover {{
        background-color: #f5f5f5; /* Slight grey background on hover */
    }}
</style>

</head>
<body>
    
    <div id="osContextMenu" class="context-menu" draggable="true">
        {label if label else item['entity_label'] if 'entity_label' in item else 'missing label'}
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {{
            const el = document.getElementById('osContextMenu');
            const trigger = ['hover', 'contextMenu']; // Adjust triggers as needed

            el.addEventListener('mouseenter', function (event) {{
                if (trigger.includes('hover')) {{
                    handleMouseEvent(event);
                }}
            }});

            el.addEventListener('contextmenu', function (event) {{
                if (trigger.includes('contextMenu')) {{
                    handleMouseEvent(event);
                }}
            }});

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

            function handleMouseEvent(event) {{
                event.preventDefault();

                const request = adjustCoordinatesForIframe(window, {{
                    x: event.clientX,
                    y: el.getBoundingClientRect().y,
                    item
                }});


                window.parent.octostar.call(CONTEXT_MENU_REQUEST, request);
            }}
        }});
    </script>
</body>
</html>
    """
    components.html(html, height=height)
