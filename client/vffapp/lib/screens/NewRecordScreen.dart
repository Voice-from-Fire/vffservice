import 'package:flutter/material.dart';

import '../components/AudioRecorder.dart';
import '../components/ScreenWrapper.dart';

class NewRecordScreen extends StatelessWidget {
  const NewRecordScreen({super.key});

  static const String route = '/new';

  @override
  Widget build(BuildContext context) {
    return ScreenWrapper("New record",
        child: AudioRecorder(onStop: (path) => {print(path)}));
  }
}
