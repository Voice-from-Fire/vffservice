import 'package:audioplayers/audioplayers.dart' as ap;
//import 'package:just_audio/just_audio.dart' as ja;

import 'package:flutter/material.dart';
import 'package:vffapp/components/AudioButton.dart';
import 'package:audio_video_progress_bar/audio_video_progress_bar.dart';

class AudioPlayer extends StatefulWidget {
  final String url;
  final Duration? duration;

  AudioPlayer({super.key, required this.url, required this.duration});

  @override
  State<AudioPlayer> createState() => _AudioPlayerState();
}

class _AudioPlayerState extends State<AudioPlayer> {
  final _player = ap.AudioPlayer();
  bool _isRunning = false;
  Duration? duration;

  @override
  void initState() {
    super.initState();

    _player.onPlayerComplete.listen((event) async {
      setState(() {
        _isRunning = false;
      });
    });
    _player.setSourceUrl(widget.url).then((_) => {
          /*_player.getDuration().then((value) => setState(() {
                print("!!!");
                print(value);
                duration = value;
              }))*/
        });
    _player.onDurationChanged.listen((value) => {print("DURATION ${value}")});

    // _player.setUrl(widget.url);
    // _player.durationFuture?.then((value) => print("D ${value}"));
    // _player.durationStream.listen((value) => print("DD ${value}"));
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
    //await _player.play();
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
    var duration = this.duration ?? Duration.zero;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        AudioButton(icon: icon, onTap: play),
        const SizedBox(width: 30),
        SizedBox(
            width: 200,
            height: 20,
            child: ProgressBar(progress: Duration.zero, total: duration))
      ],
    );
  }
}
