import 'package:dio/dio.dart';
import 'package:vff_api/vff_api.dart';
import 'package:vffapp/common/appstate.dart';

VffApi makeApi(AppState? appState) {
  var url = "http://localhost:8000";
  Map<String, String>? headers;
  if (appState?.accessToken != null) {
    headers = {"Authorization": "Bearer ${appState!.accessToken!}"};
  }

  var dio = Dio(BaseOptions(
    baseUrl: url,
    headers: headers,
    connectTimeout: 5000,
    receiveTimeout: 3000,
  ));

  return VffApi(dio: dio);
}
