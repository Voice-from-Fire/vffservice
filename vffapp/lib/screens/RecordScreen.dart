import 'package:flutter/material.dart';

import '../components/ScreenWrapper.dart';

class RecordScreen extends StatelessWidget {
  const RecordScreen({super.key});

  static const String route = '/records';

  @override
  Widget build(BuildContext context) {
    return ScreenWrapper("Audio records",
        child: Text("Records", style: Theme.of(context).textTheme.headline3));
  }
}
