import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vffapp/common/api.dart';

import '../common/appstate.dart';
import '../components/AudioPlayer.dart';
import '../components/AudioRecorder.dart';
import '../components/ScreenWrapper.dart';

/*class NewRecordScreen extends StatelessWidget {
  const NewRecordScreen({super.key});

  static const String route = '/new';

  @override
  Widget build(BuildContext context) {
    return const ScreenWrapper("New record", child: AudioPlayer(url: "xxx"));

    // return ScreenWrapper("New record",
    //     child: AudioRecorder(onStop: (path) => {print(path)}));
  }
}*/

class NewRecordScreen extends StatefulWidget {
  const NewRecordScreen({super.key});

  static const String route = '/new';

  @override
  State<NewRecordScreen> createState() => _NewRecordScreenState();
}

class _NewRecordScreenState extends State<NewRecordScreen> {
  String? _url;
  Duration? _duration;

  void onStop(String url, Duration duration) {
    setState(() {
      _url = url;
      _duration = duration;
    });
  }

  void discard() {
    setState(() {
      _url = null;
      _duration = null;
    });
  }

  Future<void> upload() async {
    print(_url);
    var bytes = await Dio().get<List<int>>(_url!,
        options: Options(responseType: ResponseType.bytes));
    print(bytes.data);
    var file = MultipartFile.fromBytes(bytes.data!);
    AppState appState = context.read<AppState>();
    var api = makeApi(appState);
    var samples = await api.getSamplesApi().uploadSampleSamplesPost(file: file);
    print(samples);
  }

  @override
  Widget build(BuildContext context) {
    var children = _url != null && _duration != null
        ? [
            AudioPlayer(
              url: _url!,
              duration: _duration!,
            ),
            const SizedBox(height: 60),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              ElevatedButton.icon(
                  onPressed: upload,
                  icon: const Icon(Icons.upload),
                  label: const Text("Upload\nrecording"),
                  style: ButtonStyle(
                      padding:
                          MaterialStateProperty.all(const EdgeInsets.all(30)))),
              const SizedBox(width: 60),
              ElevatedButton.icon(
                  onPressed: discard,
                  icon: const Icon(Icons.delete),
                  style: ButtonStyle(
                      backgroundColor: MaterialStateProperty.all(Colors.grey),
                      padding:
                          MaterialStateProperty.all(const EdgeInsets.all(30))),
                  label: const Text("Discard\nrecording"))
            ])
          ]
        : [AudioRecorder(onStop: onStop)];

    return ScreenWrapper("New record",
        child: Column(
            mainAxisAlignment: MainAxisAlignment.center, children: children));
  }
}
