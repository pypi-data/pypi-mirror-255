import os


DEFAULT_MAX_WORKERS = 1


PUBLIC_LEADERBOARD_MINIMUM_FEEDBACK_COUNT = 0


LEADERBOARD_FORMAT_CONFIGS = {}


LEADERBOARD_INDIVIDUAL_RANK_PARAMS = [
    dict(value_column='stay_in_character', rank_column='stay_in_character_rank', ascending=False),
    dict(value_column='user_preference', rank_column='user_preference_rank', ascending=False),
    dict(value_column='entertaining', rank_column='entertaining_rank', ascending=False),
    dict(value_column='double_thumbs_up_ratio', rank_column='double_thumbs_up_rank', ascending=False),
    dict(value_column='elo_rating', rank_column='elo_rank', ascending=False),
]


LEADERBOARD_OVERALL_RANK_PARAMS = [
    dict(
        from_rank_columns=['stay_in_character_rank', 'user_preference_rank', 'entertaining_rank'],
        overall_score_column='overall_meval_score', overall_rank_column='overall_meval_rank'
    ),
    dict(
        from_rank_columns=['elo_rank', 'double_thumbs_up_rank'],
        overall_score_column='overall_user_score', overall_rank_column='overall_user_rank'
    ),
]


LEADERBOARD_FORMAT_CONFIGS['meval'] = {
    "output_columns": [
        'developer_uid',
        'model_name',
        'is_custom_reward',
        'stay_in_character',
        'user_preference',
        'entertaining',
        'safety_score',
        "overall_meval_score",
        'elo_rating',
        'num_battles',
        'num_wins',
        'thumbs_up_ratio',
        'double_thumbs_up_ratio',
        'size',
        'status',
        'submission_id',
    ],
    "sort_params": {
        "by": "overall_meval_score",
        "ascending": True
    },
}


LEADERBOARD_FORMAT_CONFIGS['thumbs_up'] = {
    "output_columns": [
        'developer_uid',
        'model_name',
        'double_thumbs_up_ratio',
        'elo_rating',
        'num_battles',
        'num_wins',
        'thumbs_up_ratio',
        'total_feedback_count',
        'overall_user_rank',
        'stay_in_character',
        'user_preference',
        'entertaining',
        'safety_score',
        'repetition',
        'is_custom_reward',
        'submission_id',
        'size',
    ],
    "sort_params": {
        "by": "double_thumbs_up_ratio",
        "ascending": False
    }
}

LEADERBOARD_FORMAT_CONFIGS['user'] = {
    "output_columns": [
        'developer_uid',
        'model_name',
        'double_thumbs_up_ratio',
        'elo_rating',
        'double_thumbs_up_rank',
        'elo_rank',
        'overall_user_score',
        'num_battles',
        'num_wins',
        'thumbs_up_ratio',
        'double_thumbs_up',
        'thumbs_up',
        'total_feedback_count',
        'stay_in_character',
        'user_preference',
        'entertaining',
        'safety_score',
        'is_custom_reward',
        'submission_id',
        'size',
    ],
    "sort_params": {
        "by": "overall_user_score",
        "ascending": True
    }
}
