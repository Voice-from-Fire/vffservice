import 'package:flutter/material.dart';

import '../components/ScreenWrapper.dart';

class NewRecordScreen extends StatelessWidget {
  const NewRecordScreen({super.key});

  static const String route = '/new';

  @override
  Widget build(BuildContext context) {
    return ScreenWrapper("New record",
        child:
            Text("New record", style: Theme.of(context).textTheme.headline3));
  }
}
