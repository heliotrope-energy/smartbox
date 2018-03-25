# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: weather.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='weather.proto',
  package='smartbox',
  syntax='proto3',
  serialized_pb=_b('\n\rweather.proto\x12\x08smartbox\"[\n\x11TemperatureReport\x12\x0f\n\x07outdoor\x18\x01 \x01(\x01\x12\x0e\n\x06indoor\x18\x02 \x01(\x01\x12\x12\n\nfeels_like\x18\x03 \x01(\x01\x12\x11\n\tdew_point\x18\x04 \x01(\x01\"4\n\x0ePressureReport\x12\x10\n\x08relative\x18\x01 \x01(\x01\x12\x10\n\x08\x61\x62solute\x18\x02 \x01(\x01\"T\n\nWindReport\x12\x11\n\tdirection\x18\x01 \x01(\x01\x12\r\n\x05speed\x18\x02 \x01(\x01\x12\x0c\n\x04gust\x18\x03 \x01(\x01\x12\x16\n\x0emax_daily_gust\x18\x04 \x01(\x01\"C\n\x0eHumidityReport\x12\x18\n\x10humidity_percent\x18\x01 \x01(\x01\x12\x17\n\x0fhumidity_indoor\x18\x02 \x01(\x01\"i\n\nRainReport\x12\x0e\n\x06hourly\x18\x01 \x01(\x01\x12\r\n\x05\x64\x61ily\x18\x02 \x01(\x01\x12\x0e\n\x06weekly\x18\x03 \x01(\x01\x12\x0f\n\x07monthly\x18\x04 \x01(\x01\x12\r\n\x05total\x18\x05 \x01(\x01\x12\x0c\n\x04last\x18\x06 \x01(\t\",\n\x0bSolarReport\x12\n\n\x02uv\x18\x01 \x01(\x01\x12\x11\n\tradiation\x18\x02 \x01(\x01\"!\n\x0eWeatherRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"\xa9\x02\n\x0fWeatherResponse\x12\x0c\n\x04\x64\x61te\x18\x01 \x01(\t\x12\x10\n\x08\x64\x61te_utc\x18\x02 \x01(\x05\x12\x30\n\x0btemperature\x18\x03 \x01(\x0b\x32\x1b.smartbox.TemperatureReport\x12\"\n\x04wind\x18\x04 \x01(\x0b\x32\x14.smartbox.WindReport\x12*\n\x08pressure\x18\x05 \x01(\x0b\x32\x18.smartbox.PressureReport\x12*\n\x08humidity\x18\x06 \x01(\x0b\x32\x18.smartbox.HumidityReport\x12\"\n\x04rain\x18\x07 \x01(\x0b\x32\x14.smartbox.RainReport\x12$\n\x05solar\x18\x08 \x01(\x0b\x32\x15.smartbox.SolarReport2\\\n\x11WeatherController\x12G\n\x0eweather_report\x12\x18.smartbox.WeatherRequest\x1a\x19.smartbox.WeatherResponse\"\x00\x62\x06proto3')
)




_TEMPERATUREREPORT = _descriptor.Descriptor(
  name='TemperatureReport',
  full_name='smartbox.TemperatureReport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='outdoor', full_name='smartbox.TemperatureReport.outdoor', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='indoor', full_name='smartbox.TemperatureReport.indoor', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='feels_like', full_name='smartbox.TemperatureReport.feels_like', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dew_point', full_name='smartbox.TemperatureReport.dew_point', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=27,
  serialized_end=118,
)


_PRESSUREREPORT = _descriptor.Descriptor(
  name='PressureReport',
  full_name='smartbox.PressureReport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='relative', full_name='smartbox.PressureReport.relative', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='absolute', full_name='smartbox.PressureReport.absolute', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=120,
  serialized_end=172,
)


_WINDREPORT = _descriptor.Descriptor(
  name='WindReport',
  full_name='smartbox.WindReport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='direction', full_name='smartbox.WindReport.direction', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='speed', full_name='smartbox.WindReport.speed', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gust', full_name='smartbox.WindReport.gust', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_daily_gust', full_name='smartbox.WindReport.max_daily_gust', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=174,
  serialized_end=258,
)


_HUMIDITYREPORT = _descriptor.Descriptor(
  name='HumidityReport',
  full_name='smartbox.HumidityReport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='humidity_percent', full_name='smartbox.HumidityReport.humidity_percent', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='humidity_indoor', full_name='smartbox.HumidityReport.humidity_indoor', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=260,
  serialized_end=327,
)


_RAINREPORT = _descriptor.Descriptor(
  name='RainReport',
  full_name='smartbox.RainReport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='hourly', full_name='smartbox.RainReport.hourly', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='daily', full_name='smartbox.RainReport.daily', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='weekly', full_name='smartbox.RainReport.weekly', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='monthly', full_name='smartbox.RainReport.monthly', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total', full_name='smartbox.RainReport.total', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='last', full_name='smartbox.RainReport.last', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=329,
  serialized_end=434,
)


_SOLARREPORT = _descriptor.Descriptor(
  name='SolarReport',
  full_name='smartbox.SolarReport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uv', full_name='smartbox.SolarReport.uv', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='radiation', full_name='smartbox.SolarReport.radiation', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=436,
  serialized_end=480,
)


