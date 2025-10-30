"""CLI GeneWeb GWD - 20 lignes max"""
import click
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

try:
    # Try relative imports first (when running from gwd directory)
    from infrastructure.config import GWDSettings
    from infrastructure.server import GeneWebServer
except ImportError:
    try:
        # Try absolute imports (when running as module)
        from gwd.infrastructure.config import GWDSettings
        from gwd.infrastructure.server import GeneWebServer
    except ImportError:
        # Last attempt: try adding parent to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        try:
            from infrastructure.config import GWDSettings
            from infrastructure.server import GeneWebServer
        except ImportError:
            click.echo("Error: gwd module not found. Please check installation.", err=True)
            click.echo(f"Python path: {sys.path[:3]}", err=True)
            sys.exit(1)

@click.command()
@click.option('--port', '-p', default=2317, help='Port du serveur')
@click.option('--host', '-h', default='localhost', help='Adresse du serveur')
@click.option('--bases-dir', '-bd', help='Répertoire des bases .msgpack')
@click.option('--debug', is_flag=True, help='Mode debug')
def serve(port, host, bases_dir, debug):
    """Démarre le serveur GeneWeb Python GWD modulaire - 20 lignes max"""
    settings_kwargs = {"port": port, "host": host, "debug": debug}
    if bases_dir:
        settings_kwargs["bases_dir"] = bases_dir
    settings = GWDSettings(**settings_kwargs)
    server = GeneWebServer(settings)

    click.echo(f"🚀 Démarrage GeneWeb GWD modulaire sur {host}:{port}")
    click.echo(f"📁 Bases: {settings.bases_dir}")

    try:
        server.start()
    except KeyboardInterrupt:
        click.echo("⏹️  Arrêt du serveur...")

if __name__ == '__main__':
    serve()
