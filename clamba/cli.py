"""
Command Line Interface for CLAMBA
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("CLI requires additional dependencies. Install with: pip install clamba[cli]")
    sys.exit(1)

from .config.settings import CLAMBAConfig, create_sample_config, load_config
from .core.analyzer import CLAMBAAnalyzer
from .models.contract import ContractType

app = typer.Typer(help="CLAMBA - Smart Legal Contract Automaton Generator")
console = Console()


def show_banner():
    """Show CLAMBA banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                        CLAMBA                             ║
    ║        Smart Legal Contract Automaton Generator           ║
    ║                     Powered by AI                        ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


@app.command()
def analyze(
    pdf_path: str = typer.Argument(..., help="Path to PDF contract file"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI provider (ollama, openai, anthropic)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="AI model name"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: Optional[str] = typer.Option("json", "--format", "-f", help="Output format (json, yaml)"),
    contract_type: Optional[str] = typer.Option(None, "--type", "-t", help="Contract type hint"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Analyze a PDF contract and generate automatons
    """
    show_banner()
    
    # Validate PDF file
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        console.print(f"❌ PDF file not found: {pdf_path}", style="red")
        raise typer.Exit(1)
    
    # Load configuration
    try:
        if config:
            clamba_config = CLAMBAConfig.from_file(config)
        else:
            clamba_config = load_config()
    except Exception as e:
        console.print(f"❌ Configuration error: {str(e)}", style="red")
        raise typer.Exit(1)
    
    # Override config with CLI parameters
    if provider:
        clamba_config.ai.provider = provider
    if model:
        if clamba_config.ai.provider == "ollama":
            clamba_config.ai.ollama.model = model
        elif clamba_config.ai.provider == "openai" and clamba_config.ai.openai:
            clamba_config.ai.openai.model = model
        elif clamba_config.ai.provider == "anthropic" and clamba_config.ai.anthropic:
            clamba_config.ai.anthropic.model = model
    if format:
        clamba_config.output.output_format = format
    if debug:
        clamba_config.debug = True
    
    # Parse contract type
    contract_type_enum = None
    if contract_type:
        try:
            contract_type_enum = ContractType(contract_type.lower())
        except ValueError:
            console.print(f"❌ Invalid contract type: {contract_type}", style="red")
            console.print(f"Valid types: {', '.join([ct.value for ct in ContractType])}")
            raise typer.Exit(1)
    
    # Show configuration
    if verbose:
        config_table = Table(title="Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("AI Provider", clamba_config.ai.provider)
        config_table.add_row("Output Format", clamba_config.output.output_format)
        config_table.add_row("Debug Mode", str(clamba_config.debug))
        if contract_type_enum:
            config_table.add_row("Contract Type", contract_type_enum.value)
        
        console.print(config_table)
        console.print()
    
    # Initialize analyzer
    try:
        analyzer = CLAMBAAnalyzer(clamba_config)
    except Exception as e:
        console.print(f"❌ Analyzer initialization failed: {str(e)}", style="red")
        raise typer.Exit(1)
    
    # Validate configuration
    validation = analyzer.validate_configuration()
    if not validation["ai_provider_available"]:
        console.print("❌ AI provider not available", style="red")
        if clamba_config.ai.provider == "ollama":
            console.print("💡 Make sure Ollama is running: ollama serve", style="yellow")
        raise typer.Exit(1)
    
    # Perform analysis
    console.print(f"🔍 Analyzing contract: {pdf_file.name}", style="blue")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("Analyzing contract...", total=None)
            result = analyzer.analyze_contract(
                pdf_path=pdf_file,
                contract_type=contract_type_enum
            )
            progress.update(task, description="✅ Analysis complete")
        
    except Exception as e:
        console.print(f"❌ Analysis failed: {str(e)}", style="red")
        if debug:
            console.print_exception()
        raise typer.Exit(1)
    
    # Determine output file
    if not output:
        output = pdf_file.stem + f"_automates.{clamba_config.output.output_format}"
    
    # Save result
    try:
        analyzer.save_result(result, output)
        console.print(f"💾 Result saved: {output}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to save result: {str(e)}", style="red")
        raise typer.Exit(1)
    
    # Show summary
    summary = result.get_summary()
    
    summary_panel = Panel(
        f"""
[green]✅ Analysis Completed Successfully[/green]

📋 Contract: {summary['contract_name']}
⚙️  Automatons: {summary['automatons_count']}
🔧 Processes: {summary['processes_count']}
🔗 Dependencies: {summary['dependencies_count']}
📊 Confidence: {summary['confidence_score']:.2f}
⏱️  Time: {summary['analysis_time']:.1f}s
🤖 AI: {clamba_config.ai.provider}
        """.strip(),
        title="Analysis Summary",
        border_style="green"
    )
    
    console.print(summary_panel)


@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="Directory containing PDF files"),
    output_dir: str = typer.Argument(..., help="Output directory for results"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    pattern: str = typer.Option("*.pdf", "--pattern", "-p", help="File pattern to match"),
    provider: Optional[str] = typer.Option(None, "--provider", help="AI provider override"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
):
    """
    Analyze multiple PDF contracts in batch
    """
    show_banner()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        console.print(f"❌ Input directory not found: {input_dir}", style="red")
        raise typer.Exit(1)
    
    # Find PDF files
    pdf_files = list(input_path.glob(pattern))
    if not pdf_files:
        console.print(f"❌ No PDF files found in {input_dir} matching {pattern}", style="red")
        raise typer.Exit(1)
    
    console.print(f"📁 Found {len(pdf_files)} PDF files", style="blue")
    
    # Load configuration
    try:
        clamba_config = CLAMBAConfig.from_file(config) if config else load_config()
        if provider:
            clamba_config.ai.provider = provider
        if debug:
            clamba_config.debug = True
    except Exception as e:
        console.print(f"❌ Configuration error: {str(e)}", style="red")
        raise typer.Exit(1)
    
    # Initialize analyzer
    try:
        analyzer = CLAMBAAnalyzer(clamba_config)
    except Exception as e:
        console.print(f"❌ Analyzer initialization failed: {str(e)}", style="red")
        raise typer.Exit(1)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Batch analysis
    console.print(f"🔄 Starting batch analysis...", style="blue")
    
    try:
        results = analyzer.analyze_multiple_contracts(
            pdf_paths=pdf_files,
            output_dir=output_path
        )
        
        console.print(f"✅ Batch analysis completed: {len(results)}/{len(pdf_files)} successful", style="green")
        
    except Exception as e:
        console.print(f"❌ Batch analysis failed: {str(e)}", style="red")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def config_create(
    output: str = typer.Option("clamba_config.yaml", "--output", "-o", help="Output config file path"),
):
    """
    Create a sample configuration file
    """
    show_banner()
    
    try:
        create_sample_config(output)
        console.print(f"✅ Sample configuration created: {output}", style="green")
        console.print("💡 Edit the file to customize your settings", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to create config: {str(e)}", style="red")
        raise typer.Exit(1)


@app.command()
def config_validate(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file to validate"),
):
    """
    Validate configuration file
    """
    show_banner()
    
    try:
        clamba_config = CLAMBAConfig.from_file(config) if config else load_config()
        
        console.print("🔍 Validating configuration...", style="blue")
        
        # Basic validation
        errors = []
        
        if not clamba_config.validate_ai_config():
            errors.append("AI configuration is invalid")
        
        if errors:
            console.print("❌ Configuration validation failed:", style="red")
            for error in errors:
                console.print(f"  • {error}", style="red")
            raise typer.Exit(1)
        
        # Test AI provider
        try:
            analyzer = CLAMBAAnalyzer(clamba_config)
            validation = analyzer.validate_configuration()
            
            status_table = Table(title="Validation Results")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="")
            
            for component, status in validation.items():
                status_style = "green" if status else "red"
                status_text = "✅ OK" if status else "❌ Failed"
                status_table.add_row(component.replace("_", " ").title(), Text(status_text, style=status_style))
            
            console.print(status_table)
            
            if all(validation.values()):
                console.print("✅ Configuration is valid and ready to use", style="green")
            else:
                console.print("⚠️ Some components failed validation", style="yellow")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"❌ Validation test failed: {str(e)}", style="red")
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"❌ Configuration error: {str(e)}", style="red")
        raise typer.Exit(1)


@app.command()
def info():
    """
    Show CLAMBA information
    """
    show_banner()
    
    info_table = Table(title="CLAMBA Information")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    # Basic info
    info_table.add_row("Version", "0.1.0")
    info_table.add_row("Description", "Smart Legal Contract Automaton Generator")
    
    # Supported contract types
    contract_types = ", ".join([ct.value for ct in ContractType if ct != ContractType.AUTO])
    info_table.add_row("Supported Contract Types", contract_types)
    
    # Available AI providers
    try:
        from .ai.factory import AIProviderFactory
        providers = AIProviderFactory.get_available_providers()
        info_table.add_row("Available AI Providers", ", ".join(providers))
    except Exception:
        info_table.add_row("Available AI Providers", "Unable to detect")
    
    console.print(info_table)
    
    # Usage examples
    examples_panel = Panel(
        """
[cyan]Basic Usage:[/cyan]
  clamba analyze contract.pdf

[cyan]With specific AI provider:[/cyan]
  clamba analyze contract.pdf --provider openai --model gpt-4

[cyan]Batch processing:[/cyan]
  clamba batch ./contracts/ ./results/

[cyan]Create configuration:[/cyan]
  clamba config-create --output my_config.yaml

[cyan]Validate configuration:[/cyan]
  clamba config-validate --config my_config.yaml
        """.strip(),
        title="Usage Examples",
        border_style="blue"
    )
    
    console.print(examples_panel)


def main():
    """Main entry point for CLI"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n❌ Operation cancelled by user", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {str(e)}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()