_WEATHERREQUEST = _descriptor.Descriptor(
  name='WeatherRequest',
  full_name='smartbox.WeatherRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='smartbox.WeatherRequest.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=482,
  serialized_end=515,
)


_WEATHERRESPONSE = _descriptor.Descriptor(
  name='WeatherResponse',
  full_name='smartbox.WeatherResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='date', full_name='smartbox.WeatherResponse.date', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='date_utc', full_name='smartbox.WeatherResponse.date_utc', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='temperature', full_name='smartbox.WeatherResponse.temperature', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='wind', full_name='smartbox.WeatherResponse.wind', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pressure', full_name='smartbox.WeatherResponse.pressure', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='humidity', full_name='smartbox.WeatherResponse.humidity', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rain', full_name='smartbox.WeatherResponse.rain', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='solar', full_name='smartbox.WeatherResponse.solar', index=7,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=518,
  serialized_end=815,
)

_WEATHERRESPONSE.fields_by_name['temperature'].message_type = _TEMPERATUREREPORT
_WEATHERRESPONSE.fields_by_name['wind'].message_type = _WINDREPORT
_WEATHERRESPONSE.fields_by_name['pressure'].message_type = _PRESSUREREPORT
_WEATHERRESPONSE.fields_by_name['humidity'].message_type = _HUMIDITYREPORT
_WEATHERRESPONSE.fields_by_name['rain'].message_type = _RAINREPORT
_WEATHERRESPONSE.fields_by_name['solar'].message_type = _SOLARREPORT
DESCRIPTOR.message_types_by_name['TemperatureReport'] = _TEMPERATUREREPORT
DESCRIPTOR.message_types_by_name['PressureReport'] = _PRESSUREREPORT
DESCRIPTOR.message_types_by_name['WindReport'] = _WINDREPORT
DESCRIPTOR.message_types_by_name['HumidityReport'] = _HUMIDITYREPORT
DESCRIPTOR.message_types_by_name['RainReport'] = _RAINREPORT
DESCRIPTOR.message_types_by_name['SolarReport'] = _SOLARREPORT
DESCRIPTOR.message_types_by_name['WeatherRequest'] = _WEATHERREQUEST
DESCRIPTOR.message_types_by_name['WeatherResponse'] = _WEATHERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TemperatureReport = _reflection.GeneratedProtocolMessageType('TemperatureReport', (_message.Message,), dict(
  DESCRIPTOR = _TEMPERATUREREPORT,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.TemperatureReport)
  ))
_sym_db.RegisterMessage(TemperatureReport)

PressureReport = _reflection.GeneratedProtocolMessageType('PressureReport', (_message.Message,), dict(
  DESCRIPTOR = _PRESSUREREPORT,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.PressureReport)
  ))
_sym_db.RegisterMessage(PressureReport)

WindReport = _reflection.GeneratedProtocolMessageType('WindReport', (_message.Message,), dict(
  DESCRIPTOR = _WINDREPORT,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.WindReport)
  ))
_sym_db.RegisterMessage(WindReport)

HumidityReport = _reflection.GeneratedProtocolMessageType('HumidityReport', (_message.Message,), dict(
  DESCRIPTOR = _HUMIDITYREPORT,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.HumidityReport)
  ))
_sym_db.RegisterMessage(HumidityReport)

RainReport = _reflection.GeneratedProtocolMessageType('RainReport', (_message.Message,), dict(
  DESCRIPTOR = _RAINREPORT,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.RainReport)
  ))
_sym_db.RegisterMessage(RainReport)

SolarReport = _reflection.GeneratedProtocolMessageType('SolarReport', (_message.Message,), dict(
  DESCRIPTOR = _SOLARREPORT,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.SolarReport)
  ))
_sym_db.RegisterMessage(SolarReport)

WeatherRequest = _reflection.GeneratedProtocolMessageType('WeatherRequest', (_message.Message,), dict(
  DESCRIPTOR = _WEATHERREQUEST,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.WeatherRequest)
  ))
_sym_db.RegisterMessage(WeatherRequest)

WeatherResponse = _reflection.GeneratedProtocolMessageType('WeatherResponse', (_message.Message,), dict(
  DESCRIPTOR = _WEATHERRESPONSE,
  __module__ = 'weather_pb2'
  # @@protoc_insertion_point(class_scope:smartbox.WeatherResponse)
  ))
_sym_db.RegisterMessage(WeatherResponse)



_WEATHERCONTROLLER = _descriptor.ServiceDescriptor(
  name='WeatherController',
  full_name='smartbox.WeatherController',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=817,
  serialized_end=909,
  methods=[
  _descriptor.MethodDescriptor(
    name='weather_report',
    full_name='smartbox.WeatherController.weather_report',
    index=0,
    containing_service=None,
    input_type=_WEATHERREQUEST,
    output_type=_WEATHERRESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_WEATHERCONTROLLER)

DESCRIPTOR.services_by_name['WeatherController'] = _WEATHERCONTROLLER

# @@protoc_insertion_point(module_scope)
