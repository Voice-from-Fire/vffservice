import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

AppBar makeBar(BuildContext context) {
  final ButtonStyle style = TextButton.styleFrom(
    foregroundColor: Theme.of(context).colorScheme.onPrimary,
  );
  return AppBar(
    actions: <Widget>[
      TextButton(
        style: style,
        onPressed: () {},
        child: const Text('Action 1'),
      ),
      TextButton(
        style: style,
        onPressed: () {},
        child: const Text('Action 2'),
      ),
    ],
  );
}
