from blacksheep.server.openapi.common import EndpointDocs, ParameterInfo

from ..model import SequenceProfile

__tags = ["Sequence"]

"""
Note: When referring to sequences within the system, these serve as a means to store information for a line chart in 
the database. These data can take various forms such as pd.Dataframe, sh.Dataset, np.Arrays, Lists, etc. 
The objective is to transform these diverse data types into Arrow format and store them in files. Presently, these 
files are saved in the ".shapelets/data" directory. Additionally, it is important to note that these sequences are 
associated with a dataApp. Consequently, when a dataApp is removed, the corresponding files are also deleted.
"""

create_sequence = EndpointDocs(
    summary="Create Sequence",
    description="Save a Sequence in the system.",
    tags=__tags,
    parameters={"seq": ParameterInfo("Sequence details.", SequenceProfile)}
)

get_sequence = EndpointDocs(
    summary="Get Sequence",
    description="Retrieve sequence details.",
    tags=__tags
)

levels_blocks = EndpointDocs(
    summary="Levels And Blocks",
    description=
    """
    Retrieve the visualization information of a sequence, including the number of levels and chunk size. 
    This information is essential for the UI to comprehend how to utilize levels and blocks. 
    The "number of levels" is represented as a list, with each sublist indicating the count of elements per block for a 
    specific level. For example: [[800, 800, 800, 800], [800, 800, 800], [800, 800], [800]].
    """,
    tags=__tags
)

visualization = EndpointDocs(
    summary="Get Visualization Info",
    description=
    """
    Retrieve the specified levels and blocks in Arrow Batch format, serialized for efficient transmission. 
    The UI determines the required levels and blocks, including them in the request for processing.
    """,
    tags=__tags
)

generate_levels = EndpointDocs(
    summary="Generate Levels",
    description=
    """
    Upon saving a sequence, the background process initiates the generation of levels and blocks for that specific 
    sequence. The Visvalingam Algorithm is employed to calculate the most representative points for each block within 
    the levels. Upon completion of the algorithm, the resulting information is stored in an Arrow Batch.
    """,
    tags=__tags,
    parameters={"sequence_id": ParameterInfo("Sequence ID.", str)}
)

__all__ = ['create_sequence', 'get_sequence', 'levels_blocks', 'generate_levels']
