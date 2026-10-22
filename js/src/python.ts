// Python that runs in Pyodide and calls RenderCV's Python API (`rendercv.api`).
//
// The JavaScript side writes a project's files into `project_folder`, then
// calls `render_project` or `validate_project`. Results are plain dictionaries
// and lists, so they convert to JavaScript objects and arrays.
export const glue = String.raw`
import dataclasses
import pathlib
import shutil

from rendercv.api import problems_from_error, render, validate
from rendercv.exception import RenderCVUserError, RenderCVUserValidationError

project_folder = pathlib.Path("/home/pyodide/rendercv-project")
input_file_name = "cv.yaml"


def reset_project_folder():
    shutil.rmtree(project_folder, ignore_errors=True)
    project_folder.mkdir(parents=True)
    return str(project_folder)


def problems_as_dictionaries(problems):
    return [
        {
            "message": problem.message,
            "source": problem.source,
            "path": list(problem.path),
            "line": problem.line,
            "column": problem.column,
            "endLine": problem.end_line,
            "endColumn": problem.end_column,
        }
        for problem in problems
    ]


def render_project(formats, overrides):
    try:
        cv = render(
            project_folder / input_file_name,
            formats=list(formats),
            overrides=dict(overrides) or None,
        )
    except (RenderCVUserError, RenderCVUserValidationError) as e:
        return {"problems": problems_as_dictionaries(problems_from_error(e))}
    outputs = {
        output_format: list(output) if isinstance(output, tuple) else output
        for output_format, output in dataclasses.asdict(cv).items()
        if output is not None
    }
    return {"outputs": outputs}


def validate_project(overrides):
    problems = validate(
        project_folder / input_file_name, overrides=dict(overrides) or None
    )
    return problems_as_dictionaries(problems)

`;
