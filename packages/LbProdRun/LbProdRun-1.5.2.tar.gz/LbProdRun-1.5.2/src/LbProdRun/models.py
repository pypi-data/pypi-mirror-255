###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json
from pathlib import Path
from typing import Annotated, Any, Optional, Union

import typer
from pydantic import BaseModel as _BaseModel
from pydantic import Extra, Field, ValidationError, validator
from typer import colors as c


class BaseModel(_BaseModel, extra=Extra.forbid, validate_assignment=True):
    pass


class BaseApplication(BaseModel):
    name: str
    version: str
    event_timeout: Optional[float] = None
    number_of_processors: int = 1


class JobSpecV1(BaseModel):
    class ReleaseApplication(BaseApplication):
        data_pkgs: list[str] = []
        binary_tag: str = "best"
        nightly: Optional[str] = None

    class LbDevApplication(BaseApplication):
        project_base: Path
        binary_tag: str

    class FullDevApplication(BaseApplication):
        run_script: Path

    # It would be nice to use Discriminated Unions here to get better error
    # messages but that requires an new JobSpec version as there would need to
    # be a required ``Literal`` property on each ``BaseApplication`` subclass
    application: Union[ReleaseApplication, LbDevApplication, FullDevApplication]

    class LegacyOptions(BaseModel):
        command: Annotated[list[str], Field(min_length=1)] = []
        # FIXME: Ideally this should be annotated however there are too many buggy steps
        # files: Annotated[list[str], Field(min_length=1)]
        files: list[str]
        format: Optional[str] = None
        gaudi_extra_options: Optional[str] = None
        processing_pass: Optional[str] = None

        @validator("command", pre=True, always=True)
        def set_command(cls, command):  # noqa: B902  # pylint: disable=no-self-argument
            return command or ["gaudirun.py", "-T"]

    class LbExecOptions(BaseModel):
        entrypoint: str
        extra_options: dict[str, Any]
        extra_args: list[str] = []

    options: Union[LegacyOptions, LbExecOptions]

    class Input(BaseModel):
        files: Optional[list[str]] = None
        xml_summary_file: Optional[str] = None
        xml_file_catalog: Optional[str] = None
        run_number: Optional[int] = None
        tck: Optional[str] = None
        n_of_events: int = -1
        first_event_number: Optional[int] = None

    input: Input = Input()

    class Output(BaseModel):
        prefix: str
        types: list[str]
        histogram_file: Optional[str] = None
        compression: Optional[str] = None

    output: Output

    class DBTags(BaseModel):
        dddb_tag: Optional[str] = None
        conddb_tag: Optional[str] = None
        dq_tag: Optional[str] = None

    db_tags: DBTags = DBTags()


KNOWN_SPECS = {
    1: JobSpecV1,
}


def read_jobspec(spec_file: Path):
    try:
        data = json.loads(spec_file.read_text())
    except json.JSONDecodeError as e:
        typer.secho(f"Failed to parse {spec_file} as JSON with error {e}", fg=c.RED)
        raise typer.Exit(101) from e

    try:
        spec_version = data.pop("spec_version")
    except KeyError as e:
        typer.secho(f"'spec_version' is not specified in {spec_file}", fg=c.RED)
        raise typer.Exit(101) from e

    try:
        JobSpecClass = KNOWN_SPECS[spec_version]
    except KeyError as e:
        typer.secho(f"Unknown spec_version {spec_version!r}", fg=c.RED)
        raise typer.Exit(101) from e

    try:
        return JobSpecClass.parse_obj(data)
    except ValidationError as e:
        errors = e.errors()
        typer.secho(
            f"Found {len(errors)} error{'s' if len(errors) > 1 else ''} "
            f"when validating {spec_file}:",
            fg=c.RED,
        )
        for error in e.errors():
            if error["type"] == "value_error.missing":
                message = f"Field {'.'.join(map(str, error['loc']))!r} is required"
            else:
                message = f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
            typer.secho(f"  * {message}", fg=c.RED)
        raise typer.Exit(101) from e
