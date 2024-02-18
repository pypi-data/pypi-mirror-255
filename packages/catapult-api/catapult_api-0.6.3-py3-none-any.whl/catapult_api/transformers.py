import json

import numpy as np
import pandas as pd


def extract_parameters(parameters, parameter_names):
    parameters_slug = []
    for name in parameter_names:
        for param in parameters:
            if param["name"] == name:
                parameters_slug.append(param["slug"])
    return parameters_slug


def transform_activities(activities: dict, activity_tags: list = None) -> pd.DataFrame:
    df_activities = pd.DataFrame(activities)

    df_activities["venue"] = df_activities["venue"].apply(json.dumps)
    df_activities["owner"] = df_activities["owner"].apply(json.dumps)
    df_activities["tag_list"] = df_activities["tag_list"].apply(lambda x: json.dumps(x))
    df_activities["periods"] = df_activities["periods"].apply(lambda x: json.dumps(x))

    df_activity_tags = pd.json_normalize(
        activities,
        record_path=["tag_list"],
        record_prefix="tag_",
        meta=["id", "name"],
        meta_prefix="activity_",
    )
    df_activity_tags_wide = df_activity_tags.pivot_table(
        index="activity_id",
        columns=["tag_tag_type_name"],
        values="tag_name",
        aggfunc="first",
    )
    if activity_tags:
        df_activity_tags_wide = (
            df_activity_tags_wide.reindex(columns=activity_tags)
            .fillna(np.nan)
            .reset_index()
        )
    df_activities_final = df_activities.merge(
        df_activity_tags_wide, how="left", left_on="id", right_on="activity_id"
    )
    return df_activities_final


def transform_periods(periods: dict, period_tags: list = None):
    df_periods = pd.DataFrame(periods)

    df_periods["tags"] = df_periods["tags"].apply(lambda x: json.dumps(x))

    df_period_tags = pd.json_normalize(
        periods,
        record_path=["tags"],
        record_prefix="tag_",
        meta=["id", "name"],
        meta_prefix="period_",
    )
    df_period_tags_wide = df_period_tags.pivot_table(
        index="period_id",
        columns=["tag_tag_type_name"],
        values="tag_name",
        aggfunc="first",
    )
    if period_tags:
        df_period_tags_wide = (
            df_period_tags_wide.reindex(columns=period_tags)
            .fillna(np.nan)
            .reset_index()
        )
    df_periods_final = df_periods.merge(
        df_period_tags_wide, how="left", left_on="id", right_on="period_id"
    )
    return df_periods_final


def transform_athletes_in_activity(
    athletes_in_activity: dict, activity_id: str, athlete_activity_tags: list = None
):
    df_athletes_in_activity = pd.DataFrame(athletes_in_activity)

    tags_bool = (
        df_athletes_in_activity["tags"].apply(lambda x: False if x else True).tolist()
    )
    if True in tags_bool:
        return df_athletes_in_activity

    df_athletes_in_activity["tags"] = df_athletes_in_activity["tags"].apply(
        lambda x: json.dumps(x)
    )

    df_athlete_activity_tags = pd.json_normalize(
        athletes_in_activity,
        record_path=["tags"],
        record_prefix="tag_",
        meta="id",
        meta_prefix="athlete_",
    )
    df_athlete_activity_tags_wide = df_athlete_activity_tags.pivot_table(
        index="athlete_id",
        columns=["tag_tag_type_name"],
        values="tag_name",
        aggfunc="first",
    )
    if athlete_activity_tags:
        df_athlete_activity_tags_wide = (
            df_athlete_activity_tags_wide.reindex(columns=athlete_activity_tags)
            .fillna(np.nan)
            .reset_index()
        )
    df_athletes_in_activity_final = df_athletes_in_activity.merge(
        df_athlete_activity_tags_wide, how="left", left_on="id", right_on="athlete_id"
    )
    df_athletes_in_activity_final["activity_id"] = activity_id

    return df_athletes_in_activity_final
