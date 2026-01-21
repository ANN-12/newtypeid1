"""Utility script to initialize and verify the database connection."""
import os
from pathlib import Path

from app import create_app
from extensions import db


def main():
    # Determine config from FLASK_ENV or default
    config_name = os.getenv('FLASK_ENV', 'default')
    app = create_app(config_name)

    with app.app_context():
        print('Using SQLALCHEMY_DATABASE_URI =', app.config.get('SQLALCHEMY_DATABASE_URI'))
        # Create tables if they don't exist
        db.create_all()
        # Check if sqlite file exists when using sqlite
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if uri.startswith('sqlite:'):
            # sqlite:///path -> file path after third slash
            path = uri.replace('sqlite:///', '')
            exists = Path(path).exists()
            print(f'SQLite DB file "{path}" exists: {exists}')
        else:
            print('Non-sqlite DB in use; ensure your DB server is reachable and credentials are correct.')


if __name__ == '__main__':
    main()
