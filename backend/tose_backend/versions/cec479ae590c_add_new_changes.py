"""Add new changes

Revision ID: cec479ae590c
Revises: 
Create Date: 2023-12-27 16:22:24.301152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cec479ae590c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('adresse',
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
    op.create_table('netzbetreiber',
    sa.Column('user_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('nutzer',
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
    sa.ForeignKeyConstraint(['adresse_id'], ['adresse.adresse_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('dashboard_smartmeter_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('haushalt_id', sa.Integer(), nullable=True),
    sa.Column('datum', sa.DateTime(), nullable=True),
    sa.Column('pv_erzeugung', sa.Float(), nullable=True),
    sa.Column('soc', sa.Float(), nullable=True),
    sa.Column('batterie_leistung', sa.Float(), nullable=True),
    sa.Column('zaehler', sa.Float(), nullable=True),
    sa.Column('last', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['haushalt_id'], ['nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboard_smartmeter_data_id'), 'dashboard_smartmeter_data', ['id'], unique=False)
    op.create_table('energieausweise',
    sa.Column('energieausweis_id', sa.Integer(), nullable=False),
    sa.Column('haushalt_id', sa.Integer(), nullable=False),
    sa.Column('massnahmen_id', sa.Integer(), nullable=True),
    sa.Column('energieberater_id', sa.Integer(), nullable=True),
    sa.Column('energieeffizienzklasse', sa.String(), nullable=True),
    sa.Column('verbrauchskennwerte', sa.Float(), nullable=True),
    sa.Column('ausstellungsdatum', sa.Date(), nullable=True),
    sa.Column('gueltigkeit', sa.Date(), nullable=True),
    sa.Column('ausweis_status', sa.Enum('AnfrageGestellt', 'Ausgestellt', name='ausweisstatus'), nullable=False),
    sa.ForeignKeyConstraint(['energieberater_id'], ['nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['haushalt_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('energieausweis_id')
    )
    op.create_table('energieberatende',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('spezialisierung', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('haushalte',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('anzahl_bewohner', sa.Integer(), nullable=True),
    sa.Column('heizungsart', sa.String(), nullable=True),
    sa.Column('baujahr', sa.Integer(), nullable=True),
    sa.Column('wohnflaeche', sa.Float(), nullable=True),
    sa.Column('isolierungsqualitaet', sa.Enum('hoch', 'mittel', 'niedrig', name='isolierungsqualitaet'), nullable=True),
    sa.Column('ausrichtung_dach', sa.Enum('Nord', 'Nordost', 'Ost', 'Suedost', 'Sued', 'Suedwest', 'West', 'Nordwest', name='orientierung'), nullable=True),
    sa.Column('dachflaeche', sa.Float(), nullable=True),
    sa.Column('energieeffizienzklasse', sa.String(), nullable=True),
    sa.Column('anfragestatus', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('kalendereintraege',
    sa.Column('kalender_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('zeitpunkt', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('beschreibung', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('kalender_id')
    )
    op.create_table('preisstrukturen',
    sa.Column('preis_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('bezugspreis_kwh', sa.Float(), nullable=True),
    sa.Column('einspeisung_kwh', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('preis_id')
    )
    op.create_table('pvanlage',
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
    sa.Column('prozess_status', sa.Enum('AnfrageGestellt', 'DatenAngefordert', 'DatenFreigegeben', 'AngebotGemacht', 'AngebotAngenommen', 'PlanErstellt', 'Genehmigt', 'Abgenommen', 'InstallationAbgeschlossen', name='prozessstatus'), nullable=True),
    sa.Column('nvpruefung_status', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['haushalt_id'], ['nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['netzbetreiber_id'], ['nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['solarteur_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('anlage_id')
    )
    op.create_table('rechnungen',
    sa.Column('rechnung_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('rechnungsbetrag', sa.Float(), nullable=True),
    sa.Column('rechnungsdatum', sa.Date(), nullable=True),
    sa.Column('faelligkeitsdatum', sa.Date(), nullable=True),
    sa.Column('rechnungsart', sa.Enum('Netzbetreiber_Rechnung', 'Energieberater_Rechnung', 'Solarteur_Rechnung', name='rechnungsart'), nullable=True),
    sa.Column('zeitraum', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('rechnung_id')
    )
    op.create_table('solarteur',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('tarif',
    sa.Column('tarif_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('tarifname', sa.String(), nullable=True),
    sa.Column('preis_kwh', sa.Float(), nullable=True),
    sa.Column('grundgebuehr', sa.Float(), nullable=True),
    sa.Column('laufzeit', sa.Integer(), nullable=True),
    sa.Column('spezielle_konditionen', sa.String(), nullable=True),
    sa.Column('netzbetreiber_id', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['netzbetreiber_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('tarif_id'),
    sa.UniqueConstraint('tarifname')
    )
    op.create_table('angebote',
    sa.Column('angebot_id', sa.Integer(), nullable=False),
    sa.Column('anlage_id', sa.Integer(), nullable=True),
    sa.Column('kosten', sa.Float(), nullable=True),
    sa.Column('angebotsstatus', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['anlage_id'], ['pvanlage.anlage_id'], ),
    sa.PrimaryKeyConstraint('angebot_id')
    )
    op.create_index(op.f('ix_angebote_angebot_id'), 'angebote', ['angebot_id'], unique=False)
    op.create_table('vertrag',
    sa.Column('vertrag_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('tarif_id', sa.Integer(), nullable=True),
    sa.Column('beginn_datum', sa.Date(), nullable=True),
    sa.Column('end_datum', sa.Date(), nullable=True),
    sa.Column('netzbetreiber_id', sa.Integer(), nullable=True),
    sa.Column('jahresabschlag', sa.Float(), nullable=True),
    sa.Column('vertragstatus', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['netzbetreiber_id'], ['nutzer.user_id'], ),
    sa.ForeignKeyConstraint(['tarif_id'], ['tarif.tarif_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['nutzer.user_id'], ),
    sa.PrimaryKeyConstraint('vertrag_id'),
    sa.UniqueConstraint('user_id', 'tarif_id', name='_user_id_tarif_id_uc')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vertrag')
    op.drop_index(op.f('ix_angebote_angebot_id'), table_name='angebote')
    op.drop_table('angebote')
    op.drop_table('tarif')
    op.drop_table('solarteur')
    op.drop_table('rechnungen')
    op.drop_table('pvanlage')
    op.drop_table('preisstrukturen')
    op.drop_table('kalendereintraege')
    op.drop_table('haushalte')
    op.drop_table('energieberatende')
    op.drop_table('energieausweise')
    op.drop_index(op.f('ix_dashboard_smartmeter_data_id'), table_name='dashboard_smartmeter_data')
    op.drop_table('dashboard_smartmeter_data')
    op.drop_table('nutzer')
    op.drop_table('netzbetreiber')
    op.drop_table('adresse')
    # ### end Alembic commands ###