"""
ACTP CLI - Agent Context Transfer Protocol Command Line Interface
"""
import click
import json
from pathlib import Path
from importlib.metadata import version as get_version

try:
    ACTP_VERSION = get_version("actp")
except ImportError:
    ACTP_VERSION = "0.1-dev"

from actp.core.packager import ACTPPackagerFactory, ACTPExtractor
from actp.validator import ACTPValidator


@click.group()
@click.version_option(version=ACTP_VERSION, prog_name="actp")
def cli():
    """ACTP - Agent Context Transfer Protocol CLI
    
    Pack your project into portable AI context packets.
    JSON-LD compatible, semantically-rich, model-agnostic.
    """
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='context.actp', 
              help='Output ACTP file (default: context.actp)')
@click.option('--name', '-n', required=True,
              help='Project name')
@click.option('--goal', '-g', required=True,
              help='Project goal (one sentence)')
@click.option('--depth', '-d', default=10, type=int,
              help='Maximum directory depth to traverse')
@click.option('--created-by', default=None,
              help='Your name/identifier')
@click.option('--model', '-m', default=None,
              type=click.Choice(['claude', 'chatgpt', 'gemini', 'other']),
              help='AI model context')
def pack(project_path, output, name, goal, depth, created_by, model):
    """Pack a project directory into ACTP format
    
    Example:
        actp pack . --name "ACTP" --goal "Protocol implementation" -o pkg.actp
    """
    try:
        click.echo(f"📦 Packing '{name}'...")
        click.echo(f"   Goal: {goal}")
        
        packet = ACTPPackagerFactory.pack_directory(
            directory=Path(project_path),
            project_name=name,
            project_goal=goal,
            created_by=created_by,
            source_model=model,
            max_depth=depth
        )
        
        # Dosyaya kaydet
        packet_dict = packet.to_dict()
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(packet_dict, f, indent=2, ensure_ascii=False)
        
        # Stat'lar
        num_files = len(packet.files) if hasattr(packet, 'files') else 0
        num_decisions = len(packet.decisions)
        num_symbols = len(packet.symbol_legend)
        
        click.echo(f"✅ Packed to '{output}'")
        click.echo(f"   Files indexed: {num_files}")
        click.echo(f"   Decisions: {num_decisions}")
        click.echo(f"   Symbol legend: {num_symbols}")
        click.echo(f"   @context: {packet.context}")
        
    except Exception as e:
        raise click.ClickException(f"Failed to pack: {e}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
def validate(actp_file):
    """Validate ACTP package against schema
    
    Checks for:
    - JSON-LD structure (@context, @type, actp_version)
    - Required fields (project, decisions, symbol_legend)
    - Vocabulary hash consistency
    - Decision priority/certainty/mutability enums
    """
    try:
        click.echo(f"🔍 Validating '{actp_file}'...")
        
        # Dosyayı yükle
        with open(actp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Doğrula
        validator = ACTPValidator()
        is_valid, errors, warnings = validator.validate_data(data)
        
        if errors:
            click.echo("❌ Validation failed:")
            for error in errors:
                click.echo(f"   ERROR: {error}")
            raise click.ClickException("Invalid ACTP packet")
        
        if warnings:
            click.echo("⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"   WARNING: {warning}")
        
        click.echo("✅ Validation passed")
        click.echo(f"   Project: {data.get('project', {}).get('name', 'unknown')}")
        click.echo(f"   Decisions: {len(data.get('decisions', []))}")
        click.echo(f"   Created: {data.get('created_at', 'unknown')}")
        
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")
    except Exception as e:
        raise click.ClickException(f"Validation error: {e}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
def inspect(actp_file):
    """Inspect ACTP package contents
    
    Shows package metadata, decisions, tasks, and statistics.
    """
    try:
        with open(actp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Header
        project = data.get('project', {})
        click.echo(f"\n📋 ACTP Package: {actp_file}")
        click.echo(f"{'=' * 60}")
        
        # Project info
        click.echo(f"\n🎯 Project")
        click.echo(f"   Name: {project.get('name', 'unknown')}")
        click.echo(f"   Goal: {project.get('goal', 'unknown')}")
        if project.get('constraints'):
            click.echo(f"   Constraints: {len(project['constraints'])} rule(s)")
        if project.get('soft_preferences'):
            click.echo(f"   Preferences: {len(project['soft_preferences'])} item(s)")
        
        # Metadata
        click.echo(f"\n📅 Metadata")
        click.echo(f"   Created: {data.get('created_at', 'unknown')}")
        click.echo(f"   @context: {data.get('@context', 'unknown')}")
        click.echo(f"   Model: {data.get('source_model', 'unknown')}")
        
        # Files
        files = data.get('files', [])
        click.echo(f"\n📁 Files ({len(files)})")
        for i, file_info in enumerate(files[:5], 1):
            if isinstance(file_info, dict):
                path = file_info.get('path', '?')
                size = file_info.get('size', 0)
                click.echo(f"   [{i}] {path} ({size} bytes)")
        if len(files) > 5:
            click.echo(f"   ... and {len(files) - 5} more")
        
        # Decisions
        decisions = data.get('decisions', [])
        click.echo(f"\n📌 Decisions ({len(decisions)})")
        for i, dec in enumerate(decisions[:5], 1):
            click.echo(f"   [{i}] {dec.get('id', '?')} ({dec.get('priority', '?')}) - {dec.get('content', '')[:40]}...")
        if len(decisions) > 5:
            click.echo(f"   ... and {len(decisions) - 5} more")
        
        # Tasks
        tasks = data.get('tasks', [])
        if tasks:
            click.echo(f"\n✅ Tasks ({len(tasks)})")
            for i, task in enumerate(tasks[:5], 1):
                status = task.get('status', '?')
                click.echo(f"   [{status}] {task.get('id', '?')} - {task.get('description', '')[:40]}...")
        
        # Open questions
        questions = data.get('open_questions', [])
        if questions:
            click.echo(f"\n❓ Open Questions ({len(questions)})")
            for i, q in enumerate(questions[:3], 1):
                click.echo(f"   {i}. {q[:50]}...")
        
        # Next steps
        steps = data.get('next_steps', [])
        if steps:
            click.echo(f"\n➡️  Next Steps ({len(steps)})")
            for i, step in enumerate(steps[:3], 1):
                click.echo(f"   {i}. {step[:50]}...")
        
        # Summary
        click.echo(f"\n📊 Summary")
        click.echo(f"   Symbol legend: {len(data.get('symbol_legend', {}))}")
        click.echo(f"   Entity map: {len(data.get('entity_map', {}))}")
        click.echo(f"   Priority matrix: {len(data.get('priority_matrix', []))}")
        
        click.echo(f"\n{'=' * 60}\n")
        
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")
    except Exception as e:
        raise click.ClickException(f"Inspect error: {e}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(), default='.')
def export(actp_file, output_dir):
    """Export ACTP package contents to files
    
    Creates a directory with:
    - decisions.json
    - tasks.json
    - metadata.json
    - context.txt
    """
    try:
        with open(actp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"💾 Exporting to '{output_dir}'...")
        
        # Decisions
        if data.get('decisions'):
            with open(output_path / 'decisions.json', 'w', encoding='utf-8') as f:
                json.dump(data['decisions'], f, indent=2, ensure_ascii=False)
            click.echo(f"   ✓ decisions.json")
        
        # Tasks
        if data.get('tasks'):
            with open(output_path / 'tasks.json', 'w', encoding='utf-8') as f:
                json.dump(data['tasks'], f, indent=2, ensure_ascii=False)
            click.echo(f"   ✓ tasks.json")
        
        # Metadata
        metadata = {
            'project': data.get('project', {}),
            'created_at': data.get('created_at'),
            'source_model': data.get('source_model'),
            'symbol_legend': data.get('symbol_legend', {}),
        }
        with open(output_path / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        click.echo(f"   ✓ metadata.json")
        
        # Context summary
        context_text = f"""# ACTP Context Export

Project: {data.get('project', {}).get('name', 'Unknown')}
Goal: {data.get('project', {}).get('goal', 'Unknown')}

Decisions: {len(data.get('decisions', []))}
Tasks: {len(data.get('tasks', []))}
Questions: {len(data.get('open_questions', []))}

Generated: {data.get('created_at', 'Unknown')}
Model: {data.get('source_model', 'Unknown')}
"""
        with open(output_path / 'context.txt', 'w', encoding='utf-8') as f:
            f.write(context_text)
        click.echo(f"   ✓ context.txt")
        
        click.echo(f"✅ Export complete")
        
    except Exception as e:
        raise click.ClickException(f"Export error: {e}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), default='./restored',
              help='Output directory (default: ./restored)')
def unpack(actp_file, output):
    """Extract files from ACTP package
    
    Restores the original directory structure from the packet.
    
    Example:
        actp unpack context.actp --output ./restored
    """
    try:
        click.echo(f"🔓 Unpacking '{actp_file}'...")
        
        # Dosyaları çıkar
        extracted_count = ACTPExtractor.extract_from_file(
            packet_file=Path(actp_file),
            output_dir=Path(output)
        )
        
        click.echo(f"✅ Unpacked {extracted_count} files to '{output}'")
        click.echo(f"   Directory structure restored")
        
    except FileNotFoundError as e:
        raise click.ClickException(f"File not found: {e}")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid ACTP file: {e}")
    except Exception as e:
        raise click.ClickException(f"Unpack error: {e}")


@cli.command()
@click.argument('actp_file', type=click.Path(exists=True))
@click.option('--format', '-f', default='json', 
              type=click.Choice(['json', 'yaml', 'markdown']),
              help='Output format')
def summarize(actp_file, format):
    """Summarize ACTP package as text
    
    Generates a human-readable summary of the packet.
    """
    try:
        with open(actp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        project = data.get('project', {})
        
        if format == 'markdown':
            output = f"""# {project.get('name', 'ACTP Package')}

## Goal
{project.get('goal', 'No goal specified')}

## Decisions ({len(data.get('decisions', []))})

"""
            for dec in data.get('decisions', []):
                output += f"### {dec.get('id', '?')} - {dec.get('content', '?')}\n"
                output += f"- **Priority:** {dec.get('priority', '?')}\n"
                output += f"- **Certainty:** {dec.get('certainty', '?')}\n"
                output += f"- **Mutability:** {dec.get('mutability', '?')}\n"
                if dec.get('rationale'):
                    output += f"- **Rationale:** {dec['rationale']}\n"
                output += "\n"
            
            if data.get('next_steps'):
                output += f"## Next Steps\n\n"
                for step in data.get('next_steps', []):
                    output += f"- {step}\n"
            
            click.echo(output)
        else:
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    
    except Exception as e:
        raise click.ClickException(f"Summarize error: {e}")


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main()
