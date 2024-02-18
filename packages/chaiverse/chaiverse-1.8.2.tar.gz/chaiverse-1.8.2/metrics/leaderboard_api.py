__all__ = ["get_leaderboard"]


import numpy as np
import pandas as pd

from chaiverse.utils import get_submissions, distribute_to_workers
from chaiverse.metrics.feedback_metrics import get_metrics_from_feedback
from chaiverse.metrics.submission_metrics import get_metrics_from_submission
from chaiverse import constants, feedback


def get_leaderboard(
        developer_key=None,
        max_workers=constants.DEFAULT_MAX_WORKERS,
        submission_date_range=None,
        evaluation_date_range=None,
        submission_ids=None,
        fetch_feedback=False,
        ):
    submissions = get_submissions(developer_key, submission_date_range)
    submissions = _filter_submissions_by_submission_ids(submissions, submission_ids) if submission_ids != None else submissions
    submissions = _filter_submissions_by_feedback_count(submissions, constants.PUBLIC_LEADERBOARD_MINIMUM_FEEDBACK_COUNT)
    df = distribute_to_workers(
        get_leaderboard_row,
        submissions.items(),
        developer_key=developer_key,
        evaluation_date_range=evaluation_date_range,
        max_workers=max_workers,
        fetch_feedback=fetch_feedback
    )
    df = pd.DataFrame(df)
    if len(df):
        df = _get_filled_leaderboard(df)
        df.index = np.arange(1, len(df)+1)
    return df


def get_leaderboard_row(submission_item, developer_key=None, evaluation_date_range=None, fetch_feedback=False):
    submission_id, submission_data = submission_item
    if fetch_feedback:
        submission_feedback_total = submission_data.get('double_thumbs_up', 0) + submission_data['thumbs_up'] + submission_data['thumbs_down']
        is_updated = feedback.is_submission_updated(submission_id, submission_feedback_total)
        metrics = get_metrics_from_feedback(
            submission_id, 
            developer_key, 
            reload=is_updated, 
            evaluation_date_range=evaluation_date_range
        )
    else:
        metrics = get_metrics_from_submission(submission_data) 
    return {'submission_id': submission_id, **submission_data, **metrics}


def _get_filled_leaderboard(df):
    # maintain backwards compatibility with model_name field
    _fill_default_value(df, 'model_name', df['submission_id'])
    _fill_default_value(df, 'is_custom_reward', False)
    for col in _get_filled_columns():
        _fill_default_value(df, col, None)
    return df


def _get_filled_columns():
    columns = []
    for leaderboard_format in constants.LEADERBOARD_FORMAT_CONFIGS.keys():
        new_columns = constants.LEADERBOARD_FORMAT_CONFIGS[leaderboard_format]['output_columns']
        columns.extend(new_columns)
    return columns


def _fill_default_value(df, field, default_value):
    if field not in df:
        df[field] = None
    if default_value is not None:
        df[field] = df[field].fillna(default_value)


def _filter_submissions_by_submission_ids(submissions, submission_ids):
    filtered_submissions = {
        submission_id: data
        for submission_id, data in submissions.items()
        if submission_id in submission_ids
    }
    return filtered_submissions


def _filter_submissions_by_feedback_count(submissions, min_feedback_count):
    submissions = {
        submission_id: submission_data for submission_id, submission_data in submissions.items()
        if submission_data.get('double_thumbs_up', 0) + submission_data['thumbs_up'] + submission_data['thumbs_down'] >= min_feedback_count
    }
    return submissions
