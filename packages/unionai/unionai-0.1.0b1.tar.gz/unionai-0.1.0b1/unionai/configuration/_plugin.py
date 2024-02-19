from typing import Optional

import click
from click import Group
from flytekit.remote import FlyteRemote

from unionai._config import _UNIONAI_CONFIG, _get_config_obj, _get_default_image
from unionai.cli._create import create
from unionai.cli._delete import delete
from unionai.cli._get import get
from unionai.cli._update import update
from unionai.remote import UnionRemote


class UnionAIPlugin:
    @staticmethod
    def get_remote(
        config: Optional[str],
        project: str,
        domain: str,
        data_upload_location: Optional[str] = None,
    ) -> FlyteRemote:
        cfg_obj = _get_config_obj(config)
        if cfg_obj.platform.endpoint == _UNIONAI_CONFIG.serverless_endpoint and project == "flytesnacks":
            project = "default"

        return UnionRemote(
            cfg_obj,
            default_project=project,
            default_domain=domain,
            data_upload_location=data_upload_location,
        )

    @staticmethod
    def configure_pyflyte_cli(main: Group) -> Group:
        """Configure pyflyte's CLI."""
        # Configure org at the top level:

        def _cli_main_config_callback(ctx, param, value):
            # Set org based on config from `pyflyte --config` for downstream cli
            # commands to use.
            _UNIONAI_CONFIG.config = value
            return value

        for p in main.params:
            if p.name == "config":
                p.callback = _cli_main_config_callback

        def _set_org(ctx, param, value):
            _UNIONAI_CONFIG.org = value

        main.params.append(
            click.Option(
                ["--org"],
                help="Set organization",
                hidden=True,
                callback=_set_org,
                expose_value=False,
            )
        )

        # NOTE: This is a stop-gap measure to make sure that workflows run on
        # serverless use the correct default project name. Eventually serverless
        # will support a "default" project instead of relying on
        # "{username}-project"
        from flytekit.clis.sdk_in_container.run import RunCommand, RunLevelParams

        class RunWithNewProjectDefault(RunCommand):
            def get_command(self, ctx, filename):
                command = super().get_command(ctx, filename)
                run_params: RunLevelParams = ctx.obj
                if run_params.is_remote and run_params.project == "flytesnacks":
                    cfg_obj = _get_config_obj(run_params.config_file)
                    if cfg_obj.platform.endpoint == _UNIONAI_CONFIG.serverless_endpoint:
                        # On Serverless, change the default project value
                        run_params.project = "default"
                return command

        main.add_command(RunWithNewProjectDefault(), "run")

        def update_or_create_group(new_group):
            try:
                main_group = main.commands[new_group.name]
                for name, command in new_group.commands.items():
                    main_group.add_command(command, name)
            except KeyError:
                main.add_command(new_group)

        new_groups = [create, delete, update, get]
        for group in new_groups:
            update_or_create_group(group)

        return main

    @staticmethod
    def secret_requires_group() -> bool:
        """Return True if secrets require group entry."""
        return False

    @staticmethod
    def get_default_image() -> Optional[str]:
        """Return default image."""
        return _get_default_image()
