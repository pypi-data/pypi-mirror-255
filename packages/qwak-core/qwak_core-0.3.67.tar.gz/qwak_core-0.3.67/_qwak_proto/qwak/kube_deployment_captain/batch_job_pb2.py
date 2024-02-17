# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: qwak/kube_deployment_captain/batch_job.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n,qwak/kube_deployment_captain/batch_job.proto\x12\x1cqwak.kube.deployment.captain\"\xa1\x01\n\x1cListInferenceJobFilesRequest\x12\x0e\n\x06\x62ucket\x18\x01 \x01(\t\x12\x16\n\x0e\x64irectory_path\x18\x02 \x01(\t\x12\x14\n\x0ctoken_secret\x18\x03 \x01(\t\x12\x15\n\rsecret_secret\x18\x04 \x01(\t\x12\x1a\n\x12secret_service_url\x18\x05 \x01(\t\x12\x10\n\x08role_arn\x18\x06 \x01(\t\"\\\n\x1dListInferenceJobFilesResponse\x12\x12\n\nfile_names\x18\x01 \x03(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x16\n\x0e\x66\x61ilure_reason\x18\x03 \x01(\t\"\xf0\x01\n\"CreateInferenceTaskExecutorRequest\x12\x63\n\x1btask_executor_configuration\x18\x01 \x01(\x0b\x32>.qwak.kube.deployment.captain.TaskExecutorConfigurationMessage\x12\x65\n\x1cinference_task_configuration\x18\x02 \x01(\x0b\x32?.qwak.kube.deployment.captain.InferenceTaskConfigurationMessage\"\x89\x01\n\x1aPrepareInferenceJobRequest\x12k\n#inference_job_configuration_message\x18\x01 \x01(\x0b\x32>.qwak.kube.deployment.captain.InferenceJobConfigurationMessage\"F\n\x1bPrepareInferenceJobResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x16\n\x0e\x66\x61ilure_reason\x18\x02 \x01(\t\"\xe9\x03\n TaskExecutorConfigurationMessage\x12\x18\n\x10inference_job_id\x18\x01 \x01(\t\x12\x19\n\x11inference_task_id\x18\x02 \x01(\t\x12G\n\x10model_identifier\x18\x05 \x01(\x0b\x32-.qwak.kube.deployment.captain.ModelIdentifier\x12\x11\n\timage_url\x18\x06 \x01(\t\x12\x15\n\rbackoff_limit\x18\x07 \x01(\x05\x12\x0f\n\x03\x63pu\x18\x08 \x01(\x02\x42\x02\x18\x01\x12\x19\n\rmemory_amount\x18\t \x01(\x05\x42\x02\x18\x01\x12\x45\n\x0cmemory_units\x18\n \x01(\x0e\x32+.qwak.kube.deployment.captain.MemoryUnitApiB\x02\x18\x01\x12\x16\n\x0e\x65nvironment_id\x18\x0b \x01(\t\x12\x1b\n\x13\x63ustom_iam_role_arn\x18\x0c \x01(\t\x12\x41\n\x08job_size\x18\r \x01(\x0b\x32/.qwak.kube.deployment.captain.BatchJobResources\x12\x17\n\x0fpurchase_option\x18\x0e \x01(\t\x12\x19\n\x11image_pull_secret\x18\x0f \x01(\t\"q\n InferenceJobConfigurationMessage\x12\x18\n\x10inference_job_id\x18\x01 \x01(\t\x12\x16\n\x0e\x65nvironment_id\x18\x02 \x01(\t\x12\x1b\n\x13\x63ustom_iam_role_arn\x18\x03 \x01(\t\"`\n\x0fModelIdentifier\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x10\n\x08\x62uild_id\x18\x02 \x01(\t\x12\x15\n\tbranch_id\x18\x03 \x01(\tB\x02\x18\x01\x12\x12\n\nmodel_uuid\x18\x04 \x01(\t\"\x82\x03\n!InferenceTaskConfigurationMessage\x12\x15\n\rsource_bucket\x18\x01 \x01(\t\x12\x1a\n\x12\x64\x65stination_bucket\x18\x02 \x01(\t\x12\x10\n\x08\x66ilepath\x18\x03 \x01(\t\x12\x18\n\x10\x64\x65stination_path\x18\x04 \x01(\t\x12\x44\n\x0finput_file_type\x18\x05 \x01(\x0e\x32+.qwak.kube.deployment.captain.InputFileType\x12\x46\n\x10output_file_type\x18\x06 \x01(\x0e\x32,.qwak.kube.deployment.captain.OutputFileType\x12\x14\n\x0ctoken_secret\x18\x07 \x01(\t\x12\x15\n\rsecret_secret\x18\x08 \x01(\t\x12\x43\n\nparameters\x18\t \x03(\x0b\x32/.qwak.kube.deployment.captain.BatchJobParameter\"/\n\x11\x42\x61tchJobParameter\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"?\n#CleanInferenceTasksExecutorsRequest\x12\x18\n\x10inference_job_id\x18\x01 \x01(\t\"O\n$CleanInferenceTasksExecutorsResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x16\n\x0e\x66\x61ilure_reason\x18\x02 \x01(\t\"X\n!CleanInferenceTaskExecutorRequest\x12\x18\n\x10inference_job_id\x18\x01 \x01(\t\x12\x19\n\x11inference_task_id\x18\x02 \x01(\t\"M\n\"CleanInferenceTaskExecutorResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x16\n\x0e\x66\x61ilure_reason\x18\x02 \x01(\t\"N\n#CreateInferenceTaskExecutorResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x16\n\x0e\x66\x61ilure_reason\x18\x02 \x01(\t\"\xf7\x02\n\x1eStartInferenceJobWarmupRequest\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x15\n\tbranch_id\x18\x02 \x01(\tB\x02\x18\x01\x12\x10\n\x08\x62uild_id\x18\x03 \x01(\t\x12\x11\n\timage_url\x18\x04 \x01(\t\x12\x0f\n\x03\x63pu\x18\x05 \x01(\x02\x42\x02\x18\x01\x12\x19\n\rmemory_amount\x18\x06 \x01(\x05\x42\x02\x18\x01\x12\x45\n\x0cmemory_units\x18\x07 \x01(\x0e\x32+.qwak.kube.deployment.captain.MemoryUnitApiB\x02\x18\x01\x12\x11\n\texecutors\x18\x08 \x01(\x05\x12\x0f\n\x07timeout\x18\t \x01(\x05\x12\x41\n\x08job_size\x18\n \x01(\x0b\x32/.qwak.kube.deployment.captain.BatchJobResources\x12\x12\n\nmodel_uuid\x18\x0b \x01(\t\x12\x19\n\x11image_pull_secret\x18\x0c \x01(\t\"!\n\x1fStartInferenceJobWarmupResponse\"p\n\x1f\x43\x61ncelInferenceJobWarmupRequest\x12\x10\n\x08model_id\x18\x01 \x01(\t\x12\x15\n\tbranch_id\x18\x02 \x01(\tB\x02\x18\x01\x12\x10\n\x08\x62uild_id\x18\x03 \x01(\t\x12\x12\n\nmodel_uuid\x18\x04 \x01(\t\"\"\n CancelInferenceJobWarmupResponse\"\xd5\x01\n\x11\x42\x61tchJobResources\x12\x16\n\x0enumber_of_pods\x18\x01 \x01(\x05\x12\x0b\n\x03\x63pu\x18\x02 \x01(\x02\x12\x15\n\rmemory_amount\x18\x03 \x01(\x05\x12\x41\n\x0cmemory_units\x18\x04 \x01(\x0e\x32+.qwak.kube.deployment.captain.MemoryUnitApi\x12\x41\n\rgpu_resources\x18\x05 \x01(\x0b\x32*.qwak.kube.deployment.captain.GpuResources\"[\n\x0cGpuResources\x12\x37\n\x08gpu_type\x18\x01 \x01(\x0e\x32%.qwak.kube.deployment.captain.GpuType\x12\x12\n\ngpu_amount\x18\x02 \x01(\x05*:\n\rMemoryUnitApi\x12\x17\n\x13UNKNOWN_MEMORY_UNIT\x10\x00\x12\x07\n\x03MIB\x10\x01\x12\x07\n\x03GIB\x10\x02*\x81\x01\n\rInputFileType\x12\x1d\n\x19UNDEFINED_INPUT_FILE_TYPE\x10\x00\x12\x17\n\x13\x43SV_INPUT_FILE_TYPE\x10\x01\x12\x1b\n\x17\x46\x45\x41THER_INPUT_FILE_TYPE\x10\x02\x12\x1b\n\x17PARQUET_INPUT_FILE_TYPE\x10\x03*\x86\x01\n\x0eOutputFileType\x12\x1e\n\x1aUNDEFINED_OUTPUT_FILE_TYPE\x10\x00\x12\x18\n\x14\x43SV_OUTPUT_FILE_TYPE\x10\x01\x12\x1c\n\x18\x46\x45\x41THER_OUTPUT_FILE_TYPE\x10\x02\x12\x1c\n\x18PARQUET_OUTPUT_FILE_TYPE\x10\x03*{\n\x07GpuType\x12\x0f\n\x0bINVALID_GPU\x10\x00\x12\x0e\n\nNVIDIA_K80\x10\x01\x12\x0f\n\x0bNVIDIA_V100\x10\x02\x12\x0f\n\x0bNVIDIA_A100\x10\x03\x12\r\n\tNVIDIA_T4\x10\x04\x12\x0f\n\x0bNVIDIA_A10G\x10\x05\x12\r\n\tNVIDIA_L4\x10\x06\x42+\n\'com.qwak.ai.kube.deployment.captain.apiP\x01\x62\x06proto3')

