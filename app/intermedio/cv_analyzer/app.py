"""Streamlit entry point for CV Analyzer."""

import logging

from ui.streamlit_ui import main


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


if __name__ == "__main__":
    main()

