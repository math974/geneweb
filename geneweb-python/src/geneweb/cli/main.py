"""Command-line interface for GeneWeb server."""

import argparse
import sys
from pathlib import Path

from geneweb.adapters.config.settings import ServerSettings
from geneweb.infrastructure.server.fastapi_server import GeneWebServer


def parse_args(args: list[str] | None = None) -> ServerSettings:
    """Parse command-line arguments and return settings."""
    parser = argparse.ArgumentParser(
        description="GeneWeb Web Daemon - Python Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Basic options
    parser.add_argument("-p", "--port", type=int, default=2317, help="Port number (default: 2317)")
    parser.add_argument("-bd", "--base-dir", type=Path, default=Path("bases"), help="Bases directory")
    parser.add_argument("-hd", "--html-dir", type=Path, default=Path("gw"), help="HTML/templates directory")
    
    # Network options
    parser.add_argument("-a", "--bind-address", help="Bind to specific address")
    parser.add_argument("-only", "--only-address", help="Only accept from this address")
    parser.add_argument("-no_host_address", "--no-host-address", action="store_true", help="Disable reverse DNS")
    
    # Authentication options
    parser.add_argument("-auth", "--auth-file", type=Path, help="Authorization file")
    parser.add_argument("-friend", "--friend-password", help="Friend password")
    parser.add_argument("-wizard", "--wizard-password", help="Wizard password")
    parser.add_argument("-digest", "--use-digest", action="store_true", help="Use Digest auth")
    parser.add_argument("-wjf", "--wizard-just-friend", action="store_true", help="Wizard just friend")
    
    # Timeout and limits
    parser.add_argument("-conn_tmout", "--conn-timeout", type=int, default=120, help="Connection timeout (seconds)")
    parser.add_argument("-login_tmout", "--login-timeout", type=int, default=1800, help="Login timeout (seconds)")
    parser.add_argument("-max_clients", "--max-clients", type=int, help="Max clients (DEPRECATED)")
    
    # Language options
    parser.add_argument("-lang", "--default-lang", default="fr", help="Default language")
    parser.add_argument("-blang", "--browser-lang", action="store_true", help="Use browser language")
    parser.add_argument("-cache_langs", "--cache-langs", help="Cache languages")
    
    # Interface options
    parser.add_argument("-setup_link", "--setup-link", action="store_true", help="Display setup link")
    parser.add_argument("-images_url", "--images-url", help="Images URL")
    parser.add_argument("-images_dir", "--images-dir", help="Images directory")
    parser.add_argument("-allowed_tags", "--allowed-tags-file", type=Path, help="Allowed tags file")
    
    # Logging
    parser.add_argument("-log", "--log-file", type=Path, help="Log file")
    parser.add_argument("-log_level", "--log-level", type=int, default=6, help="Log level (0-7)")
    parser.add_argument("-trace_failed_passwd", "--trace-failed-passwd", action="store_true", help="Trace failed passwords")
    parser.add_argument("-debug", "--debug", action="store_true", help="Debug mode")
    
    # Advanced options
    parser.add_argument("-redirect", "--redirect-addr", help="Redirect address")
    parser.add_argument("-add_lexicon", "--add-lexicon", type=Path, help="Add lexicon file")
    parser.add_argument("-plugin", "--plugin", type=Path, help="Plugin file")
    parser.add_argument("-plugins", "--plugins-dir", type=Path, help="Plugins directory")
    
    # Mode options
    parser.add_argument("-daemon", "--daemon", action="store_true", help="Daemon mode")
    parser.add_argument("-cgi", "--cgi", action="store_true", help="CGI mode")
    parser.add_argument("-predictable_mode", "--predictable-mode", action="store_true", help="Predictable mode")
    
    # Other options
    parser.add_argument("-wd", "--working-dir", type=Path, help="Working directory")
    parser.add_argument("-nolock", "--no-lock", action="store_true", help="No file locking")
    parser.add_argument("-robot_xcl", "--robot-exclude", help="Robot exclusion")
    parser.add_argument("-min_disp_req", "--min-disp-req", type=int, default=6, help="Min display requests")
    
    parser.add_argument("-version", "--version", action="version", version="geneweb-python 0.1.0")
    
    parsed = parser.parse_args(args)
    
    # Convert argparse Namespace to ServerSettings
    settings_dict = {
        "port": parsed.port,
        "base_dir": parsed.base_dir,
        "html_dir": parsed.html_dir,
        "bind_address": parsed.bind_address,
        "only_address": parsed.only_address,
        "no_host_address": parsed.no_host_address,
        "auth_file": parsed.auth_file,
        "friend_password": parsed.friend_password,
        "wizard_password": parsed.wizard_password,
        "use_digest": parsed.use_digest,
        "wizard_just_friend": parsed.wizard_just_friend,
        "conn_timeout": parsed.conn_timeout,
        "login_timeout": parsed.login_timeout,
        "max_clients": parsed.max_clients,
        "default_lang": parsed.default_lang,
        "browser_lang": parsed.browser_lang,
        "cache_langs": parsed.cache_langs,
        "setup_link": parsed.setup_link,
        "images_url": parsed.images_url,
        "images_dir": parsed.images_dir,
        "allowed_tags_file": parsed.allowed_tags_file,
        "log_file": parsed.log_file,
        "log_level": parsed.log_level,
        "trace_failed_passwd": parsed.trace_failed_passwd,
        "debug": parsed.debug,
        "redirect_addr": parsed.redirect_addr,
        "add_lexicon": parsed.add_lexicon,
        "plugin": parsed.plugin,
        "plugins_dir": parsed.plugins_dir,
        "daemon": parsed.daemon,
        "cgi": parsed.cgi,
        "predictable_mode": parsed.predictable_mode,
        "working_dir": parsed.working_dir,
        "no_lock": parsed.no_lock,
        "robot_exclude": parsed.robot_exclude,
        "min_disp_req": parsed.min_disp_req,
    }
    
    return ServerSettings(**settings_dict)


def main() -> int:
    """Main entry point for the gwd command."""
    try:
        settings = parse_args()
        
        print(f"Starting GeneWeb server on port {settings.port}...")
        print(f"Base directory: {settings.base_dir}")
        print(f"HTML directory: {settings.html_dir}")
        
        server = GeneWebServer(settings)
        server.run()
        return 0
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