_MEMORYUNITAPI = DESCRIPTOR.enum_types_by_name['MemoryUnitApi']
MemoryUnitApi = enum_type_wrapper.EnumTypeWrapper(_MEMORYUNITAPI)
_INPUTFILETYPE = DESCRIPTOR.enum_types_by_name['InputFileType']
InputFileType = enum_type_wrapper.EnumTypeWrapper(_INPUTFILETYPE)
_OUTPUTFILETYPE = DESCRIPTOR.enum_types_by_name['OutputFileType']
OutputFileType = enum_type_wrapper.EnumTypeWrapper(_OUTPUTFILETYPE)
_GPUTYPE = DESCRIPTOR.enum_types_by_name['GpuType']
GpuType = enum_type_wrapper.EnumTypeWrapper(_GPUTYPE)
UNKNOWN_MEMORY_UNIT = 0
MIB = 1
GIB = 2
UNDEFINED_INPUT_FILE_TYPE = 0
CSV_INPUT_FILE_TYPE = 1
FEATHER_INPUT_FILE_TYPE = 2
PARQUET_INPUT_FILE_TYPE = 3
UNDEFINED_OUTPUT_FILE_TYPE = 0
CSV_OUTPUT_FILE_TYPE = 1
FEATHER_OUTPUT_FILE_TYPE = 2
PARQUET_OUTPUT_FILE_TYPE = 3
INVALID_GPU = 0
NVIDIA_K80 = 1
NVIDIA_V100 = 2
NVIDIA_A100 = 3
NVIDIA_T4 = 4
NVIDIA_A10G = 5
NVIDIA_L4 = 6


