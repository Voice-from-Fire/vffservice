import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vffapp/common/api.dart';
import 'package:vffapp/common/appstate.dart';
import 'package:vffapp/common/errors.dart';
import 'package:vffapp/screens/RecordScreen.dart';
import 'package:vff_api/vff_api.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final nameController = TextEditingController(text: "testuser");
  final passwordController = TextEditingController(text: "pass");
  bool _loginInProgress = false;

  @override
  void dispose() {
    nameController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  void setLoginInProcess(bool value) {
    setState(() {
      _loginInProgress = value;
    });
  }

  Future<void> doLogin(BuildContext context) async {
    setLoginInProcess(true);
    var api = makeApi(null).getUsersApi();

    try {
      var response = await api.loginAuthTokenPost(
          username: nameController.text, password: passwordController.text);
      AppState appState = context.read<AppState>();
      appState.login(nameController.text, response.data!.asMap["access_token"]);
      Navigator.of(context).pushNamed("/");
    } on DioError catch (e) {
      setLoginInProcess(false);
      if (e.response?.statusCode == 401) {
        showErrorMessage(context, "Invalid name or password");
      } else {
        showErrorMessage(context, "Connection to server failed");
      }
    }

    //showErrorMessage(context, "XXXX");
    /*appState.login("xxx", "token");
    Navigator.of(context).pushNamed("/");*/
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
        SizedBox(
            width: 300,
            child: Column(children: [
              TextField(controller: nameController),
              TextField(
                  controller: passwordController,
                  obscureText: true,
                  enableSuggestions: false,
                  autocorrect: false),
              Padding(
                  padding: const EdgeInsets.only(top: 15),
                  child: ElevatedButton(
                      onPressed:
                          _loginInProgress ? null : () => doLogin(context),
                      child: const Text("Login")))
            ]))
      ],
    ));
  }
}
