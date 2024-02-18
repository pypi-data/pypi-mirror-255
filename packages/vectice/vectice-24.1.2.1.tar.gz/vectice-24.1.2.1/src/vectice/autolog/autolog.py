# This captures the code called, we then use regex to identify the variables in locals. The variables found can then be logged to vectice.
"""Auto-Logging assets with Vectice.

NOTE: **IMPORTANT INFORMATION**
    Autolog is currently in Beta, and we are actively enhancing supported libraries, environments, and functionalities to provide an improved user experience.

    Your feedback is highly valued. Please send any feedback to support@vectice.com.

------------
The enhanced auto-logging feature in Vectice allows for seamless documentation and management of your data science projects. Please note the following details about this beta feature.

NOTE: **This feature is designed to work specifically with notebooks.**

1.** Installation:**
    To enable the auto-logging feature, install the additional dependencies using the following command:

    ```bash
    pip install vectice[autolog]
    ```

2.** Supported libraries and environment:**
    Vectice automatically identifies and log assets encapsulated within a specified list of supported libraries and environement mentioned below

NOTE: **Supported libraries and environment**
    - Dataframe: Pandas, Spark.
    - Model: Scikit, Xgboost, Lightgbm, Catboost, Keras.
    - Graphs: Matplotlib, Seaborn, Plotly.
    - Environments: Colab, Jupyter, Vertex, SageMaker, Databricks and VScode notebook.

3.** General behavior:**
    Vectice autolog provides three methods: autolog.config, autolog.notebook, and autolog.cell. These methods are designed to log every asset to Vectice existing as a variable in the notebook's memory. It is important to review the specific behaviors outlined in the documentation for each of these three methods.

NOTE: **IMPORTANT INFORMATION**
    - For GRAPHS, ensure they are saved as files to be automatically logged in the iteration i.e:
        - plt.savefig("my figure.png") (for seaborn or matploltlib)
        - fig.write_image("my figure.png") (for plotly)
    - For METRICS, Vectice currently recognizes sklearn metrics for automatic association with models.
        - In cases there's ambiguity due to multiple models with different metrics, Vectice won't automatically link them. To establish the link, make sure each model and its respective metrics are placed within the same notebook cell.

"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell

    from vectice.models import Phase


class Login(TypedDict):
    phase: Phase | None


LOGIN: Login = {"phase": None}


_logger = logging.getLogger(__name__)


# Setup vectice connection on phass
def config(api_token: str, phase: str, host: str | None = None) -> None:
    """Configures the autolog functionality within Vectice.

    The `config` method allows you to establish a connection to Vectice and specify the phase in which you want to autolog your work.

    ```python
    # Configure autolog
    from vectice import autolog
    autolog.config(
        api_token = 'your-api-key', # Paste your api key
        phase = 'PHA-XXX'           # Paste your Phase Id
    )
    ```

    Parameters:
            api_token: The api token provided inside your Vectice app (API key).
            phase: The ID of the phase in which you wish to autolog your work as an iteration.
            host: The backend host to which the client will connect. If not found, the default endpoint https://app.vectice.com is used.

    """
    from vectice import Connection
    from vectice.connection import DEFAULT_HOST

    host = host or DEFAULT_HOST
    vec = Connection(api_token=api_token, host=host)
    client = vec._client  # pyright: ignore[reportPrivateUsage]
    client.assert_feature_flag_or_raise("autolog")
    asset = client.get_user_and_default_workspace()
    user_name = asset["user"]["name"]
    _logger.info(f"Welcome, {user_name}. You`re now successfully connected to Vectice.")
    LOGIN["phase"] = vec.phase(phase)
    _logger.warning(
        "\nAutolog is currently in Beta, and we are actively enhancing supported libraries, environments, and functionalities to provide an improved user experience."
        "\nFor detailed information, supported libraries and environments please consult the documentation: https://api-docs.vectice.com/reference/vectice/autolog/"
    )
    from vectice.autolog.autolog_class import start_listen

    start_listen()


# Log the whole notebook inside Vectice iteration
def notebook(note: str | None = None) -> None:
    """Automatically log all supported models, dataframes, and graphs from your notebook within the Vectice App as assets.

    NOTE: **IMPORTANT INFORMATION**
        Autolog must be configured at the beginning of your notebook to capture all relevant information. Cells executed prior to configuring autolog may not have their assets recorded by the autolog.notebook() method and may need to be run again.

    ```python
                                   ...
    #Add this command at the end of notebook to log all the assets in memory
    autolog.notebook()
    ```

    NOTE: **Ensure that the required assets are in memory before calling this method.**

    Parameters:
        note: the note or comment to log to your iteration associated with the autolog.notebook
    """
    from vectice.autolog.autolog_class import Autolog

    # TODO add notebook parsing of content
    Autolog(LOGIN["phase"], _check_if_notebook(), True, True, note)


def cell(create_new_iteration: bool = False, note: str | None = None):
    """Automatically logs all supported models, dataframes, and graphs from a specific notebook cell within the Vectice platform.

    This method facilitates the selective logging of assets within a particular notebook cell, allowing users to precisely choose the assets to log to Vectice with an optional control to log assets inside a new iteration.

    NOTE: **Ensure that you have configured the autolog with your Vectice API token and the relevant phase ID before using this method.**

    ```python
                                   ...
    #Add this command at the end of the desired cell to log all the cells assets
    autolog.cell()
    ```

    NOTE: **Place the command at the end of the desired cell to log all assets within that cell.**

    Parameters:
        create_new_iteration: If set to False, logging of assets will happen in the last updated iteration. Otherwise, it will create a new iteration for logging the cell's assets.
        note: the note or comment to log to your iteration associated with the autolog.cell

    """
    from vectice.autolog.autolog_class import Autolog

    Autolog(LOGIN["phase"], _check_if_notebook(), False, create_new_iteration, note)


def _check_if_notebook() -> InteractiveShell:
    from IPython.core.getipython import get_ipython

    ipython = get_ipython()

    if ipython is None:
        raise ValueError("Not a notebook.")
    return ipython
