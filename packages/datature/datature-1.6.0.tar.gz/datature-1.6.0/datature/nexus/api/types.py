#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   types.py
@Author  :   Raighne.Weng
@Version :   1.6.0
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Types for Datature API resources.
'''
# pylint: disable=R0902,C0103,W0212

from typing import Union, List
from enum import Enum, unique
from dataclasses import dataclass


def add_mapping(enum_cls):
    """Add Mapping to Type."""

    for key, value in enum_cls.__MAPPING__.items():
        enum_cls._member_map_[key] = value
    return enum_cls


@dataclass
class ProjectMetadata:
    """Project metadata.

    :param name: The name of the project.
    """

    name: str

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {
            "name": self.name,
        }


@add_mapping
@unique
class BoundType(Enum):
    """Bound Type.

    Bound Type Options:
        Rectangle
        Polygon
        Classification
        Keypoints
    """

    POLYGON = "Polygon"
    RECTANGLE = "Rectangle"
    CLASSIFICATION = "Classification"
    KEYPOINTS = "Keypoints"

    __MAPPING__ = {
        "Polygon": POLYGON,
        "Rectangle": RECTANGLE,
        "Classification": CLASSIFICATION,
        "Keypoints": KEYPOINTS,
    }


@add_mapping
@unique
class AnnotationExportFormat(Enum):
    """Annotation Export CSV Format.

    Bounding Box Options:
        coco
        csv_fourcorner
        csv_widthheight
        pascal_voc
        yolo_darknet
        yolo_keras_pytorch
        createml
        tfrecord

    Polygon Options:
        polygon_single
        polygon_coco

    Classification Options:
        csv_classification
        classification_tfrecord

    Key Point Options:
        keypoints_coco
    """

    COCO = "coco"
    CSV_FOURCORNER = "csv_fourcorner"
    CSV_WIDTHHEIGHT = "csv_widthheight"
    PASCAL_VOC = "pascal_voc"
    YOLO_DARKNET = "yolo_darknet"
    YOLO_KERAS_PYTORCH = "yolo_keras_pytorch"
    CREATEML = "createml"
    TFRECORD = "tfrecord"
    POLYGON_COCO = "polygon_coco"
    POLYGON_SINGLE = "polygon_single"
    CSV_CLASSIFICATION = "csv_classification"
    CLASSIFICATION_TFRECORD = "classification_tfrecord"
    KEYPOINTS_COCO = "keypoints_coco"

    __MAPPING__ = {
        "coco": COCO,
        "csv_fourcorner": CSV_FOURCORNER,
        "csv_widthheight": CSV_WIDTHHEIGHT,
        "pascal_voc": PASCAL_VOC,
        "yolo_darknet": YOLO_DARKNET,
        "yolo_keras_pytorch": YOLO_KERAS_PYTORCH,
        "createml": CREATEML,
        "tfrecord": TFRECORD,
        "polygon_coco": POLYGON_COCO,
        "polygon_single": POLYGON_SINGLE,
        "csv_classification": CSV_CLASSIFICATION,
        "classification_tfrecord": CLASSIFICATION_TFRECORD,
        "keypoints_coco": KEYPOINTS_COCO,
    }


@add_mapping
@unique
class AssetStatus(Enum):
    """Asset Status.

    Asset Status Options:
        Annotated
        Review
        Completed
        Tofix
        None
    """

    ANNOTATED = "Annotated"
    REVIEW = "Review"
    COMPLETED = "Completed"
    TOFIX = "Tofix"
    NONE = "None"

    __MAPPING__ = {
        "Annotated": ANNOTATED,
        "Review": REVIEW,
        "Completed": COMPLETED,
        "Tofix": TOFIX,
        "None": NONE,
    }


@add_mapping
@unique
class OperationStatusOverview(Enum):
    """Operation Status. 
    """

    QUEUED = "Queued"
    RUNNING = "Running"
    FINISHED = "Finished"
    CANCELLED = "Cancelled"
    ERRORED = "Errored"

    __MAPPING__ = {
        "Queued": QUEUED,
        "Running": RUNNING,
        "Finished": FINISHED,
        "Cancelled": CANCELLED,
        "Errored": ERRORED,
    }


@add_mapping
@unique
class DeploymentStatusOverview(Enum):
    """Deployment Status. 
    """

    CREATING = "Creating"
    UPDATING = "Updating"
    REMOVING = "Removing"
    AVAILABLE = "Available"
    ERRORED = "Errored"

    __MAPPING__ = {
        "Creating": CREATING,
        "Updating": UPDATING,
        "Removing": REMOVING,
        "Available": AVAILABLE,
        "Errored": ERRORED,
    }


@add_mapping
@unique
class RunStatusOverview(Enum):
    """Run Status. 
    """
    CREATING = "Creating"
    RUNNING = "Running"
    FINISHED = "Finished"
    ERRORED = "Errored"
    CANCELLED = "Cancelled"

    __MAPPING__ = {
        "Creating": CREATING,
        "Running": RUNNING,
        "Finished": FINISHED,
        "Errored": ERRORED,
        "Cancelled": CANCELLED,
    }


@add_mapping
@unique
class ModelFormat(Enum):
    """Artifact supported Models Format. 
    """
    TENSORFLOW = "TensorFlow"
    TFLITE = "TFLite"
    ONNX = "ONNX"
    PYTORCH = "PyTorch"
    COREML = "CoreML"

    __MAPPING__ = {
        "TensorFlow": TENSORFLOW,
        "TFLite": TFLITE,
        "ONNX": ONNX,
        "PyTorch": PYTORCH,
        "CoreML": COREML
    }


@dataclass
class AnnotationMetadata:
    """Annotation metadata.

    :param asset_id: The unique ID of the asset.
    :param tag: The tag class name of the annotation.
    :param bound_type: The bound type of the annotation (Rectangle or Polygon).
    :param bound: The bound coordinates of the annotation in
        [[x1, y1], [x2, y2], ... , [xn, yn]] format.
    """

    asset_id: str
    tag: str
    bound_type: BoundType
    bound: list

    def __post_init__(self):
        if isinstance(self.bound_type, str):
            self.bound_type = BoundType(self.bound_type)

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {
            "assetId": self.asset_id,
            "tag": self.tag,
            "boundType": self.bound_type.value,
            "bound": self.bound,
        }


@dataclass
class AnnotationExportOptions:
    """Annotation exported options.

    :param split_ratio: The ratio used to split the data into training and validation sets.
    :param seed: The number used to initialize a pseudorandom
        number generator to randomize the annotation shuffling.
    :param normalized: Boolean to indicate whether the bound
        coordinates of the exported annotations should be normalized. Defaults to True.
    """
    split_ratio: int
    seed: int
    normalized: bool = True

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {
            "splitRatio": self.split_ratio,
            "seed": self.seed,
            "normalized": self.normalized,
        }


@dataclass
class AnnotationExportMetadata:
    """Annotation exported metadata.

    :param format: The annotation format for bounding boxes or polygons as a string.
    :param options: The exporting options.
    """
    format: Union[AnnotationExportFormat, str]
    options: Union[AnnotationExportOptions, dict]

    def __post_init__(self):
        assert isinstance(self.format, (AnnotationExportFormat, str))
        assert isinstance(self.options, (AnnotationExportOptions, dict))

        if isinstance(self.format, str):
            self.format = AnnotationExportFormat(self.format)
        if isinstance(self.options, dict):
            self.options = AnnotationExportOptions(**self.options)

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {"format": self.format.value, "options": self.options.to_json()}


@dataclass
class Pagination:
    """Pagination Params.
    If the length of the function call results exceeds the limit,
    the results will be broken into multiple pages.

    :param page: An optional cursor to specify pagination if there are multiple pages of results.
    :param limit: A limit on the number of objects to be returned in a page. Defaults to 100.
    """

    page: str = None
    limit: int = 100

    def to_json(self):
        """ Function to convert dataclass to dict """
        pagination = {
            "page": self.page,
            "limit": self.limit,
        }

        # Remove None values
        return {k: v for k, v in pagination.items() if v is not None}


@dataclass
class AssetMetadata:
    """Asset Metadata.

    :param status: The annotation status of the asset (annotated, review, completed, tofix, none).
    :param custom_metadata: A dictionary containing any key-value pairs.
    """

    status: Union[AssetStatus, None] = None
    custom_metadata: object = None

    def to_json(self):
        """ Function to convert dataclass to dict """
        asset_metadata = {
            "status": self.status,
            "customMetadata": self.custom_metadata,
        }

        # Remove None values
        return {k: v for k, v in asset_metadata.items() if v is not None}


@dataclass
class DeploymentOptions:
    """The configuration options for creating each Inference API instance.

    :param evaluation_strategy: The evaluation strategy to use
        of each Inference API, default entropy_score.
    :param evaluation_threshold: The evaluation threshold to
        use to trigger post-evaluation actions, default 0.5.
    :param evaluation_group: The asset group to which assets
        triggered by the active learning route will be uploaded, comma-separated list.
    """
    evaluation_strategy: str = None
    evaluation_threshold: float = None
    evaluation_group: [str] = None

    def to_json(self):
        """ Function to convert dataclass to dict """
        options = {
            "evaluationStrategy": self.evaluation_strategy,
            "evaluationThreshold": self.evaluation_threshold,
            "evaluationGroup": self.evaluation_group,
        }
        # Remove None values
        return {k: v for k, v in options.items() if v is not None}


@dataclass
class DeploymentResource:
    """The resource allocation for the deployment instance, optional.

    :param GPU_T4: The number of NVIDIA Tesla T4 GPUs to
        allocate to each Inference API instance, optional.
    """

    GPU_T4: int = None

    def to_json(self):
        """ Function to convert dataclass to dict """
        resource = {
            "GPU_T4": self.GPU_T4,
        }
        # Remove None values
        return {k: v for k, v in resource.items() if v is not None}


@dataclass
class DeploymentMetadata:
    """Deployment Settings Metadata.

    :param name: The name of the deployment instance.
    :param model_id: The ID of the exported artifact to be deployed.
    :param artifact_id: The ID of the artifact to be deployed.
    :param replicas: Number of deployment instances to spawn. Defaults to 1.
    :param version_tag: The current version tag of the deployment instance.
    :param resources: The resource allocation for the deployment instance, optional.
    :param options: The configuration options for the deployment instance, optional.
    """

    name: str = None
    model_id: str = None
    artifact_id: str = None
    replicas: int = 1
    version_tag: str = None
    resources: DeploymentResource = None
    options: DeploymentOptions = None

    def __post_init__(self):
        if isinstance(self.options, dict):
            self.options = DeploymentOptions(**self.options)
        if isinstance(self.resources, dict):
            self.resources = DeploymentResource(**self.resources)

    def to_json(self):
        """ Function to convert dataclass to dict """
        deployment_metadata = {
            'name':
            self.name,
            "versionTag":
            self.version_tag,
            'modelId':
            self.model_id,
            'artifactId':
            self.artifact_id,
            'replicas':
            self.replicas,
            'resources':
            self.resources.to_json() if self.resources is not None else None,
            'options':
            self.options.to_json() if self.options is not None else None,
        }
        return {
            k: v
            for k, v in deployment_metadata.items()
            if v is not None and v != {}
        }


@dataclass
class Accelerator:
    """The hardware accelerator to be used for the training.

    :param name: The name of the GPU to be used for the training
        (GPU_T4, GPU_P100, GPU_V100, GPU_L4, GPU_A100_40GB).
    :param count: The number of GPUs to be used for the training.
        More GPUs will use up more compute minutes. Defaults to 1.
    """

    name: str
    count: int = 1

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {
            "name": self.name,
            "count": self.count,
        }


@dataclass
class Checkpoint:
    """The checkpoint metric to be used for the training.

    :param strategy: The checkpointing strategy to be used for the training.

        Checkpoint Strategies:
            STRAT_EVERY_N_EPOCH: Checkpoints are saved at intervals of n epochs.
            STRAT_ALWAYS_SAVE_LATEST: The final checkpoint is always saved.
            STRAT_LOWEST_VALIDATION_LOSS: The checkpoint with the lowest validation loss is saved.
            STRAT_HIGHEST_ACCURACY: The checkpoint with the highest accuracy is saved.

    :param metric: The checkpointing metric to be used for training.
        Note that metrics starting with "Loss" are only applicable when the
        strategy is set to "STRAT_LOWEST_VALIDATION_LOSS", and metrics starting with
        "DetectionBoxes" are only applicable when the strategy is set to "STRAT_HIGHEST_ACCURACY".

        Loss:
            Loss/total_loss
            Loss/regularization_loss
            Loss/classification_loss
            Loss/localization_loss

        Precision:
            DetectionBoxes_Precision/mAP
            DetectionBoxes_Precision/mAP@.50IOU
            DetectionBoxes_Precision/mAP@.75IOU
            DetectionBoxes_Precision/mAP (small)
            DetectionBoxes_Precision/mAP (medium)
            DetectionBoxes_Precision/mAP (large)

        Recall:
            DetectionBoxes_Recall/AR@1
            DetectionBoxes_Recall/AR@10
            DetectionBoxes_Recall/AR@100
            DetectionBoxes_Recall/AR@100 (small)
            DetectionBoxes_Recall/AR@100 (medium)
            DetectionBoxes_Recall/AR@100 (large)

    :param evaluation_interval: The step interval for checkpoint
        evaluation during training. Defaults to 250.
    """

    strategy: str
    metric: str = None
    evaluation_interval: int = 250

    def to_json(self):
        """ Function to convert dataclass to dict """

        checkpoint = {
            "strategy": self.strategy,
            "metric": self.metric,
            "evaluationInterval": self.evaluation_interval,
        }
        # Remove None values
        return {k: v for k, v in checkpoint.items() if v is not None}


@dataclass
class Limit:
    """The limit configuration for the training.

    :param metric: The limit metric for the training.

        Limit Metrics:
            LIM_MINUTE: Limits the training to a maximum number of minutes before it is killed.
            LIM_EPOCHS: Limits the training to a maximum number of epochs before it is killed.
            LIM_NONE: No limit will be set for the training.

    :param value: The limit value for the training. This value will not be
        used if the limit metric is "LIM_NONE". Defaults to 1.
    """

    metric: str
    value: int = 1

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {
            "metric": self.metric,
            "value": self.value,
        }


@dataclass
class RunSetupMetadata:
    """The settings to start training.

    :param accelerator: The hardware accelerator to be used for the training.
    :param checkpoint: The checkpoint metric to be used for the training.
    :param limit: The limit configuration for the training.
    :param preview: Boolean to indicate whether preview
        is enabled for the training. Defaults to True.
    """

    accelerator: Accelerator = None
    checkpoint: Checkpoint = None
    limit: Limit = None
    preview: bool = True
    matrix: bool = True
    debug: bool = False

    def __post_init__(self):
        if isinstance(self.accelerator, dict):
            self.accelerator = Accelerator(**self.accelerator)
        if isinstance(self.checkpoint, dict):
            self.checkpoint = Checkpoint(**self.checkpoint)
        if isinstance(self.limit, dict):
            self.limit = Limit(**self.limit)


@dataclass
class FlowMetadata:
    """Workflow Metadata.

    :param title: The title of the workflow.
    """

    title: str

    def to_json(self):
        """ Function to convert dataclass to dict """
        return {
            "title": self.title,
        }


@dataclass
class AssetFilter:
    """Asset list filter.
    """
    groups: List[str] = None
    filename: str = None
    metadata_query: str = None
    status: Union[AssetStatus, str, None] = None

    def __post_init__(self):
        assert isinstance(self.groups, (List, type(None)))

        if isinstance(self.status, str):
            self.status = AssetStatus(self.status)

    def to_json(self):
        """ Function to convert dataclass to dict """
        asset_filters = {
            "group": self.groups,
            "filename": self.filename,
            "metadataQuery": self.metadata_query,
            "status": self.status.value if self.status is not None else None,
        }

        return {k: v for k, v in asset_filters.items() if v is not None}


@dataclass
class AnnotationFilter:
    """Annotation list filter.
    """
    asset_ids: List[str] = None

    def __post_init__(self):
        assert isinstance(self.asset_ids, (List, type(None)))

    def to_json(self):
        """ Function to convert dataclass to dict """
        annotation_filters = {
            "assetId": self.asset_ids,
        }

        return {k: v for k, v in annotation_filters.items() if v is not None}


@dataclass
class TagMetadata:
    """Tag Metadata.
    """
    name: str = None
    color: str = None
    description: str = None

    def to_json(self):
        """ Function to convert dataclass to dict """
        tag = {
            "name": self.name,
            "color": self.color,
            "description": self.description,
        }

        # Remove None values
        return {k: v for k, v in tag.items() if v is not None}


@dataclass
class ArtifactExportOptions:
    """Artifact Export Options.
    """
    format: Union[ModelFormat, str]
    quantization: str = None

    def __post_init__(self):
        assert isinstance(self.format, (ModelFormat, str))

        if isinstance(self.format, str):
            self.format = ModelFormat(self.format)

    def to_json(self):
        """ Function to convert dataclass to dict """
        options = {
            "format": self.format.value,
            "quantization": self.quantization,
        }

        # Remove None values
        return {k: v for k, v in options.items() if v is not None}


@dataclass
class ArtifactFilters:
    """Artifact list filter.
    """
    run_ids: List[str] = None

    def __post_init__(self):
        assert isinstance(self.run_ids, (List, type(None)))

    def to_json(self):
        """ Function to convert dataclass to dict """
        artifact_filters = {
            "runId": self.run_ids,
        }

        return {k: v for k, v in artifact_filters.items() if v is not None}