_LISTINFERENCEJOBFILESREQUEST = DESCRIPTOR.message_types_by_name['ListInferenceJobFilesRequest']
_LISTINFERENCEJOBFILESRESPONSE = DESCRIPTOR.message_types_by_name['ListInferenceJobFilesResponse']
_CREATEINFERENCETASKEXECUTORREQUEST = DESCRIPTOR.message_types_by_name['CreateInferenceTaskExecutorRequest']
_PREPAREINFERENCEJOBREQUEST = DESCRIPTOR.message_types_by_name['PrepareInferenceJobRequest']
_PREPAREINFERENCEJOBRESPONSE = DESCRIPTOR.message_types_by_name['PrepareInferenceJobResponse']
_TASKEXECUTORCONFIGURATIONMESSAGE = DESCRIPTOR.message_types_by_name['TaskExecutorConfigurationMessage']
_INFERENCEJOBCONFIGURATIONMESSAGE = DESCRIPTOR.message_types_by_name['InferenceJobConfigurationMessage']
_MODELIDENTIFIER = DESCRIPTOR.message_types_by_name['ModelIdentifier']
_INFERENCETASKCONFIGURATIONMESSAGE = DESCRIPTOR.message_types_by_name['InferenceTaskConfigurationMessage']
_BATCHJOBPARAMETER = DESCRIPTOR.message_types_by_name['BatchJobParameter']
_CLEANINFERENCETASKSEXECUTORSREQUEST = DESCRIPTOR.message_types_by_name['CleanInferenceTasksExecutorsRequest']
_CLEANINFERENCETASKSEXECUTORSRESPONSE = DESCRIPTOR.message_types_by_name['CleanInferenceTasksExecutorsResponse']
_CLEANINFERENCETASKEXECUTORREQUEST = DESCRIPTOR.message_types_by_name['CleanInferenceTaskExecutorRequest']
_CLEANINFERENCETASKEXECUTORRESPONSE = DESCRIPTOR.message_types_by_name['CleanInferenceTaskExecutorResponse']
_CREATEINFERENCETASKEXECUTORRESPONSE = DESCRIPTOR.message_types_by_name['CreateInferenceTaskExecutorResponse']
_STARTINFERENCEJOBWARMUPREQUEST = DESCRIPTOR.message_types_by_name['StartInferenceJobWarmupRequest']
_STARTINFERENCEJOBWARMUPRESPONSE = DESCRIPTOR.message_types_by_name['StartInferenceJobWarmupResponse']
_CANCELINFERENCEJOBWARMUPREQUEST = DESCRIPTOR.message_types_by_name['CancelInferenceJobWarmupRequest']
_CANCELINFERENCEJOBWARMUPRESPONSE = DESCRIPTOR.message_types_by_name['CancelInferenceJobWarmupResponse']
_BATCHJOBRESOURCES = DESCRIPTOR.message_types_by_name['BatchJobResources']
_GPURESOURCES = DESCRIPTOR.message_types_by_name['GpuResources']
ListInferenceJobFilesRequest = _reflection.GeneratedProtocolMessageType('ListInferenceJobFilesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTINFERENCEJOBFILESREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.ListInferenceJobFilesRequest)
  })
