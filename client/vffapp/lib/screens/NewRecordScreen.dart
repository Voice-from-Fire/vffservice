import 'package:flutter/material.dart';

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

  @override
  Widget build(BuildContext context) {
    var children = _url != null && _duration != null
        ? [
            AudioPlayer(
              url: _url!,
              duration: _duration!,
            )
          ]
        : [AudioRecorder(onStop: onStop)];
    return ScreenWrapper("New record",
        child: Column(
            mainAxisAlignment: MainAxisAlignment.center, children: children));
  }
}
