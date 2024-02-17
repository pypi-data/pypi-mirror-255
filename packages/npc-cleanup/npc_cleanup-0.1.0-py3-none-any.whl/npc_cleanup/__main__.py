import click
import json
import logging
import pathlib

from . import validation


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")
    if debug:
        validation.logger.setLevel(logging.DEBUG)


@cli.command()
@click.argument(
    'session_id',
    type=str,
)
@click.option(
    '--output_path',
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
    default="validation.json",
)
def validate_npc_session(
    session_id,
    output_path,
):
    result = validation.validate_npc_session(
        session_id,
    )
    pathlib.Path(output_path) \
        .write_text(
            json.dumps(
                [
                    validation_result.model_dump()
                    for validation_result in result
                ],
                indent=4,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    cli()