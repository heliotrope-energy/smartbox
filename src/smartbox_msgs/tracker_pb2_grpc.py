# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import tracker_pb2 as tracker__pb2


class TrackerControllerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.get_tracker_status = channel.unary_unary(
        '/smartbox_msgs.TrackerController/get_tracker_status',
        request_serializer=tracker__pb2.TrackerSystemStatusRequest.SerializeToString,
        response_deserializer=tracker__pb2.TrackerSystemStatusResponse.FromString,
        )
    self.tracker_control = channel.stream_stream(
        '/smartbox_msgs.TrackerController/tracker_control',
        request_serializer=tracker__pb2.ControlRequest.SerializeToString,
        response_deserializer=tracker__pb2.ControlResponse.FromString,
        )
    self.tracker_status = channel.unary_stream(
        '/smartbox_msgs.TrackerController/tracker_status',
        request_serializer=tracker__pb2.TrackerSystemStatusRequest.SerializeToString,
        response_deserializer=tracker__pb2.TrackerSystemStatusResponse.FromString,
        )


class TrackerControllerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def get_tracker_status(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def tracker_control(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def tracker_status(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_TrackerControllerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'get_tracker_status': grpc.unary_unary_rpc_method_handler(
          servicer.get_tracker_status,
          request_deserializer=tracker__pb2.TrackerSystemStatusRequest.FromString,
          response_serializer=tracker__pb2.TrackerSystemStatusResponse.SerializeToString,
      ),
      'tracker_control': grpc.stream_stream_rpc_method_handler(
          servicer.tracker_control,
          request_deserializer=tracker__pb2.ControlRequest.FromString,
          response_serializer=tracker__pb2.ControlResponse.SerializeToString,
      ),
      'tracker_status': grpc.unary_stream_rpc_method_handler(
          servicer.tracker_status,
          request_deserializer=tracker__pb2.TrackerSystemStatusRequest.FromString,
          response_serializer=tracker__pb2.TrackerSystemStatusResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'smartbox_msgs.TrackerController', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
