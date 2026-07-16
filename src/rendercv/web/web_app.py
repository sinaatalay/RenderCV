import io
import json
import pathlib
import tempfile
import traceback
import urllib.parse

import ruamel.yaml
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
from rendercv.renderer.pdf_png import generate_pdf
from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_dictionary,
    build_rendercv_model_from_commented_map,
)
from rendercv.schema.sample_generator import create_sample_yaml_input_file

app = FastAPI(title="RenderCV Web Editor", description="Live YAML Editor & PDF Generator for RenderCV")

static_dir = pathlib.Path(__file__).parent / "static"

class RenderRequest(BaseModel):
    yaml: str
    hide_sections: list[str] = []

class SwitchThemeRequest(BaseModel):
    yaml: str
    theme: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the single-page application frontend."""
    index_file = static_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/api/templates")
def get_templates() -> list[str]:
    """Get the list of available built-in RenderCV themes."""
    return available_themes

@app.get("/api/templates/{theme_name}")
def get_template(theme_name: str) -> dict[str, str]:
    """Get the example YAML string for a specific theme."""
    if theme_name not in available_themes:
        raise HTTPException(
            status_code=404,
            detail=f"Theme {theme_name} not found. Available themes: {', '.join(available_themes)}"
        )
    try:
        yaml_content = create_sample_yaml_input_file(file_path=None, name="John Doe", theme=theme_name)
        return {"yaml": yaml_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/api/switch_theme")
def switch_theme(request: SwitchThemeRequest):
    """Merge the 'cv' section from the user's current YAML into the target theme's template."""
    if request.theme not in available_themes:
        raise HTTPException(status_code=404, detail="Theme not found.")
        
    try:
        ryaml = ruamel.yaml.YAML()
        ryaml.preserve_quotes = True
        ryaml.indent(mapping=2, sequence=4, offset=2)
        
        # Load user's current YAML
        try:
            current_data = ryaml.load(request.yaml)
        except Exception as e:
            err_msg = f"Invalid YAML format in editor: {e!s}"
            raise ValueError(err_msg) from e
            
        if not isinstance(current_data, dict):
            err_msg = "YAML must represent a mapping/dictionary structure."
            raise ValueError(err_msg)
            
        # Generate the new theme template
        new_theme_yaml = create_sample_yaml_input_file(file_path=None, name="John Doe", theme=request.theme)
        new_data = ryaml.load(new_theme_yaml)
        
        # Merge the CV data
        if current_data.get("cv"):
            new_data["cv"] = current_data["cv"]
            
        # Dump back to YAML string
        with io.StringIO() as stream:
            ryaml.dump(new_data, stream)
            merged_yaml = stream.getvalue()
            
        return {"yaml": merged_yaml}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/render")
def render_pdf(request: RenderRequest):
    """Compile the provided YAML to a PDF and return the PDF file bytes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        try:
            # Parse YAML into CommentedMap first to modify the dictionary
            input_dict, overlay_sources = build_rendercv_dictionary(
                request.yaml,
                output_folder=tmp_path,
                dont_generate_png=True,
                dont_generate_markdown=True,
                dont_generate_html=True,
            )
            
            # Extract all sections that were in the YAML originally
            all_sections = []
            if "cv" in input_dict and "sections" in input_dict["cv"] and input_dict["cv"]["sections"]:
                all_sections = list(input_dict["cv"]["sections"].keys())
                
            # Programmatically remove hidden sections from the dictionary
            if request.hide_sections:
                for sec in request.hide_sections:
                    if "cv" in input_dict and "sections" in input_dict["cv"] and input_dict["cv"]["sections"]:
                        input_dict["cv"]["sections"].pop(sec, None)
            
            # Validate and build model from our potentially modified dictionary
            model = build_rendercv_model_from_commented_map(input_dict, tmp_path, overlay_sources)
            
            # Generate the Typst file
            typst_path = generate_typst(model)
            if not typst_path:
                raise HTTPException(status_code=400, detail="Failed to generate Typst code.")
                
            # Compile Typst code to PDF
            pdf_path = generate_pdf(model, typst_path)
            if not pdf_path or not pdf_path.exists():
                raise HTTPException(status_code=500, detail="PDF compilation failed to produce output.")
                
            # Read the PDF bytes
            pdf_bytes = pdf_path.read_bytes()
            
            # Send sections list in headers (URL-encoded JSON)
            headers = {
                "X-RenderCV-Sections": urllib.parse.quote(json.dumps(all_sections)),
                "Access-Control-Expose-Headers": "X-RenderCV-Sections"
            }
            return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
            
        except RenderCVUserValidationError as e:
            # Return validation errors with exact YAML line/col coordinates
            errors = []
            for err in e.validation_errors:
                start_line = err.yaml_location[0][0] if err.yaml_location else None
                start_col = err.yaml_location[0][1] if err.yaml_location else None
                errors.append({
                    "message": err.message,
                    "line": start_line,
                    "col": start_col,
                    "schema_location": err.schema_location
                })
            return JSONResponse(
                status_code=422,
                content={
                    "type": "validation_error",
                    "detail": "YAML validation failed",
                    "errors": errors
                }
            )
        except RenderCVUserError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "type": "user_error",
                    "detail": str(e.message or e)
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "type": "internal_error",
                    "detail": f"An unexpected error occurred during rendering: {e!s}",
                    "traceback": "".join(traceback.format_exception(type(e), e, e.__traceback__))
                }
            )
