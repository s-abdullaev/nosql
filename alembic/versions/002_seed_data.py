"""Seed restaurants and regions in Paris.

Revision ID: 0002
Revises: 0001
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO restaurant (name, cuisine, address, location) VALUES
        (
            'Le Jules Verne', 'French fine dining',
            'Eiffel Tower, Champ de Mars, 75007 Paris',
            ST_SetSRID(ST_MakePoint(2.2945, 48.8584), 4326)
        ),
        (
            'Le Comptoir du Panthéon', 'French brasserie',
            '5 Rue Soufflot, 75005 Paris',
            ST_SetSRID(ST_MakePoint(2.3458, 48.8462), 4326)
        ),
        (
            'Café de Flore', 'French café',
            '172 Bd Saint-Germain, 75006 Paris',
            ST_SetSRID(ST_MakePoint(2.3325, 48.8540), 4326)
        ),
        (
            'Le Procope', 'French historic',
            '13 Rue de l''Ancienne Comédie, 75006 Paris',
            ST_SetSRID(ST_MakePoint(2.3389, 48.8533), 4326)
        ),
        (
            'Chez Janou', 'Provençal',
            '2 Rue Roger Verlomme, 75003 Paris',
            ST_SetSRID(ST_MakePoint(2.3625, 48.8572), 4326)
        ),
        (
            'Bouillon Chartier', 'French traditional',
            '7 Rue du Faubourg Montmartre, 75009 Paris',
            ST_SetSRID(ST_MakePoint(2.3470, 48.8747), 4326)
        ),
        (
            'Le Train Bleu', 'French classic',
            'Gare de Lyon, Place Louis-Armand, 75012 Paris',
            ST_SetSRID(ST_MakePoint(2.3735, 48.8443), 4326)
        ),
        (
            'Brasserie Lipp', 'French brasserie',
            '151 Bd Saint-Germain, 75006 Paris',
            ST_SetSRID(ST_MakePoint(2.3335, 48.8541), 4326)
        ),
        (
            'Le Petit Cler', 'French bistro',
            '29 Rue Cler, 75007 Paris',
            ST_SetSRID(ST_MakePoint(2.3098, 48.8568), 4326)
        ),
        (
            'Pink Mamma', 'Italian',
            '20bis Rue de Douai, 75009 Paris',
            ST_SetSRID(ST_MakePoint(2.3370, 48.8820), 4326)
        );
        """
    )

    op.execute(
        """
        INSERT INTO region (name, description, boundary) VALUES
        (
            'Saint-Germain-des-Prés',
            'Historic literary and artistic neighborhood in the 6th arrondissement',
            ST_SetSRID(ST_GeomFromText(
                'POLYGON((2.3260 48.8565, 2.3420 48.8565, 2.3420 48.8500, 2.3260 48.8500, 2.3260 48.8565))'
            ), 4326)
        ),
        (
            'Le Marais',
            'Trendy district spanning the 3rd and 4th arrondissements',
            ST_SetSRID(ST_GeomFromText(
                'POLYGON((2.3530 48.8620, 2.3700 48.8620, 2.3700 48.8530, 2.3530 48.8530, 2.3530 48.8620))'
            ), 4326)
        ),
        (
            'Tour Eiffel',
            'Area surrounding the Eiffel Tower in the 7th arrondissement',
            ST_SetSRID(ST_GeomFromText(
                'POLYGON((2.2880 48.8620, 2.3150 48.8620, 2.3150 48.8530, 2.2880 48.8530, 2.2880 48.8620))'
            ), 4326)
        ),
        (
            'Quartier Latin',
            'Historic student quarter in the 5th arrondissement',
            ST_SetSRID(ST_GeomFromText(
                'POLYGON((2.3380 48.8530, 2.3560 48.8530, 2.3560 48.8420, 2.3380 48.8420, 2.3380 48.8530))'
            ), 4326)
        ),
        (
            'Rive Gauche Centre',
            'Central Left Bank area overlapping Saint-Germain and Quartier Latin',
            ST_SetSRID(ST_GeomFromText(
                'POLYGON((2.3350 48.8560, 2.3500 48.8560, 2.3500 48.8440, 2.3350 48.8440, 2.3350 48.8560))'
            ), 4326)
        );
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM restaurant")
    op.execute("DELETE FROM region")
