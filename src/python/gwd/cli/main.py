"""CLI GeneWeb GWD - 20 lignes max"""
import click
from geneweb_gwd.infrastructure.config import GWDSettings
from geneweb_gwd.infrastructure.server import GeneWebServer

@click.command()
@click.option('--port', '-p', default=2317, help='Port du serveur')
@click.option('--host', '-h', default='localhost', help='Adresse du serveur')
@click.option('--bases-dir', '-bd', help='Répertoire des bases .msgpack')
@click.option('--debug', is_flag=True, help='Mode debug')
def serve(port, host, bases_dir, debug):
    """Démarre le serveur GeneWeb Python GWD modulaire - 20 lignes max"""
    settings = GWDSettings(port=port, host=host, bases_dir=bases_dir, debug=debug)
    server = GeneWebServer(settings)
    
    click.echo(f"🚀 Démarrage GeneWeb GWD modulaire sur {host}:{port}")
    click.echo(f"📁 Bases: {settings.bases_dir}")
    
    try:
        server.start()
    except KeyboardInterrupt:
        click.echo("⏹️  Arrêt du serveur...")

if __name__ == '__main__':
    serve()
