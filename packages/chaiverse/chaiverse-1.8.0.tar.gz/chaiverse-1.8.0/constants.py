import os


DEFAULT_MAX_WORKERS = 1


PUBLIC_LEADERBOARD_MINIMUM_FEEDBACK_COUNT = 0


MODEL_EVAL_SCORE_COLS = ['stay_in_character', 'user_preference', 'entertaining']


LEADERBOARD_FORMAT_CONFIGS = {}


LEADERBOARD_FORMAT_CONFIGS['meval'] = {
    "output_columns": [
        'developer_uid',
        'model_name',
        'is_custom_reward',
        'stay_in_character',
        'user_preference',
        'entertaining',
        'safety_score',
        "overall_rank",
        'elo_rating',
        'num_battles',
        'num_wins',
        'thumbs_up_ratio',
        'size',
        'status',
        'submission_id',
    ],
    "sort_params": {
        "by": "overall_score",
        "ascending": True
    }
}


LEADERBOARD_FORMAT_CONFIGS['thumbs_up'] = {
    "output_columns": [
        'developer_uid',
        'model_name',
        'thumbs_up_ratio',
        'overall_rank',
        'total_feedback_count',
        'repetition',
        'stay_in_character',
        'user_preference',
        'entertaining',
        'safety_score',
        'is_custom_reward',
        'submission_id',
        'size',
    ],
    "sort_params": {
        "by": "thumbs_up_ratio",
        "ascending": False
    }
}
