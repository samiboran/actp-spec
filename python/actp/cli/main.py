import click
import json
from pathlib import Path
from importlib.metadata import version as get_version

try:
    ACTP_VERSION = get_version("actp")
except ImportError:
    ACTP_VERSION = "0.1.3-dev"

from actp.core.packager import ACTPPackager
from actp.core.schema import ACTPValidator


@click.group()
@click.version_option(version=ACTP_VERSION, prog_name="actp")
def cli():
    """ACTP - Agent Context Transfer Protocol CLI"""
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='context.actp', help='Output file')
@click.option('--depth', '-d', default=3, help='Directory traversal depth')
@click.option('--strict-secrets', is_flag=True, help='Fail if secrets detected')
def pack(project_path, output, depth, strict_secrets):
    """Pack a project directory into ACTP format"""
    packager = ACTPPackager()
    result = packager.pack(
        Path(project_path), max_depth=depth, strict_secrets=strict_secrets
    )

    with open(output, 'w') as f:
        json.dump(result, f, indent=2)

    click.echo(f"Packed {result['metadata']['total_files']} files to {output}")
    click.echo(f"  Estimated tokens: {result['metadata']['total_tokens_estimate']}")

    if result['metadata']['warnings']:
        click.echo(f"  Warnings ({len(result['metadata']['warnings'])}):")
        for w in result['metadata']['warnings'][:5]:
            click.echo(f"    - {w}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='.', help='Output directory')
def unpack(actp_file, output_dir):
    """Unpack ACTP file to directory (path traversal protected)"""
    packager = ACTPPackager()

    # Guvenli JSON yukleme
    try:
        with open(actp_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")

    packager.unpack(data, Path(output_dir))
    click.echo(f"Unpacked to {output_dir}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
def inspect(actp_file):
    """Inspect ACTP package metadata"""
    try:
        with open(actp_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")

    click.echo(f"ACTP Package: {actp_file}")
    click.echo(f"  Version: {data.get('version', 'unknown')}")
    click.echo(f"  Project: {data.get('project_name', 'unknown')}")
    click.echo(f"  Generated: {data.get('generated_at', 'unknown')}")
    click.echo(f"  Files: {data['metadata']['total_files']}")
    click.echo(f"  Est. Tokens: {data['metadata']['total_tokens_estimate']}")

    types = {}
    for f in data.get('files', []):
        t = f.get('type', 'unknown')
        types[t] = types.get(t, 0) + 1
    if types:
        click.echo("  File types:")
        for t, count in sorted(types.items(), key=lambda x: -x[1])[:5]:
            click.echo(f"    {t}: {count}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
@click.option('--checksums', is_flag=True, help='Verify SHA-256 checksums')
def validate(actp_file, checksums):
    """Validate ACTP package against schema and checksums"""
    # Guvenli JSON yukleme
    try:
        with open(actp_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")

    validator = ACTPValidator()

    # Schema dogrulama
    is_valid, errors = validator.validate(data)
    if not is_valid:
        click.echo("Schema dogrulama basarisiz:")
        for e in errors:
            click.echo(f"  - {e}")
        raise click.ClickException("Gecersiz ACTP paketi")

    click.echo("Schema dogrulama basarili")

    # Checksum dogrulama
    if checksums:
        ok, checksum_errors = validator.validate_checksums(data)
        if not ok:
            click.echo("Checksum dogrulama basarisiz:")
            for e in checksum_errors:
                click.echo(f"  - {e}")
            raise click.ClickException("Checksum uyusmazligi")
        click.echo("Checksum dogrulama basarili")

    click.echo(f"{actp_file} gecerli")


def main():
    cli()

if __name__ == '__main__':
    main()
