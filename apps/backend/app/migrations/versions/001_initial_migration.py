"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create games table
    op.create_table('games',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('site', sa.String(length=20), nullable=False),
        sa.Column('pgn', sa.Text(), nullable=False),
        sa.Column('json', sa.JSON(), nullable=True),
        sa.Column('eco', sa.String(length=10), nullable=True),
        sa.Column('opening', sa.String(length=200), nullable=True),
        sa.Column('result', sa.Enum('WHITE_WINS', 'BLACK_WINS', 'DRAW', name='gameresult'), nullable=True),
        sa.Column('time_control', sa.String(length=50), nullable=True),
        sa.Column('white', sa.String(length=100), nullable=True),
        sa.Column('black', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_games_username'), 'games', ['username'], unique=False)
    op.create_index(op.f('ix_games_eco'), 'games', ['eco'], unique=False)

    # Create moves table
    op.create_table('moves',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ply', sa.Integer(), nullable=False),
        sa.Column('fen', sa.String(length=100), nullable=False),
        sa.Column('san', sa.String(length=20), nullable=False),
        sa.Column('side', sa.Enum('WHITE', 'BLACK', name='side'), nullable=False),
        sa.Column('time_left_ms', sa.Integer(), nullable=True),
        sa.Column('sf_eval_cp', sa.Integer(), nullable=True),
        sa.Column('sf_mate', sa.Integer(), nullable=True),
        sa.Column('sf_bestmove_uci', sa.String(length=10), nullable=True),
        sa.Column('sf_pv', sa.Text(), nullable=True),
        sa.Column('mistake_tag', sa.Enum('NONE', 'INACCURACY', 'MISTAKE', 'BLUNDER', name='mistaketype'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moves_game_id'), 'moves', ['game_id'], unique=False)

    # Create features table
    op.create_table('features',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('counts_by_motif', sa.JSON(), nullable=True),
        sa.Column('blunder_rate_by_phase', sa.JSON(), nullable=True),
        sa.Column('time_profile', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id')
    )

    # Create neighbors table
    op.create_table('neighbors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('move_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ref_game_id', sa.String(length=50), nullable=False),
        sa.Column('ref_ply', sa.Integer(), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=False),
        sa.Column('human_choice_san', sa.String(length=20), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['move_id'], ['moves.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_neighbors_move_id'), 'neighbors', ['move_id'], unique=False)

    # Create puzzles table
    op.create_table('puzzles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_move_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fen_start', sa.String(length=100), nullable=False),
        sa.Column('solution_san', sa.JSON(), nullable=False),
        sa.Column('motif', sa.String(length=50), nullable=True),
        sa.Column('strength', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
        sa.ForeignKeyConstraint(['source_move_id'], ['moves.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create analysis_jobs table
    op.create_table('analysis_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=True),
        sa.Column('processed_items', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_jobs_username'), 'analysis_jobs', ['username'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_analysis_jobs_username'), table_name='analysis_jobs')
    op.drop_table('analysis_jobs')
    op.drop_table('puzzles')
    op.drop_index(op.f('ix_neighbors_move_id'), table_name='neighbors')
    op.drop_table('neighbors')
    op.drop_table('features')
    op.drop_index(op.f('ix_moves_game_id'), table_name='moves')
    op.drop_table('moves')
    op.drop_index(op.f('ix_games_eco'), table_name='games')
    op.drop_index(op.f('ix_games_username'), table_name='games')
    op.drop_table('games')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS gameresult')
    op.execute('DROP TYPE IF EXISTS side')
    op.execute('DROP TYPE IF EXISTS mistaketype')

