import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vffapp/common/appstate.dart';
import 'package:vffapp/screens/LoginScreen.dart';
import 'package:vffapp/screens/NewRecordScreen.dart';
import 'package:vffapp/screens/RecordScreen.dart';

void main() {
  runApp(MultiProvider(
    providers: [
      ChangeNotifierProvider(create: (_) => AppState()),
    ],
    child: const VffApp(),
  ));
}

class VffApp extends StatelessWidget {
  const VffApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'VoiceFromFire',
        theme: ThemeData(
          primarySwatch: Colors.orange,
        ),
        initialRoute: '/',
        onGenerateRoute: (settings) {
          AppState appState = context.read<AppState>();
          if (appState.isLogged()) {
            Widget screen;
            if (RecordScreen.route == settings.name) {
              screen = const RecordScreen();
            } else if (NewRecordScreen.route == settings.name) {
              screen = const NewRecordScreen();
            } else {
              screen = const NewRecordScreen();
              //screen = const RecordScreen();
            }
            return MaterialPageRoute(builder: (_) => screen);
          } else {
            return MaterialPageRoute(builder: (_) => const LoginScreen());
            //return MaterialPageRoute(builder: (_) => const NewRecordScreen());
          }
        });
    /*routes: {
          '/': (context) => const LoginScreen(),
          RecordScreen.route: (context) => const RecordScreen(),
        });*/
  }
}