_sym_db.RegisterMessage(ListInferenceJobFilesRequest)

ListInferenceJobFilesResponse = _reflection.GeneratedProtocolMessageType('ListInferenceJobFilesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTINFERENCEJOBFILESRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.ListInferenceJobFilesResponse)
  })
_sym_db.RegisterMessage(ListInferenceJobFilesResponse)

CreateInferenceTaskExecutorRequest = _reflection.GeneratedProtocolMessageType('CreateInferenceTaskExecutorRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEINFERENCETASKEXECUTORREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CreateInferenceTaskExecutorRequest)
  })
_sym_db.RegisterMessage(CreateInferenceTaskExecutorRequest)

PrepareInferenceJobRequest = _reflection.GeneratedProtocolMessageType('PrepareInferenceJobRequest', (_message.Message,), {
  'DESCRIPTOR' : _PREPAREINFERENCEJOBREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.PrepareInferenceJobRequest)
  })
_sym_db.RegisterMessage(PrepareInferenceJobRequest)

PrepareInferenceJobResponse = _reflection.GeneratedProtocolMessageType('PrepareInferenceJobResponse', (_message.Message,), {
  'DESCRIPTOR' : _PREPAREINFERENCEJOBRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.PrepareInferenceJobResponse)
  })
_sym_db.RegisterMessage(PrepareInferenceJobResponse)

