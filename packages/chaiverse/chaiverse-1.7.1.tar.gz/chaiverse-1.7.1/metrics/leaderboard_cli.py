__all__ = ["display_leaderboard", "display_competition_leaderboard"]

from typing import Optional
import warnings

import pandas as pd
from tabulate import tabulate

from chaiverse.competition_cli import get_competitions
from chaiverse import constants
from chaiverse.metrics.leaderboard_formatter import format_leaderboard
from chaiverse.metrics.leaderboard_api import get_leaderboard
from chaiverse.schemas import Competition
from chaiverse.utils import print_color, cache

pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)
pd.set_option("display.colheader_justify","center")

warnings.filterwarnings('ignore', 'Mean of empty slice')


def display_leaderboard(
    developer_key=None,
    regenerate=False,
    detailed=False,
    max_workers=constants.DEFAULT_MAX_WORKERS,
):
    default_competition = Competition(
        competition_id='Default',
        leaderboard_format='meval',
    )

    df = display_competition_leaderboard(
        competition=default_competition,
        detailed=detailed,
        regenerate=regenerate,
        developer_key=developer_key,
        max_workers=max_workers,
    )
    return df


def display_competition_leaderboard(
    competition:Optional[Competition]=None,
    detailed=False,
    regenerate=False, 
    developer_key=None,
    max_workers=constants.DEFAULT_MAX_WORKERS
):
    competition = competition if competition else get_competitions()[-1]
    leaderboard_format = competition.leaderboard_format or 'meval'
    fetch_feedback = competition.leaderboard_should_use_feedback

    submission_date_range = competition.submission_date_range
    evaluation_date_range = competition.evaluation_date_range
    submission_ids = competition.enrolled_submission_ids
    competition_id = competition.competition_id
    title_prefix = 'Detailed ' if detailed else ''
    display_title = f'{title_prefix}{competition_id} Leaderboard'

    df = cache(get_leaderboard, regenerate)(
        developer_key=developer_key,
        max_workers=max_workers,
        submission_date_range=submission_date_range,
        evaluation_date_range=evaluation_date_range,
        submission_ids=submission_ids,
        fetch_feedback=fetch_feedback
        )

    if len(df) > 0:
        display_df = df.copy()
        display_df = format_leaderboard(
            display_df, 
            detailed=detailed, 
            format=leaderboard_format
        )
        _pprint_leaderboard(display_df, display_title)
    else:
        print('No eligible submissions found!')
    return df


def _pprint_leaderboard(df, title):
    print_color(f'\n💎 {title}:', 'red')
    print(tabulate(df.round(3).head(30), headers=df.columns, numalign='decimal'))

