import 'package:audioplayers/audioplayers.dart' as ap;
//import 'package:just_audio/just_audio.dart' as ja;

import 'package:flutter/material.dart';
import 'package:vffapp/components/AudioButton.dart';
import 'package:audio_video_progress_bar/audio_video_progress_bar.dart';

class AudioPlayer extends StatefulWidget {
  final String url;
  final Duration duration;

  const AudioPlayer({super.key, required this.url, required this.duration});

  @override
  State<AudioPlayer> createState() => _AudioPlayerState();
}

class _AudioPlayerState extends State<AudioPlayer> {
  final _player = ap.AudioPlayer();
  bool _isRunning = false;
  Duration _position = Duration.zero;

  @override
  void initState() {
    super.initState();

    _player.onPositionChanged.listen((position) {
      setState(() {
        _position = position;
      });
    });

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
    await _player.resume();
  }

  Future<void> pause() async {
    setState(() {
      _isRunning = false;
    });
    await _player.pause();
  }

  Future<void> onSeek(Duration position) async {
    if (!_isRunning) {
      // There is a strange behavior when
      // stream is completed then seek does not work
      // anymore (at least for web version)
      // It seems that in "pause" mode, it works
      await _player.pause();
    }
    await _player.seek(position);
  }

  @override
  Widget build(BuildContext context) {
    var icon = _isRunning ? Icons.pause : Icons.play_arrow;
    var onTap = _isRunning ? pause : play;
    var duration = widget.duration;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        AudioButton(icon: icon, onTap: onTap),
        const SizedBox(width: 30),
        SizedBox(
            width: 200,
            height: 20,
            child: ProgressBar(
                progress: _position, total: duration, onSeek: onSeek))
      ],
    );
  }
}
