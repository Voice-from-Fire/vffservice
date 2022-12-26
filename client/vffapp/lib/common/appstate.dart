import 'package:flutter/material.dart';

class AppState with ChangeNotifier {
  String? _accessToken = null;
  String? _userName = null;

  bool isLogged() => _accessToken != null;
  String? userName() => _userName;

  void login(String userName, String token) {
    _userName = userName;
    _accessToken = token;
    notifyListeners();
  }

  void logout() {
    _userName = null;
    _accessToken = null;
    notifyListeners();
  }
}