TaskExecutorConfigurationMessage = _reflection.GeneratedProtocolMessageType('TaskExecutorConfigurationMessage', (_message.Message,), {
  'DESCRIPTOR' : _TASKEXECUTORCONFIGURATIONMESSAGE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.TaskExecutorConfigurationMessage)
  })
_sym_db.RegisterMessage(TaskExecutorConfigurationMessage)

InferenceJobConfigurationMessage = _reflection.GeneratedProtocolMessageType('InferenceJobConfigurationMessage', (_message.Message,), {
  'DESCRIPTOR' : _INFERENCEJOBCONFIGURATIONMESSAGE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.InferenceJobConfigurationMessage)
  })
_sym_db.RegisterMessage(InferenceJobConfigurationMessage)

ModelIdentifier = _reflection.GeneratedProtocolMessageType('ModelIdentifier', (_message.Message,), {
  'DESCRIPTOR' : _MODELIDENTIFIER,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.ModelIdentifier)
  })
_sym_db.RegisterMessage(ModelIdentifier)

InferenceTaskConfigurationMessage = _reflection.GeneratedProtocolMessageType('InferenceTaskConfigurationMessage', (_message.Message,), {
  'DESCRIPTOR' : _INFERENCETASKCONFIGURATIONMESSAGE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.InferenceTaskConfigurationMessage)
  })
_sym_db.RegisterMessage(InferenceTaskConfigurationMessage)

BatchJobParameter = _reflection.GeneratedProtocolMessageType('BatchJobParameter', (_message.Message,), {
  'DESCRIPTOR' : _BATCHJOBPARAMETER,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.BatchJobParameter)
  })
_sym_db.RegisterMessage(BatchJobParameter)

CleanInferenceTasksExecutorsRequest = _reflection.GeneratedProtocolMessageType('CleanInferenceTasksExecutorsRequest', (_message.Message,), {
  'DESCRIPTOR' : _CLEANINFERENCETASKSEXECUTORSREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CleanInferenceTasksExecutorsRequest)
  })
_sym_db.RegisterMessage(CleanInferenceTasksExecutorsRequest)

CleanInferenceTasksExecutorsResponse = _reflection.GeneratedProtocolMessageType('CleanInferenceTasksExecutorsResponse', (_message.Message,), {
  'DESCRIPTOR' : _CLEANINFERENCETASKSEXECUTORSRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CleanInferenceTasksExecutorsResponse)
  })
_sym_db.RegisterMessage(CleanInferenceTasksExecutorsResponse)

CleanInferenceTaskExecutorRequest = _reflection.GeneratedProtocolMessageType('CleanInferenceTaskExecutorRequest', (_message.Message,), {
  'DESCRIPTOR' : _CLEANINFERENCETASKEXECUTORREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CleanInferenceTaskExecutorRequest)
  })
_sym_db.RegisterMessage(CleanInferenceTaskExecutorRequest)

CleanInferenceTaskExecutorResponse = _reflection.GeneratedProtocolMessageType('CleanInferenceTaskExecutorResponse', (_message.Message,), {
  'DESCRIPTOR' : _CLEANINFERENCETASKEXECUTORRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CleanInferenceTaskExecutorResponse)
  })
_sym_db.RegisterMessage(CleanInferenceTaskExecutorResponse)

CreateInferenceTaskExecutorResponse = _reflection.GeneratedProtocolMessageType('CreateInferenceTaskExecutorResponse', (_message.Message,), {
  'DESCRIPTOR' : _CREATEINFERENCETASKEXECUTORRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CreateInferenceTaskExecutorResponse)
  })
