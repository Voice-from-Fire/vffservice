import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vffapp/screens/NewRecordScreen.dart';
import 'package:vffapp/screens/RecordScreen.dart';

import '../common/appstate.dart';

class ScreenWrapper extends StatelessWidget {
  final Widget? child;
  final String title;

  const ScreenWrapper(this.title, {Key? key, @required this.child})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    AppState appState = context.watch<AppState>();
    String userName = appState.userName ?? "<unknown>";
    var drawer_content = ListView(
      // Important: Remove any padding from the ListView.
      padding: EdgeInsets.zero,
      children: [
        DrawerHeader(
          decoration: BoxDecoration(),
          child: Text('Logged as: ${userName}'),
        ),
        ListTile(
          title: const Text('New record'),
          onTap: () {
            Navigator.pop(context);
            Navigator.of(context).pushNamed(NewRecordScreen.route);
          },
        ),
        ListTile(
          title: const Text('My records'),
          onTap: () {
            Navigator.pop(context);
            Navigator.of(context).pushNamed(RecordScreen.route);
          },
        ),
        ListTile(
          title: const Text('Logout'),
          onTap: () {
            AppState appState = context.read<AppState>();
            appState.logout();
            Navigator.pop(context);
            Navigator.of(context).pushNamed("/");
          },
        ),
      ],
    );
    return Scaffold(
        appBar: AppBar(title: Text(title)),
        body: child,
        drawer: Drawer(child: drawer_content));
  }
}
