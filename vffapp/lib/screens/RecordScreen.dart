import 'package:flutter/material.dart';
import 'package:vffapp/components/MainBar.dart';

class RecordScreen extends StatelessWidget {
  const RecordScreen({super.key});

  static const String route = '/records';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: makeBar(context),
        body: Text("Records", style: Theme.of(context).textTheme.headline3));
  }
}
