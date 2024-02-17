from truera.protobuf.public import metadata_message_types_pb2 as md_pb
from truera.protobuf.useranalytics import \
    analytics_event_schema_pb2 as analytics_event_schema_pb


def buildDeleteProjectEventProperties(
    workspace: str, command: str, project_name: str, is_recursive: bool
):
    return analytics_event_schema_pb.StructuredEventProperties(
        delete_project_event_properties=analytics_event_schema_pb.
        DeleteProjectEventProperties(
            workspace=workspace,
            project_name=project_name,
            command=command,
            is_recursive=str(is_recursive)
        )
    )


def buildDeleteModelEventProperties(
    workspace: str, command: str, model_name: str
):
    return analytics_event_schema_pb.StructuredEventProperties(
        delete_model_event_properties=analytics_event_schema_pb.
        DeleteModelEventProperties(
            workspace=workspace, command=command, model_name=model_name
        )
    )


def buildDeleteDataCollectionProperties(
    workspace: str, command: str, data_collection_name: str
):
    return analytics_event_schema_pb.StructuredEventProperties(
        delete_data_collection_event_properties=analytics_event_schema_pb.
        DeleteDataCollectionEventProperties(
            workspace=workspace,
            command=command,
            data_collection_name=data_collection_name
        )
    )


def buildDeleteDataSplitProperties(
    workspace: str, command: str, data_split_name: str
):
    return analytics_event_schema_pb.StructuredEventProperties(
        delete_data_split_event_properties=analytics_event_schema_pb.
        DeleteDataSplitEventProperties(
            workspace=workspace,
            command=command,
            data_split_name=data_split_name
        )
    )


def buildAddProjectEventProperties(
    workspace: str, command: str, project_name: str
):
    return analytics_event_schema_pb.StructuredEventProperties(
        add_project_event_properties=analytics_event_schema_pb.
        AddProjectEventProperties(
            workspace=workspace, project_name=project_name, command=command
        )
    )


def buildAddFeatureListEventProperties(workspace: str, feature_list_id: str):
    return analytics_event_schema_pb.StructuredEventProperties(
        add_feature_list_event_properties=analytics_event_schema_pb.
        AddFeatureListEventProperties(
            workspace=workspace,
            feature_list_id=feature_list_id
            if feature_list_id is not None else ""
        )
    )


def buildAddDataSourceEventProperties(
    workspace: str, command: str, data_source_name: str
):
    return analytics_event_schema_pb.StructuredEventProperties(
        modify_data_source_event_properties=analytics_event_schema_pb.
        ModifyDataSourceEventProperties(
            workspace="remote",
            command="add_data_source",
            data_source_name=data_source_name
        )
    )


def buildModifyCacheEventProperties(
    workspace: str, score_type: str, insert_only: bool, cache_type: any
):
    if cache_type == md_pb.CacheType.EXPLANATION_CACHE:
        command = "add_prediction_cache" if insert_only else "update_prediction_cache"
        return analytics_event_schema_pb.StructuredEventProperties(
            modify_prediction_cache_event_properties=analytics_event_schema_pb.
            ModifyPredictionCacheEventProperties(
                workspace=workspace, command=command, score_type=score_type
            )
        )
    else:
        command = "add_explaination_cache" if insert_only else "update_explaination_cache"
        return analytics_event_schema_pb.StructuredEventProperties(
            modify_explanation_cache_event_properties=analytics_event_schema_pb.
            ModifyExplanationCacheEventProperties(
                workspace=workspace, command=command, score_type=score_type
            )
        )


def buildModifyModelEventProperties(
    workspace: str, model_name: str, insert_only: bool
):
    if insert_only:
        return analytics_event_schema_pb.StructuredEventProperties(
            add_model_event_properties=analytics_event_schema_pb.
            AddModelEventProperties(
                workspace=workspace, command="add_model", model_name=model_name
            )
        )
    else:
        return analytics_event_schema_pb.StructuredEventProperties(
            update_model_event_properties=analytics_event_schema_pb.
            UpdateModelEventProperties(
                workspace=workspace,
                command="update_model",
                model_name=model_name
            )
        )


def buildModifyDataCollectionEventProperties(
    workspace: str, data_collection_name: str, insert_only: bool
):
    if insert_only:
        return analytics_event_schema_pb.StructuredEventProperties(
            add_data_collection_event_properties=analytics_event_schema_pb.
            AddDataCollectionEventProperties(
                workspace=workspace,
                command="add_data_collection",
                data_collection_name=data_collection_name
            )
        )
    else:
        return analytics_event_schema_pb.StructuredEventProperties(
            update_data_collection_event_properties=analytics_event_schema_pb.
            UpdateDataCollectionEventProperties(
                workspace=workspace,
                command="update_data_collection",
                data_collection_name=data_collection_name
            )
        )


def buildModifyDataSplitEventProperties(
    workspace: str, data_split_name: str, insert_only: bool
):
    if insert_only:
        return analytics_event_schema_pb.StructuredEventProperties(
            add_data_split_event_properties=analytics_event_schema_pb.
            AddDataSplitEventProperties(
                workspace=workspace,
                command="add_data_split",
                data_split_name=data_split_name
            )
        )
    else:
        return analytics_event_schema_pb.StructuredEventProperties(
            update_data_split_event_properties=analytics_event_schema_pb.
            UpdateDataSplitEventProperties(
                workspace=workspace,
                command="update_data_split",
                data_split_name=data_split_name
            )
        )


def buildModifyReportEventProperties(report_title: str, insert_only: bool):
    if insert_only:
        return analytics_event_schema_pb.StructuredEventProperties(
            add_report_event_properties=analytics_event_schema_pb.
            AddReportEventProperties(report_title=report_title)
        )
    else:
        return analytics_event_schema_pb.StructuredEventProperties(
            update_report_event_properties=analytics_event_schema_pb.
            UpdateReportEventProperties(report_title=report_title)
        )


def buildDeleteReportEventProperties(report_title: str):
    return analytics_event_schema_pb.StructuredEventProperties(
        delete_report_event_properties=analytics_event_schema_pb.
        DeleteReportEventProperties(report_title=report_title)
    )
