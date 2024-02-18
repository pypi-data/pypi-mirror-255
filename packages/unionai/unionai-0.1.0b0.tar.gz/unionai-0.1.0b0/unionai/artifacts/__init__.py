# TODO: Remove try/except when https://github.com/flyteorg/flytekit/pull/2136/ is merged
try:
    import flytekit.core.artifact  # noqa: F401 place this line first

    from unionai.artifacts._artifact import Artifact
    from unionai.artifacts._triggers import Trigger

    __all__ = ["Artifact", "Trigger"]

except ModuleNotFoundError:
    pass
