import pydantic


class BaseModelWithoutExtraKeys(pydantic.BaseModel):
    """Pydantic base model that rejects unrecognized fields.

    Why:
        Most RenderCV models have fixed schemas. Forbidding extra keys
        catches typos and unsupported fields early during YAML validation,
        giving users clear error messages instead of silently ignoring
        misspelled options.
    """

    model_config = pydantic.ConfigDict(extra="forbid", validate_default=True)
