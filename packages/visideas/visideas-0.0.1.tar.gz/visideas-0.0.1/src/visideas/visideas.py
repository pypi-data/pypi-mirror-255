# visualize by groups
import csv
import uuid
import click
import json
import tabulate
from pathlib import Path
from typing import Optional, Union
from enum import Enum
# from pprint import pprint

# Often your labels will look something like:
# [
#     "Index",
#     "Idea Name",
#     "Idea Description",
#     "Compound Score",
#     "Rohan Score",
#     "Venkat Score",
#     "Adriano Score",
#     "Ideator",
#     "Our problem?",
#     "Idea State",
#     "Latest Non-Closed Idea State Reached",
#     "Idea Group",
#     "Comments and/or Postmortem",
#     "Next Steps",
#     "Opened Date",
#     "Closed Date",
#     "Idea Survival Duration",
#     "Ideas Open Right Now",
# ]
# (though it's OK to vary so long as the names "Idea Name", "Idea Description", "Idea Group", and "Idea State" are present AND
# "Idea Description" is NEVER empty; though ideally Idea Name is not empty.)
#
# And it will be the case that
# 1. Scores are numeric
# 2. Idea State is one of
# [
#    "Unopened",
#    "Open",
#    "Private Open",
#    "Coasted,"
#    "Closed",
# ]
# (and if it is empty it is assumed to be Unopened)

class Format(Enum):
    JSON = 'json'
    TREE = 'tree'
    TABLE = 'table'

@click.command()
@click.argument('input_file', type=str, required=True)
@click.option('--save-to', default=None, help='Save to file')
@click.option('--format', default=Format.JSON, help=f'Format to save to; must be one of {[x.value for x in Format]}')
@click.option('--skip-subsequent-count', default=1, help='Skip subsequent rows by this count after the first row. Your first row must always be labels and these rows might be informational.')
@click.option("--disable-strict-name", is_flag=True, help="Disable strict name checking, if you toggle this then you may have ideas without names so long as they have a desc.")
def main(input_file: str, save_to: Optional[str], format: Union[Format, str], skip_subsequent_count: int, disable_strict_name: bool = False) -> None:
    """Visualize the idea spreadsheet that you are using for your startup ideation. This was created by Adriano for himself, Rohan, and Venkat
    at Meru Production in 2024 during a pivot. It is NOT guaranteed to be maintained.
    """

    # Verify the parameters
    enforce_must_have_name = not disable_strict_name
    input_file = Path(input_file).expanduser().resolve()
    if not input_file.exists():
        raise ValueError(f"File {input_file.as_posix()} does not exist")
    if input_file.suffix != ".csv":
        raise ValueError(f"File {input_file.as_posix()} is not a CSV file")
    save_to = Path(save_to).expanduser().resolve() if save_to is not None else None
    if save_to is not None and save_to.exists():
        raise ValueError(f"File {save_to.as_posix()} already exists")
    format = Format(format)

    # Collect the ideas info into a simple dictionary grouping
    ideas_info = {}
    with open(input_file, "r") as f:
        reader = csv.reader(f)
        # Always skip first row to use as labels
        first_iteration: bool = True
        # Skip subsequent rows because we have informational boxes
        index2label = {}
        label2index = {}
        for xi, x in enumerate(reader):
            if first_iteration:
                first_iteration = False
                assert isinstance(x, list) and all(isinstance(xx, str) for xx in x)
                for i, label in enumerate(x):
                    label2index[label] = i
                    index2label[i] = label
            elif xi > skip_subsequent_count:
                assert (
                    label2index is not None
                    and len(index2label) == len(label2index)
                    and len(index2label) > 0
                )
                idea_idx = label2index['Idea Name']
                idea_desc_idx = label2index['Idea Description']
                group_idx = label2index['Idea Group']
                state_idx = label2index['Idea State']

                idea = x[idea_idx]
                if len(idea) == 0:
                    if enforce_must_have_name:
                        raise ValueError(f"Row {xi} has no idea name, but you are not disabling strict name enforcement. You should NAME all of your ideas!")
                    idea = x[idea_desc_idx][:20] + "_" + str(uuid.uuid4())
                assert len(idea) > 0

                group = x[group_idx]
                if len(group) == 0:
                    group = None
                assert group is None or len(group) > 0

                state = x[state_idx]
                if len(state) == 0:
                    state = 'Unopened'
                assert len(state) > 0

                if group not in ideas_info:
                    ideas_info[group] = []
                ideas_info[group].append(f'({state}){idea}')
    assert 'Misc' not in ideas_info
    ideas_info['Misc'] = ideas_info[None]
    del ideas_info[None]
    ideas_info = {k : sorted(vs) for k, vs in ideas_info.items()}
    printout = None
    if format == Format.JSON:
        printout = json.dumps(ideas_info, indent=4)
    elif format == Format.TREE:
        raise NotImplementedError("Tree visualization is still under design.")
    elif format == Format.TABLE:
        table_length = max(len(vs) for vs in ideas_info.values())
        table = [[k for k in sorted(ideas_info.keys())]]
        for i in range(table_length):
            row = []
            for k in table[0]:
                v = '' if i >= len(ideas_info[k]) else ideas_info[k][i]
                row.append(v)
            assert len(row) == len(table[0])
            table.append(row)
        printout = tabulate.tabulate(table, headers='firstrow')
    assert printout is not None
    if save_to is not None:
        with open(save_to, "w") as f:
            f.write(printout)
    else:
        print(printout)

if __name__ == "__main__":
    main()
