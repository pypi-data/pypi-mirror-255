from chaiverse.lib import binomial_tools


def get_metrics_from_submission(submission):
    double_thumbs_up =  submission.get('double_thumbs_up', 0)
    thumbs_up = submission['thumbs_up']
    thumbs_down = submission['thumbs_down']
    submission_feedback_total = double_thumbs_up + thumbs_up + thumbs_down

    metrics = {
        'thumbs_up_ratio': binomial_tools.get_ratio(thumbs_up, thumbs_down + double_thumbs_up),
        'thumbs_up_ratio_se': binomial_tools.get_ratio_se(thumbs_up, thumbs_down + double_thumbs_up),
        'double_thumbs_up_ratio': binomial_tools.get_ratio(double_thumbs_up, thumbs_down + thumbs_up),
        'double_thumbs_up_ratio_se': binomial_tools.get_ratio_se(double_thumbs_up, thumbs_down + thumbs_up),
        'total_feedback_count': submission_feedback_total,
    }
    return metrics