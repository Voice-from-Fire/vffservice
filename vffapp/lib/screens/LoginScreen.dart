import 'package:flutter/material.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();

  // @override
  // Widget build(BuildContext context) {
  //   return Scaffold(
  //       body: Column(
  //     mainAxisAlignment: MainAxisAlignment.center,
  //     crossAxisAlignment: CrossAxisAlignment.center,
  //     children: <Widget>[
  //       Center(
  //         child: Text('Voice From Fire',
  //             style: Theme.of(context).textTheme.headline2),
  //       ),
  //       Text("XXX")
  //     ],
  //   ));
  // }
}

class _LoginScreenState extends State<LoginScreen> {
  final nameController = TextEditingController(text: "testuser");
  final passwordController = TextEditingController(text: "pass");

  @override
  void dispose() {
    nameController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: <Widget>[
        Center(
          child: Text('Voice From Fire',
              style: Theme.of(context).textTheme.headline2),
        ),
        TextField(controller: nameController),
        TextField(
            controller: passwordController,
            obscureText: true,
            enableSuggestions: false,
            autocorrect: false),
        ElevatedButton(onPressed: () {}, child: Text("Login"))
      ],
    ));
  }
}
