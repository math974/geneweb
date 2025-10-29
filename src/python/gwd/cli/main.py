"""CLI GeneWeb GWD - 20 lignes max par fonction"""
import click
from gwd.infrastructure.config import Config
from gwd.infrastructure.server import Server
from gwd.adapters.database.base_repository import MessagePackBaseRepository

@click.group()
def cli():
    """GeneWeb GWD - Serveur de généalogie"""
    pass

@cli.command()
@click.option("--port", default=2317, help="Port du serveur")
@click.option("--bases-dir", required=True, help="Répertoire des bases")
@click.option("--host", default="localhost", help="Host du serveur")
@click.option("--debug", is_flag=True, help="Mode debug")
def serve(port, bases_dir, host, debug):
    """Démarrer le serveur - MAX 20 LIGNES"""
    config = Config(
        bases_dir=bases_dir,
        port=port,
        host=host,
        debug=debug
    )
    
    click.echo(f"🚀 Démarrage GeneWeb GWD sur {host}:{port}")
    click.echo(f"📁 Bases: {bases_dir}")
    
    server = Server(config)
    try:
        server.start()
    except KeyboardInterrupt:
        click.echo("⏹️  Arrêt du serveur...")
        server.stop()

@cli.command()
@click.argument("bases_dir")
def list_bases(bases_dir):
    """Lister les bases - MAX 20 LIGNES"""
    import os
    from pathlib import Path
    
    path = Path(bases_dir)
    if not path.exists():
        click.echo(f"❌ Répertoire non trouvé: {bases_dir}")
        return
    
    click.echo(f"📂 Bases dans {bases_dir}:")
    for file in os.listdir(bases_dir):
        if file.endswith('.msgpack'):
            base_name = file.replace('.msgpack', '')
            click.echo(f"  - {base_name}")

@cli.command()
@click.argument("base_name")
@click.option("--bases-dir", required=True, help="Répertoire des bases")
def info(base_name, bases_dir):
    """Info sur une base - MAX 20 LIGNES"""
    repository = MessagePackBaseRepository(bases_dir)
    base = repository.load_base(base_name)
    
    if base:
        click.echo(f"📊 Base: {base.name}")
        click.echo(f"👥 Personnes: {base.persons_count}")
        click.echo(f"👨‍👩‍👧‍👦 Familles: {base.families_count}")
    else:
        click.echo(f"❌ Base non trouvée: {base_name}")

@cli.command()
@click.argument("base_name")
@click.argument("query")
@click.option("--bases-dir", required=True, help="Répertoire des bases")
def search(base_name, query, bases_dir):
    """Rechercher dans une base - MAX 20 LIGNES"""
    from gwd.use_cases.commands import SearchPersonsCommand
    
    repository = MessagePackBaseRepository(bases_dir)
    cmd = SearchPersonsCommand(repository)
    results = cmd.execute(base_name, query)
    
    click.echo(f"🔍 Recherche '{query}' dans '{base_name}':")
    if results:
        click.echo(f"✅ {len(results)} résultats trouvés:")
        for person in results:
            click.echo(f"  - {person.display_name}")
    else:
        click.echo("❌ Aucun résultat trouvé")

@cli.command()
def version():
    """Afficher la version - MAX 20 LIGNES"""
    click.echo("GeneWeb GWD Python v1.0.0")
    click.echo("© 2023-2024 GeneWeb Team")

if __name__ == '__main__':
    cli()
