import contextlib
import os
import zipfile
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Union

import requests
from qwak.clients.feature_store.management_client import FeatureRegistryClient
from qwak.exceptions import QwakException

ZIP_FUNCTION_CONTENT_TYPE = "text/plain"

if TYPE_CHECKING:
    from qwak.feature_store.data_sources.streaming.kafka.deserialization import (
        Deserializer,
    )
    from qwak.feature_store.feature_sets.transformations.transformations import (
        BaseTransformation,
    )


def zip_function_with_base_folder(
    functions: List[Callable], fs_object_module_dir: Path = None
) -> bytes:
    """
    Prepare zip bytes of the UDF functions and it's parent folder
    In case the functions param is a Callable it will write the pkled code to "function.pkl" (original flow)
    If a list of functions it will write each function to {function_name}.pkl
    Args:
        functions: udf functions
        fs_object_module_dir: parent directory path of the registered feature store object
    Returns:
        bytes representing the zip bytes of the udf functions pkl and module
    """
    try:
        import cloudpickle
    except ImportError:
        raise QwakException(
            "Please install the cloudpickle package in your environment"
        )

    in_memory = BytesIO()
    with chdir(fs_object_module_dir):
        zf = zipfile.ZipFile(in_memory, mode="w")
        with zf:
            if fs_object_module_dir:
                for path in Path.cwd().glob("**/*"):
                    str_path = (
                        f"./{path.relative_to(Path.cwd())}"
                        if path.is_file()
                        else str(path.resolve())
                    )
                    zf.write(str_path, "code" + "/" + str_path)
            for function in functions:
                zf.writestr(f"{function.__name__}.pkl", cloudpickle.dumps(function))
        in_memory.seek(0)
    return in_memory.read()


@contextlib.contextmanager
def chdir(dirname: Path = None):
    """
    chdir to given path and return to previous cwd when done
    Args:
        dirname: dir to chdir into
    """
    current_dir = Path.cwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(current_dir)


def get_featureset_presign_url(
    features_manager_client: FeatureRegistryClient,
    feature_store_object_name: str,
    feature_store_object_name_suffix: str,
    transformation,
) -> str:
    return features_manager_client.get_presigned_url_v1(
        feature_set_name=feature_store_object_name + feature_store_object_name_suffix,
        transformation=transformation._to_proto(),
    )


def get_data_source_presign_url(
    features_manager_client: FeatureRegistryClient,
    data_source_object_name: str,
    data_source_name_suffix: str,
) -> str:
    return features_manager_client.get_data_source_presigned_url(
        data_source_name=data_source_object_name, object_name=data_source_name_suffix
    )


def upload_artifact(
    feature_store_object_name: str,
    feature_store_object_name_suffix: str,
    functions: List[Callable],
    feature_module_dir: Path,
    features_manager_client: FeatureRegistryClient,
    artifact_object: Union["BaseTransformation", "Deserializer"],
) -> str:
    """
    This function is used for uploading the function code in case a UDF type transformation was used (Pandas/Koalas)
    If a transformation was supplied, meaning we're running for at least batch, will use the SaaS adapted
    function to get the presign URL.
    """
    uploaded_artifact_url: str

    # this is done here to avoid cyclic imports
    from qwak.feature_store.data_sources.streaming.kafka.deserialization import (
        Deserializer,
    )
    from qwak.feature_store.feature_sets.transformations.transformations import (
        BaseTransformation,
    )

    if isinstance(artifact_object, BaseTransformation):
        presign_url = get_featureset_presign_url(
            features_manager_client=features_manager_client,
            feature_store_object_name=feature_store_object_name,
            feature_store_object_name_suffix=feature_store_object_name_suffix,
            transformation=artifact_object,
        )
    elif isinstance(artifact_object, Deserializer):
        presign_url = get_data_source_presign_url(
            features_manager_client=features_manager_client,
            data_source_object_name=feature_store_object_name,
            data_source_name_suffix=feature_store_object_name_suffix,
        )
    else:
        raise QwakException(
            f"Got an unsupported artifact type: {type(artifact_object)}"
        )

    uploaded_artifact_url = base_upload_function_code(
        presign_url, functions, feature_module_dir
    )

    return uploaded_artifact_url


def upload_data_source_function_code(
    data_source_name: str,
    data_source_object_name_suffix: str,
    functions: List[Callable],
    module_dir: Path,
    features_manager_client: FeatureRegistryClient,
) -> str:
    presign_url = get_data_source_presign_url(
        features_manager_client, data_source_name, data_source_object_name_suffix
    )
    return base_upload_function_code(presign_url, functions, module_dir)


def upload_to_s3(presign_url: str, in_memory_zip: bytes, content_type: str) -> str:
    http_response = requests.put(
        presign_url,
        headers={"content-type": content_type},
        data=in_memory_zip,
        timeout=600,
    )
    if 400 <= http_response.status_code < 600:
        raise QwakException(
            f"Error while uploading user function to s3. status code: {http_response.status_code}"
        )

    from urllib.parse import urlparse

    parsed_url = urlparse(presign_url)
    postfix = parsed_url.path
    bucket = parsed_url.hostname.split(".s3.")[0]
    s3_path = f"s3://{bucket}{postfix}"  # noqa: E231
    return s3_path


def base_upload_function_code(
    presign_url: str,
    functions: List[Callable],
    feature_module_dir: Path,
) -> str:
    """
    get presign url and prepare a zip file with the functions code
    and it's module and upload it to clients' s3 bucket
    Args:
        presign_url: presign url
        functions: udf functions
        feature_module_dir: parent directory path of the feature
    Returns:
        Full path to the zip file uploaded
    """
    in_memory_zip = zip_function_with_base_folder(functions, feature_module_dir)
    return upload_to_s3(
        presign_url=presign_url,
        in_memory_zip=in_memory_zip,
        content_type=ZIP_FUNCTION_CONTENT_TYPE,
    )
