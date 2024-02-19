__all__ = ["display_leaderboard", "display_competition_leaderboard"]

from typing import Optional
import warnings

import pandas as pd
from tabulate import tabulate

from chaiverse.competition_cli import get_competitions
from chaiverse import constants
from chaiverse.metrics.leaderboard_formatter import format_leaderboard
from chaiverse.metrics.leaderboard_api import get_leaderboard
from chaiverse.schemas import Competition, DateRange
from chaiverse.utils import print_color, cache

pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 500)
pd.set_option("display.colheader_justify","center")

warnings.filterwarnings('ignore', 'Mean of empty slice')


DEFAULT_COMPETITION = Competition(
    display_name='Default',
    leaderboard_format='meval'
)


def display_leaderboard(
    developer_key=None,
    regenerate=False,
    detailed=False,
    max_workers=constants.DEFAULT_MAX_WORKERS,
    leaderboard_format=None
):
    df = display_competition_leaderboard(
        competition=DEFAULT_COMPETITION,
        detailed=detailed,
        regenerate=regenerate,
        developer_key=developer_key,
        max_workers=max_workers,
        leaderboard_format=leaderboard_format
    )
    return df


def display_competition_leaderboard(
    competition:Optional[Competition]=None,
    detailed=False,
    regenerate=False, 
    developer_key=None,
    max_workers=constants.DEFAULT_MAX_WORKERS,
    leaderboard_format=None
):
    competition = competition if competition else get_competitions()[-1]
    leaderboard_format = competition.leaderboard_format or 'user' if leaderboard_format is None else leaderboard_format
    fetch_feedback = competition.leaderboard_should_use_feedback

    submission_date_range = competition.submission_date_range
    evaluation_date_range = competition.evaluation_date_range
    submission_ids = competition.enrolled_submission_ids
    display_name = competition.display_name
    title_prefix = 'Detailed ' if detailed else ''
    sort_by = constants.LEADERBOARD_FORMAT_CONFIGS[leaderboard_format]['sort_params']['by']
    display_title = f'{title_prefix}{display_name} Leaderboard (sorted by {sort_by})'

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

