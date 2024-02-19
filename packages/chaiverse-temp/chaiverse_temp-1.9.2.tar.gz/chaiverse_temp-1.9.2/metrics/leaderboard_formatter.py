__all__ = ["format_leaderboard"]


from datetime import datetime

import numpy as np

from chaiverse import constants


def format_leaderboard(df, detailed, format):
    if len(df) > 0:
        competition_configuration = constants.LEADERBOARD_FORMAT_CONFIGS[format]
        sort_params = competition_configuration['sort_params']
        output_columns = competition_configuration['output_columns']
        for individual_rank_param in constants.LEADERBOARD_INDIVIDUAL_RANK_PARAMS:
            df = _add_individual_rank(df, **individual_rank_param)
        for overall_rank_param in constants.LEADERBOARD_OVERALL_RANK_PARAMS:
            df = _add_overall_rank(df, **overall_rank_param)
        df = _sort(df, sort_params)
        df = df if detailed else _get_deduped_leaderboard(df)
        df = _get_formatted_leaderboard(df)
        df = df if detailed else df[output_columns]
        df.index = np.arange(1, len(df)+1)
    return df


def _get_deduped_leaderboard(df):
    df = _get_submissions_with_unique_model(df)
    df = _get_submissions_with_unique_dev_id(df)
    return df


def _get_formatted_leaderboard(df):
    df['timestamp'] = df.timestamp.apply(_get_isoformatted_timestamp)
    df['size'] = df.model_num_parameters.apply(_get_model_size)
    df['date'] = df['timestamp'].dt.date
    df.drop(['timestamp'], axis=1, inplace=True)
    df['is_custom_reward'] = df['is_custom_reward'].replace({
        True: '✅',
        False: '❌'
    })
    df = df.reset_index(drop=True)
    return df


def _get_isoformatted_timestamp(timestamp):
    formatted = datetime.fromisoformat(timestamp)
    return formatted


def _get_model_size(num_parameters):
    size = 'n/a'
    if num_parameters is not None and not np.isnan(num_parameters):
        size = f'{int(round(num_parameters/1e9,0))}'
    return size


def _get_submissions_with_unique_model(df):
    df = df.drop_duplicates(subset=['developer_uid', 'model_repo', 'reward_repo'], keep='first')
    return df


def _get_submissions_with_unique_dev_id(df):
    out = df.drop_duplicates('developer_uid', keep='first')
    return out


def _add_individual_rank(df, value_column, rank_column, ascending=True):
    df[rank_column] = df[value_column].rank(ascending=ascending, na_option='bottom')
    return df


def _add_overall_rank(df, overall_rank_column, overall_score_column, from_rank_columns):
    ranks = [df[column] for column in from_rank_columns]
    overall_score = np.mean(ranks, axis=0)
    df.loc[:, overall_score_column] = overall_score
    df.loc[:, overall_rank_column] = df[overall_score_column].rank(na_option='bottom')
    return df


def _sort(df, sort_params):
    df = df.sort_values(**sort_params, na_position='last').reset_index(drop=True)
    return df
