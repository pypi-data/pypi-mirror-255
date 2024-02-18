import click

from scoutbook_parser.main import Parser


@click.command()
@click.option(
    "-t",
    "--output-type",
    default="yaml",
    help="output type, options are yaml (default), toml, and json",
)
@click.option(
    "-o",
    "--outfile",
    type=click.Path(dir_okay=False, writable=True),
    help='output filename, default is "output" with the extension',
)
@click.option(
    "-p",
    "--input_personal",
    type=click.Path(exists=True, dir_okay=False),
    help="input filename for personal data (optional)",
)
@click.argument(
    "input_advancement",
    type=click.Path(exists=True, dir_okay=False),
    default="advancement.csv",
)
def main(output_type=None, outfile=None, input_personal=None, input_advancement=None):
    if not outfile:
        output_type = "yaml"
    else:
        match outfile:
            case [file, "json"]:
                output_type = "json"
            case [file, "yaml"]:
                output_type = "yaml"
            case [file, "toml"]:
                output_type = "toml"
    parser = Parser(
        input_personal=input_personal,
        input_advancement=input_advancement,
        outfile=outfile,
        file_format=output_type,
    )

    if outfile:
        parser.dump()
    else:
        print(parser.dumps())


if __name__ == "__main__":
    main()
