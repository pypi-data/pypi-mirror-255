from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

# Tell streamlit that there is a component called streamlit_octostar_research,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
octostar_component_func = components.declare_component(
	"streamlit_octostar_research", path=str(frontend_dir)
)