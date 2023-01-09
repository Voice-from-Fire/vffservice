import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:vffapp/components/AudioButton.dart';

class AudioRecorder extends StatefulWidget {
  final void Function(String path, Duration duration) onStop;

  const AudioRecorder({Key? key, required this.onStop}) : super(key: key);

  @override
  State<AudioRecorder> createState() => _AudioRecorderState();
}

class _AudioRecorderState extends State<AudioRecorder> {
  Timer? _timer;
  final Record _audioRecorder = Record();
  StreamSubscription<RecordState>? _recordSub;
  StreamSubscription<Amplitude>? _amplitudeSub;
  Amplitude? _amplitude;
  bool _initing = false;
  bool _recording = false;
  Duration _elapsed = Duration.zero;
  final Stopwatch _stopwatch = Stopwatch();

  @override
  void initState() {
    /*_recordSub = _audioRecorder.onStateChanged().listen((recordState) {
      setState(() => _recordState = recordState);
    });*/

    _amplitudeSub = _audioRecorder
        .onAmplitudeChanged(const Duration(milliseconds: 300))
        .listen((amp) => setState(() => _amplitude = amp));

    super.initState();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _recordSub?.cancel();
    _amplitudeSub?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _start() async {
    try {
      setState(() => _initing = true);
      if (await _audioRecorder.hasPermission()) {
        // We don't do anything with this but printing
        final isSupported = await _audioRecorder.isEncoderSupported(
          AudioEncoder.aacLc,
        );
        if (kDebugMode) {
          print('${AudioEncoder.aacLc.name} supported: $isSupported');
        }

        // final devs = await _audioRecorder.listInputDevices();
        // final isRecording = await _audioRecorder.isRecording();

        await _audioRecorder.start();
        setState(() {
          _initing = false;
          _recording = true;
        });
        _startTimer();
      }
    } catch (e) {
      print(e);
      if (kDebugMode) {
        print(e);
      }
    }
  }

  Future<void> _stop() async {
    _timer?.cancel();

    final path = await _audioRecorder.stop();
    _stopwatch.stop();

    if (path != null) {
      widget.onStop(path, _stopwatch.elapsed);
    }
  }

  Future<void> _pause() async {
    _timer?.cancel();
    await _audioRecorder.pause();
  }

  Future<void> _resume() async {
    _startTimer();
    await _audioRecorder.resume();
  }

  @override
  Widget build(BuildContext context) {
    var button = !_recording
        ? AudioButton(icon: Icons.mic, onTap: _start)
        : AudioButton(icon: Icons.pause, onTap: _stop);
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        Column(children: [
          button,
          const SizedBox(height: 20),
          _buildText(),
        ])
      ],
    );
    /*if (_amplitude != null) ...[
              const SizedBox(height: 40),
              Text('Current: ${_amplitude?.current ?? 0.0}'),
              Text('Max: ${_amplitude?.max ?? 0.0}'),
            ],*/
  }

  Widget _buildText() {
    if (_initing) {
      return const Text("Initing ...");
    }
    if (_recording) {
      var ms = _elapsed.inMilliseconds;
      return Text("Recording ... ${ms ~/ 1000}.${(ms ~/ 100) % 10}s");
    }

    return const Text("Ready to record");
  }

  String _formatNumber(int number) {
    String numberStr = number.toString();
    if (number < 10) {
      numberStr = '0$numberStr';
    }

    return numberStr;
  }

  void _startTimer() {
    _stopwatch.start();
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(milliseconds: 200), (Timer t) {
      setState(() => _elapsed = _stopwatch.elapsed);
    });
  }
}
