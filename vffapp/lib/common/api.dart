import 'package:vff_api/vff_api.dart';

VffApi makeApi() {
  return VffApi(basePathOverride: "http://localhost:8000");
}
