"""neu aufsetzen

Revision ID: a1819474f4bc
Revises: 
Create Date: 2023-12-23 11:19:13.899848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1819474f4bc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Adresse',
    sa.Column('adresse_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('strasse', sa.String(), nullable=True),
    sa.Column('hausnummer', sa.Integer(), nullable=True),
    sa.Column('zusatz', sa.String(), nullable=True),
    sa.Column('plz', sa.Integer(), nullable=True),
    sa.Column('stadt', sa.String(), nullable=True),
    sa.Column('land', sa.String(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('adresse_id')
    )
    op.create_table('Netzbetreiber',
    sa.Column('user_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('Tarif',
    sa.Column('tarif_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('tarifname', sa.String(), nullable=True),
    sa.Column('preis_kwh', sa.Float(), nullable=True),
    sa.Column('grundgebuehr', sa.Float(), nullable=True),
    sa.Column('laufzeit', sa.Integer(), nullable=True),
    sa.Column('spezielle_konditionen', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('tarif_id'),
    sa.UniqueConstraint('tarifname')
    )
    op.create_table('Nutzer',
    sa.Column('user_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('nachname', sa.String(), nullable=True),
    sa.Column('vorname', sa.String(), nullable=True),
    sa.Column('geburtsdatum', sa.Date(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('passwort', sa.String(), nullable=True),
    sa.Column('rolle', sa.Enum('Haushalte', 'Solarteure', 'Energieberatende', 'Netzbetreiber', 'Admin', name='rolle'), nullable=False),
    sa.Column('telefonnummer', sa.String(), nullable=True),
    sa.Column('adresse_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['adresse_id'], ['Adresse.adresse_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('Dashboard_smartmeter_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('haushalt_id', sa.Integer(), nullable=True),
    sa.Column('datum', sa.DateTime(), nullable=True),
    sa.Column('pv_erzeugung', sa.Float(), nullable=True),
    sa.Column('soc', sa.Float(), nullable=True),
    sa.Column('batterie_leistung', sa.Float(), nullable=True),
    sa.Column('zaehler', sa.Float(), nullable=True),
    sa.Column('last', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['haushalt_id'], ['Nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Dashboard_smartmeter_data_id'), 'Dashboard_smartmeter_data', ['id'], unique=False)
    op.create_table('Energieberatende',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('spezialisierung', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('Haushalt',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('anzahl_bewohner', sa.Integer(), nullable=True),
    sa.Column('heizungsart', sa.String(), nullable=True),
    sa.Column('baujahr', sa.Integer(), nullable=True),
    sa.Column('wohnflaeche', sa.Float(), nullable=True),
    sa.Column('isolierungsqualitaet', sa.Enum('hoch', 'mittel', 'niedrig', name='isolierungsqualitaet'), nullable=True),
    sa.Column('ausrichtung_dach', sa.Enum('Nord', 'Nordost', 'Ost', 'Suedost', 'Sued', 'Suedwest', 'West', 'Nordwest', name='ausrichtungdach'), nullable=True),
    sa.Column('dachflaeche', sa.Float(), nullable=True),
    sa.Column('energieeffizienzklasse', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('PVAnlage',
    sa.Column('anlage_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('haushalt_id', sa.Integer(), nullable=True),
    sa.Column('solarteur_id', sa.Integer(), nullable=True),
    sa.Column('netzbetreiber_id', sa.Integer(), nullable=True),
    sa.Column('modultyp', sa.String(), nullable=True),
    sa.Column('kapazitaet', sa.Float(), nullable=True),
    sa.Column('installationsflaeche', sa.Float(), nullable=True),
    sa.Column('installationsdatum', sa.Date(), nullable=True),
    sa.Column('modulanordnung', sa.Enum('Nord', 'Nordost', 'Ost', 'Suedost', 'Sued', 'Suedwest', 'West', 'Nordwest', name='orientierung'), nullable=True),
    sa.Column('kabelwegfuehrung', sa.String(), nullable=True),
    sa.Column('montagesystem', sa.Enum('Aufdachmontage', 'Indachmontage', 'Flachdachmontage', 'Freilandmontage', 'Trackermontage', 'Fassadenmontage', name='montagesystem'), nullable=True),
    sa.Column('schattenanalyse', sa.Enum('Kein_Schatten', 'Minimalschatten', 'Moderater_Schatten', 'Ausgedehnter_Schatten', 'Dauerhafter_Schatten', name='schatten'), nullable=True),
    sa.Column('wechselrichterposition', sa.String(), nullable=True),
    sa.Column('installationsplan', sa.String(), nullable=True),
    sa.Column('prozess_status', sa.Enum('AnfrageGestellt', 'AngebotGemacht', 'AngebotAngenommen', 'PlanErstellt', 'Genehmigt', 'Abgenommen', 'InstallationAbgeschlossen', name='prozessstatus'), nullable=True),
    sa.Column('nvpruefung_status', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['haushalt_id'], ['Nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['netzbetreiber_id'], ['Nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['solarteur_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('anlage_id')
    )
    op.create_table('Preisstrukturen',
    sa.Column('preis_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('bezugspreis_kwh', sa.Float(), nullable=True),
    sa.Column('einspeisung_kwh', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('preis_id')
    )
    op.create_table('Rechnungen',
    sa.Column('rechnung_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('rechnungsbetrag', sa.Float(), nullable=True),
    sa.Column('rechnungsdatum', sa.Date(), nullable=True),
    sa.Column('faelligkeitsdatum', sa.Date(), nullable=True),
    sa.Column('rechnungsart', sa.Enum('Netzbetreiber_Rechnung', 'Energieberater_Rechnung', 'Solarteur_Rechnung', name='rechnungsart'), nullable=True),
    sa.Column('zeitraum', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('rechnung_id')
    )
    op.create_table('Solarteur',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['Nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('Angebote',
    sa.Column('angebot_id', sa.Integer(), nullable=False),
    sa.Column('anlage_id', sa.Integer(), nullable=True),
    sa.Column('modultyp', sa.String(), nullable=True),
    sa.Column('kapazitaet', sa.Float(), nullable=True),
    sa.Column('installationsflaeche', sa.Integer(), nullable=True),
    sa.Column('kosten', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['anlage_id'], ['PVAnlage.anlage_id'], ),
    sa.PrimaryKeyConstraint('angebot_id')
    )
    op.create_index(op.f('ix_Angebote_angebot_id'), 'Angebote', ['angebot_id'], unique=False)
    op.create_table('Vertrag',
    sa.Column('vertrag_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('haushalt_id', sa.Integer(), nullable=True),
    sa.Column('tarif_id', sa.Integer(), nullable=True),
    sa.Column('beginn_datum', sa.Date(), nullable=True),
    sa.Column('end_datum', sa.Date(), nullable=True),
    sa.Column('jahresabschlag', sa.Float(), nullable=True),
    sa.Column('vertragstatus', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['haushalt_id'], ['Haushalt.user_id'], ),
    sa.ForeignKeyConstraint(['tarif_id'], ['Tarif.tarif_id'], ),
    sa.PrimaryKeyConstraint('vertrag_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Vertrag')
    op.drop_index(op.f('ix_Angebote_angebot_id'), table_name='Angebote')
    op.drop_table('Angebote')
    op.drop_table('Solarteur')
    op.drop_table('Rechnungen')
    op.drop_table('Preisstrukturen')
    op.drop_table('PVAnlage')
    op.drop_table('Haushalt')
    op.drop_table('Energieberatende')
    op.drop_index(op.f('ix_Dashboard_smartmeter_data_id'), table_name='Dashboard_smartmeter_data')
    op.drop_table('Dashboard_smartmeter_data')
    op.drop_table('Nutzer')
    op.drop_table('Tarif')
    op.drop_table('Netzbetreiber')
    op.drop_table('Adresse')
    # ### end Alembic commands ###