_sym_db.RegisterMessage(CreateInferenceTaskExecutorResponse)

StartInferenceJobWarmupRequest = _reflection.GeneratedProtocolMessageType('StartInferenceJobWarmupRequest', (_message.Message,), {
  'DESCRIPTOR' : _STARTINFERENCEJOBWARMUPREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.StartInferenceJobWarmupRequest)
  })
_sym_db.RegisterMessage(StartInferenceJobWarmupRequest)

StartInferenceJobWarmupResponse = _reflection.GeneratedProtocolMessageType('StartInferenceJobWarmupResponse', (_message.Message,), {
  'DESCRIPTOR' : _STARTINFERENCEJOBWARMUPRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.StartInferenceJobWarmupResponse)
  })
_sym_db.RegisterMessage(StartInferenceJobWarmupResponse)

CancelInferenceJobWarmupRequest = _reflection.GeneratedProtocolMessageType('CancelInferenceJobWarmupRequest', (_message.Message,), {
  'DESCRIPTOR' : _CANCELINFERENCEJOBWARMUPREQUEST,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CancelInferenceJobWarmupRequest)
  })
_sym_db.RegisterMessage(CancelInferenceJobWarmupRequest)

CancelInferenceJobWarmupResponse = _reflection.GeneratedProtocolMessageType('CancelInferenceJobWarmupResponse', (_message.Message,), {
  'DESCRIPTOR' : _CANCELINFERENCEJOBWARMUPRESPONSE,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.CancelInferenceJobWarmupResponse)
  })
_sym_db.RegisterMessage(CancelInferenceJobWarmupResponse)

BatchJobResources = _reflection.GeneratedProtocolMessageType('BatchJobResources', (_message.Message,), {
  'DESCRIPTOR' : _BATCHJOBRESOURCES,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.BatchJobResources)
  })
_sym_db.RegisterMessage(BatchJobResources)

GpuResources = _reflection.GeneratedProtocolMessageType('GpuResources', (_message.Message,), {
  'DESCRIPTOR' : _GPURESOURCES,
  '__module__' : 'qwak.kube_deployment_captain.batch_job_pb2'
  # @@protoc_insertion_point(class_scope:qwak.kube.deployment.captain.GpuResources)
  })
