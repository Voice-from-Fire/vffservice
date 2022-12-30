import 'package:audioplayers/audioplayers.dart' as ap;
import 'package:flutter/material.dart';
import 'package:vffapp/components/AudioButton.dart';

class AudioPlayer extends StatefulWidget {
  final String url;

  const AudioPlayer({super.key, required this.url});

  @override
  State<AudioPlayer> createState() => _AudioPlayerState();
}

class _AudioPlayerState extends State<AudioPlayer> {
  final _player = ap.AudioPlayer();
  bool _isRunning = false;

  @override
  void initState() {
    super.initState();
    _player.setSourceUrl(widget.url);
    _player.onPlayerComplete.listen((event) {
      setState(() {
        _isRunning = false;
      });
    });
  }

  @override
  void dispose() {
    super.dispose();
    _player.dispose();
  }

  Future<void> play() async {
    setState(() {
      _isRunning = true;
    });
    await _player.resume();
  }

  Future<void> pause() async {
    setState(() {
      _isRunning = false;
    });
    await _player.pause();
  }

  @override
  Widget build(BuildContext context) {
    var icon = _isRunning ? Icons.pause : Icons.play_arrow;
    var onTap = _isRunning ? pause : play;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        AudioButton(icon: icon, onTap: play),
      ],
    );
  }
}
