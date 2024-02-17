# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from _qwak_proto.qwak.execution.v1.jobs import job_service_pb2 as qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2


class JobServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ApplyJobRecord = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/ApplyJobRecord',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ApplyJobRecordRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ApplyJobRecordResponse.FromString,
                )
        self.InitPagination = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/InitPagination',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.InitPaginationRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.InitPaginationResponse.FromString,
                )
        self.ListJobs = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/ListJobs',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ListJobsRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ListJobsResponse.FromString,
                )
        self.DeleteFeaturesetJobs = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/DeleteFeaturesetJobs',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.DeleteFeaturesetJobsRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.DeleteFeaturesetJobsResponse.FromString,
                )
        self.GetLatestSuccessfulJobByFeaturesetId = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/GetLatestSuccessfulJobByFeaturesetId',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetLatestSuccessfulJobByFeaturesetIdRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetLatestSuccessfulJobByFeaturesetIdResponse.FromString,
                )
        self.GetAllFeaturesetLatestSuccessfulJobs = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/GetAllFeaturesetLatestSuccessfulJobs',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetLatestSuccessfulJobsRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetLatestSuccessfulJobsResponse.FromString,
                )
        self.GetAllFeaturesetJobsSummaries = channel.unary_unary(
                '/qwak.feature.store.execution.v1.jobs.JobService/GetAllFeaturesetJobsSummaries',
                request_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetJobsSummariesRequest.SerializeToString,
                response_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetJobsSummariesResponse.FromString,
                )


class JobServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ApplyJobRecord(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def InitPagination(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListJobs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteFeaturesetJobs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLatestSuccessfulJobByFeaturesetId(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllFeaturesetLatestSuccessfulJobs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllFeaturesetJobsSummaries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_JobServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ApplyJobRecord': grpc.unary_unary_rpc_method_handler(
                    servicer.ApplyJobRecord,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ApplyJobRecordRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ApplyJobRecordResponse.SerializeToString,
            ),
            'InitPagination': grpc.unary_unary_rpc_method_handler(
                    servicer.InitPagination,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.InitPaginationRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.InitPaginationResponse.SerializeToString,
            ),
            'ListJobs': grpc.unary_unary_rpc_method_handler(
                    servicer.ListJobs,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ListJobsRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ListJobsResponse.SerializeToString,
            ),
            'DeleteFeaturesetJobs': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteFeaturesetJobs,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.DeleteFeaturesetJobsRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.DeleteFeaturesetJobsResponse.SerializeToString,
            ),
            'GetLatestSuccessfulJobByFeaturesetId': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLatestSuccessfulJobByFeaturesetId,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetLatestSuccessfulJobByFeaturesetIdRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetLatestSuccessfulJobByFeaturesetIdResponse.SerializeToString,
            ),
            'GetAllFeaturesetLatestSuccessfulJobs': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllFeaturesetLatestSuccessfulJobs,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetLatestSuccessfulJobsRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetLatestSuccessfulJobsResponse.SerializeToString,
            ),
            'GetAllFeaturesetJobsSummaries': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllFeaturesetJobsSummaries,
                    request_deserializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetJobsSummariesRequest.FromString,
                    response_serializer=qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetJobsSummariesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'qwak.feature.store.execution.v1.jobs.JobService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class JobService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ApplyJobRecord(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/ApplyJobRecord',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ApplyJobRecordRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ApplyJobRecordResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def InitPagination(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/InitPagination',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.InitPaginationRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.InitPaginationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListJobs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/ListJobs',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ListJobsRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.ListJobsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteFeaturesetJobs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/DeleteFeaturesetJobs',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.DeleteFeaturesetJobsRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.DeleteFeaturesetJobsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLatestSuccessfulJobByFeaturesetId(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/GetLatestSuccessfulJobByFeaturesetId',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetLatestSuccessfulJobByFeaturesetIdRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetLatestSuccessfulJobByFeaturesetIdResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAllFeaturesetLatestSuccessfulJobs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/GetAllFeaturesetLatestSuccessfulJobs',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetLatestSuccessfulJobsRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetLatestSuccessfulJobsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAllFeaturesetJobsSummaries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qwak.feature.store.execution.v1.jobs.JobService/GetAllFeaturesetJobsSummaries',
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetJobsSummariesRequest.SerializeToString,
            qwak_dot_execution_dot_v1_dot_jobs_dot_job__service__pb2.GetAllFeaturesetJobsSummariesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