_sym_db.RegisterMessage(GpuResources)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\'com.qwak.ai.kube.deployment.captain.apiP\001'
  _TASKEXECUTORCONFIGURATIONMESSAGE.fields_by_name['cpu']._options = None
  _TASKEXECUTORCONFIGURATIONMESSAGE.fields_by_name['cpu']._serialized_options = b'\030\001'
  _TASKEXECUTORCONFIGURATIONMESSAGE.fields_by_name['memory_amount']._options = None
  _TASKEXECUTORCONFIGURATIONMESSAGE.fields_by_name['memory_amount']._serialized_options = b'\030\001'
  _TASKEXECUTORCONFIGURATIONMESSAGE.fields_by_name['memory_units']._options = None
  _TASKEXECUTORCONFIGURATIONMESSAGE.fields_by_name['memory_units']._serialized_options = b'\030\001'
  _MODELIDENTIFIER.fields_by_name['branch_id']._options = None
  _MODELIDENTIFIER.fields_by_name['branch_id']._serialized_options = b'\030\001'
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['branch_id']._options = None
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['branch_id']._serialized_options = b'\030\001'
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['cpu']._options = None
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['cpu']._serialized_options = b'\030\001'
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['memory_amount']._options = None
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['memory_amount']._serialized_options = b'\030\001'
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['memory_units']._options = None
  _STARTINFERENCEJOBWARMUPREQUEST.fields_by_name['memory_units']._serialized_options = b'\030\001'
  _CANCELINFERENCEJOBWARMUPREQUEST.fields_by_name['branch_id']._options = None
  _CANCELINFERENCEJOBWARMUPREQUEST.fields_by_name['branch_id']._serialized_options = b'\030\001'
  _MEMORYUNITAPI._serialized_start=3201
  _MEMORYUNITAPI._serialized_end=3259
  _INPUTFILETYPE._serialized_start=3262
  _INPUTFILETYPE._serialized_end=3391
  _OUTPUTFILETYPE._serialized_start=3394
  _OUTPUTFILETYPE._serialized_end=3528
  _GPUTYPE._serialized_start=3530
  _GPUTYPE._serialized_end=3653
  _LISTINFERENCEJOBFILESREQUEST._serialized_start=79
  _LISTINFERENCEJOBFILESREQUEST._serialized_end=240
  _LISTINFERENCEJOBFILESRESPONSE._serialized_start=242
  _LISTINFERENCEJOBFILESRESPONSE._serialized_end=334
  _CREATEINFERENCETASKEXECUTORREQUEST._serialized_start=337
  _CREATEINFERENCETASKEXECUTORREQUEST._serialized_end=577
  _PREPAREINFERENCEJOBREQUEST._serialized_start=580
  _PREPAREINFERENCEJOBREQUEST._serialized_end=717
  _PREPAREINFERENCEJOBRESPONSE._serialized_start=719
  _PREPAREINFERENCEJOBRESPONSE._serialized_end=789
  _TASKEXECUTORCONFIGURATIONMESSAGE._serialized_start=792
  _TASKEXECUTORCONFIGURATIONMESSAGE._serialized_end=1281
  _INFERENCEJOBCONFIGURATIONMESSAGE._serialized_start=1283
  _INFERENCEJOBCONFIGURATIONMESSAGE._serialized_end=1396
  _MODELIDENTIFIER._serialized_start=1398
  _MODELIDENTIFIER._serialized_end=1494
  _INFERENCETASKCONFIGURATIONMESSAGE._serialized_start=1497
  _INFERENCETASKCONFIGURATIONMESSAGE._serialized_end=1883
  _BATCHJOBPARAMETER._serialized_start=1885
  _BATCHJOBPARAMETER._serialized_end=1932
  _CLEANINFERENCETASKSEXECUTORSREQUEST._serialized_start=1934
  _CLEANINFERENCETASKSEXECUTORSREQUEST._serialized_end=1997
  _CLEANINFERENCETASKSEXECUTORSRESPONSE._serialized_start=1999
  _CLEANINFERENCETASKSEXECUTORSRESPONSE._serialized_end=2078
  _CLEANINFERENCETASKEXECUTORREQUEST._serialized_start=2080
  _CLEANINFERENCETASKEXECUTORREQUEST._serialized_end=2168
  _CLEANINFERENCETASKEXECUTORRESPONSE._serialized_start=2170
  _CLEANINFERENCETASKEXECUTORRESPONSE._serialized_end=2247
  _CREATEINFERENCETASKEXECUTORRESPONSE._serialized_start=2249
  _CREATEINFERENCETASKEXECUTORRESPONSE._serialized_end=2327
  _STARTINFERENCEJOBWARMUPREQUEST._serialized_start=2330
  _STARTINFERENCEJOBWARMUPREQUEST._serialized_end=2705
  _STARTINFERENCEJOBWARMUPRESPONSE._serialized_start=2707
  _STARTINFERENCEJOBWARMUPRESPONSE._serialized_end=2740
  _CANCELINFERENCEJOBWARMUPREQUEST._serialized_start=2742
  _CANCELINFERENCEJOBWARMUPREQUEST._serialized_end=2854
  _CANCELINFERENCEJOBWARMUPRESPONSE._serialized_start=2856
  _CANCELINFERENCEJOBWARMUPRESPONSE._serialized_end=2890
  _BATCHJOBRESOURCES._serialized_start=2893
  _BATCHJOBRESOURCES._serialized_end=3106
  _GPURESOURCES._serialized_start=3108
  _GPURESOURCES._serialized_end=3199
# @@protoc_insertion_point(module_scope)
